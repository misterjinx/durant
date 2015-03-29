"""Durant. Simple git deployment tool.

Usage:
durant.py [OPTIONS] deploy <stage>

Options:
-n, --dry-run   Perform a trial run, without actually deploying
-v, --version   Show version number
-h, --help      Show this screen
"""

import os
import sys
import time
import subprocess
from ConfigParser import SafeConfigParser

VERSION = 0.1

class Durant(object):    
    config_file = 'durant.conf'
    config_path = None
    config = None

    project_path = None

    commands = ['git', 'rsync']
    binaries = {}

    def __init__(self):
        self.project_path = os.getcwd()
        self.config_path = os.path.realpath(os.path.join(self.project_path, self.config_file))
        
    def check_environment(self):
        # checking and configuring the needed commands
        for command in self.commands:
            try:
                self.binaries[command] = subprocess.check_output(['which', command]).strip()
            except subprocess.CalledProcessError:
                print '\nERR: %s not available. Please install it and retry.' % command
                sys.exit(1)
    
    def check_config(self):
        if not os.path.exists(self.config_file):
            print '\nERR: Config file not found'
            sys.exit(1)
        else:
            self.config = SafeConfigParser()
            self.config.readfp(open(self.config_path))

    def deploy(self, stage, dry_run=False):
        if not self.config.has_section(stage):
            print '\nERR: Config section for "%s" stage not found' % stage
            sys.exit(1)
        else:
            start = time.time()

            servers_value = self.config.get(stage, 'server')
            servers = servers_value.splitlines() if '\n' in servers_value else servers_value.split(',')
            servers = filter(None, map(str.strip, servers))
            
            before_deploy_value = self.config.get(stage, 'before_deploy')
            before_deploy = before_deploy_value.splitlines() if '\n' in before_deploy_value else before_deploy_value.split(',')
            before_deploy = filter(None, map(str.strip, before_deploy))                         
            
            print 'Preparing for deploy...'
            
            print 'Cloning repository on local machine...'

            already_cloned = False
            # check if the temp directory is empty
            if os.listdir(self.config.get(stage, 'temp_dir')):
                # seems that there are files inside the directory
                # check if there is already the same repo cloned
                if os.path.exists(self.config.get(stage, 'temp_dir') + '/.git'):
                    os.chdir(self.config.get(stage, 'temp_dir'))
                    if subprocess.check_output([self.binaries['git'], 'config', '--get', 'remote.origin.url']).strip() == self.config.get(stage, 'repository'):
                        already_cloned = True
                        print 'Repository already cloned, updating instead...'    
                    else:    
                        print 'ERR: Temp directory is not empty and the existing repository differs from the target repository'
                        sys.exit(1)
                else:
                    print 'ERR: Temp directory is not empty, cannot clone'
                    sys.exit(1)

            command_clone = '%s clone --depth 1 --branch %s %s %s' % (
                self.binaries['git'],
                self.config.get(stage, 'branch'),
                self.config.get(stage, 'repository'),
                self.config.get(stage, 'temp_dir')
            )
            command_pull = '%s pull origin %s' % (
                self.binaries['git'],
                self.config.get(stage, 'branch')
            )

            try:
                if not already_cloned:
                    command_checkcout = command_clone
                else:
                    command_checkout = command_pull

                os.chdir(self.config.get(stage, 'temp_dir'))
                subprocess.check_call(command_checkout.split())
            except subprocess.CalledProcessError as err:
                print "\nERR: " + "Cloning" if not already_cloned else "Updating" + " repository '%s' failed" % self.config.get(stage, 'repository') 
                sys.exit(1)
            
            if before_deploy:
                os.chdir(self.config.get(stage, 'temp_dir'))
                for before_cmd in before_deploy:                                                                
                    print '\nRunning ' + before_cmd
                    try:
                        subprocess.check_call(before_cmd.split())
                    except subprocess.CalledProcessError as err:
                        print '\nERR: Received return code %s. Cannot continue.' % err.returncode
                        print '\nDeployment failed'
                        sys.exit(1)

            for server in servers:
                print "Deploying '%s' (%s branch) repository to %s (%s)..." % (
                    self.config.get(stage, 'repository'),
                    self.config.get(stage, 'branch'),
                    server,
                    self.config.get(stage, 'project_dir')
                )                        

                excludes_value = self.config.get(stage, 'exclude')
                excludes = excludes_value.splitlines() if '\n' in excludes_value else excludes_value.split(',')
                excludes = filter(None, map(str.strip, excludes))
            
                command_rsync_exclude = ''
                for exclude in excludes:
                    command_rsync_exclude += ' --exclude ' + exclude

                temp_dir = self.config.get(stage, 'temp_dir')
                if temp_dir[-1] != os.sep:
                    temp_dir += os.sep

                command_rsync_server_part = '%s@%s:%s' % (
                    self.config.get(stage, 'user'), 
                    server,
                    self.config.get(stage, 'project_dir')
                )
                if server in ['127.0.0.1', 'local', 'localhost']:
                    command_rsync_server_part = self.config.get(stage, 'project_dir')

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
                    print '\nERR: Received return code %s' % err.returncode
                    print '\nDeployment failed'
                    sys.exit(1)
                
                print 'DONE'
            
            end = time.time()

            print 'Deployment complete (%.3f sec)' % (end - start)


def usage():
    print __doc__

if __name__ == '__main__':
    try:
        sys.argv[1]
    except IndexError:
        usage()
        sys.exit(1)
    else:
        args = sys.argv[1:]
        if '-h' in args or '--help' in args:
            usage()
            sys.exit(1)
        elif '-v' in args or '--version' in args:
            print 'Version %s' % VERSION
            sys.exit(1)             
        elif 'deploy' in args:
            dry_run = True if '-n' in args or '--dry-run' in args else False
            
            try:                
                stage = args[args.index('deploy')+1]
            except IndexError:
                usage()
                sys.exit(1)
            else:
                d = Durant()
                
                print 'Checking environment...',

                d.check_environment()

                print 'DONE'

                print 'Checking config file...',

                d.check_config()

                print 'DONE'

                d.deploy(stage, dry_run)
        else:
            usage()
            sys.exit(1)
                
