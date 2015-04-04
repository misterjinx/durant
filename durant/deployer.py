import os
import sys
import time
import subprocess
from ConfigParser import SafeConfigParser

from exceptions import DependencyError
from exceptions import ConfigError
from exceptions import DeployError


class Deployer(object):    
    config_file = 'durant.conf'
    config_path = None
    config = None

    project_path = None

    commands = ['git', 'rsync']
    binaries = {}

    def __init__(self):
        self.project_path = os.getcwd()
        self.config_path = os.path.realpath(
            os.path.join(self.project_path, self.config_file)
        )
        
    def check_environment(self):
        # checking and configuring the needed commands
        for command in self.commands:
            try:
                self.binaries[command] = subprocess.check_output(
                    ['which', command]
                ).strip()
            except subprocess.CalledProcessError:
                raise DependencyError(
                    '%s not available. Please install it and retry.' % command
                )                

        return True
    
    def check_config(self):
        if not os.path.exists(self.config_file):
            raise ConfigError('Config file not found')            

        self.config = SafeConfigParser()
        self.config.readfp(open(self.config_path))

        return True

    def deploy(self, stage, dry_run=False):
        if not self.config.has_section(stage):
            raise ConfigError(
                'Config section for "%s" stage not found' % stage
            )
        
        start = time.time()

        servers = self.get_config_value(stage, 'server')
        before_deploy = self.get_config_value(stage, 'before_deploy')
        
        print 'Preparing for deploy...'
        
        print 'Cloning repository on local machine...'

        temp_dir = self.config.get(stage, 'temp_dir')
        repository = self.config.get(stage, 'repository')
        branch = self.config.get(stage, 'branch')
        project_dir = self.config.get(stage, 'project_dir')

        already_cloned = False
        # check if the temp directory is empty
        if os.listdir(temp_dir):
            # seems that there are files inside the directory
            # check if there is already the same repo cloned
            if os.path.exists(temp_dir + '/.git'):
                os.chdir(temp_dir)
                remote_origin_url = subprocess.check_output(
                    [self.binaries['git'], 'config', '--get', 'remote.origin.url']
                ).strip() == repository
                if remote_origin_url == repository:
                    already_cloned = True
                    print 'Repository already cloned, updating instead...'    
                else:    
                    raise DeployError(
                        'Temp directory is not empty and the existing repository differs from the target repository'
                    )            
            else:
                raise DeployError(
                    'Temp directory is not empty, cannot clone'
                )                

        command_clone = '%s clone --depth 1 --branch %s %s %s' % (
            self.binaries['git'], branch, repository, temp_dir
        )
        command_pull = '%s pull origin %s' % (
            self.binaries['git'], branch
        )

        try:
            command_checkout = command_clone
            if already_cloned:
                command_checkout = command_pull

            os.chdir(temp_dir)
            subprocess.check_call(command_checkout.split())
        except subprocess.CalledProcessError as err:
            raise DeployError(
                "Cloning" if not already_cloned else "Updating" + " repository '%s' failed" % repository
            ) 
        
        if before_deploy:
            os.chdir(temp_dir)
            for before_cmd in before_deploy:                                                                
                print '\nRunning ' + before_cmd
                try:
                    subprocess.check_call(before_cmd.split())
                except subprocess.CalledProcessError as err:
                    raise DeployError(
                        'Received return code %s. Cannot continue.' % err.returncode
                    )                                        

        for server in servers:
            print "Deploying '%s' (%s branch) repository to %s (%s)..." % (
                repository, branch, server, project_dir
            )                        

            excludes = self.get_config_value(stage, 'exclude')
        
            command_rsync_exclude = ''
            for exclude in excludes:
                command_rsync_exclude += ' --exclude ' + exclude

            if temp_dir[-1] != os.sep:
                temp_dir += os.sep

            server_user = self.config.get(stage, 'user')

            command_rsync_server_part = '%s@%s:%s' % (
                server_user, server, project_dir
            )
            if server in ['127.0.0.1', 'local', 'localhost']:
                command_rsync_server_part = project_dir

            command_rsync = '%s -avzuh %s -e ssh %s %s %s' % (
                self.binaries['rsync'],
                '--dry-run' if dry_run else '',
                command_rsync_exclude,
                temp_dir,
                command_rsync_server_part 
            )
            
            print 'Sending files...',
            
            try:
                subprocess.check_call(command_rsync.split())
            except subprocess.CalledProcessError as err:
                raise DeployError('Received return code %s' % err.returncode)                                
            
            print 'DONE'
        
        end = time.time()

        print 'Deployment complete (%.3f sec)' % (end - start)
    
    def get_config_value(self, section, key):
        raw_value = self.config.get(section, key)
        value = raw_value.splitlines() if '\n' in raw_value else raw_value.split(',')

        return filter(None, map(str.strip, value))

