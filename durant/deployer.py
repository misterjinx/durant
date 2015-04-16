from __future__ import print_function

import os
import sys
import time
import subprocess

from durant.cli import output
from durant.colors import colors

from durant.exceptions import DependencyError
from durant.exceptions import ConfigError
from durant.exceptions import DeployError

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class Deployer(object):
    config_file = 'durant.conf'
    config_path = None
    config = None

    project_path = None

    default_excludes = ['.git', '.gitignore', '.gitmodules', '.gitkeep']
    
    commands = ['git', 'rsync']
    binaries = {}

    def __init__(self):
        self.project_path = os.getcwd()
        self.config_path = os.path.realpath(
            os.path.join(self.project_path, self.config_file))

    def check_environment(self):
        # checking and configuring the needed commands
        for command in self.commands:
            try:
                self.binaries[command] = subprocess.check_output([
                    'which', command
                ]).strip()
            except subprocess.CalledProcessError:
                raise DependencyError(
                    '%s not available. Please install it and retry.' % command)

        return True

    def check_config(self):
        if not os.path.exists(self.config_file):
            raise ConfigError('Config file not found')

        try:
            self.config = configparser.ConfigParser()
            self.config.read_file(open(self.config_path))
        except:
            self.config = configparser.SafeConfigParser()
            self.config.readfp(open(self.config_path))

        return True

    def deploy(self, stage, dry_run=False):
        self.print('Checking environment...', end='')
        self.check_environment()
        self.print_done()

        self.print('Checking config file...', end='')
        self.check_config()
        self.print_done()

        self.print('Preparing for deploy...', end='')

        if not self.config.has_section(stage):
            self.print_fail()
            raise ConfigError("Config section for '%s' stage not found" %
                              stage)

        self.print_done()

        self.print('Cloning repository on local machine...')

        servers = self.get_config_value(stage, 'server', many=True)
        before_deploy = self.get_config_value(stage, 'before_deploy',
                                              many=True)

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
                    [self.binaries['git'], 'config', '--get',
                     'remote.origin.url']).strip()
                if remote_origin_url == repository:
                    already_cloned = True
                    self.print('Repository already cloned, updating instead...')
                else:
                    self.print_fail()
                    raise DeployError('Temp directory is not empty and the existing repository '\
                        'differs from the target repository')
            else:
                self.print_fail()
                raise DeployError('Temp directory is not empty, cannot clone')

        command_clone = '%s clone --depth 1 --branch %s %s %s' % (
            self.binaries['git'], branch, repository, temp_dir
        )
        command_pull = '%s pull origin %s' % (self.binaries['git'], branch)

        self.print_nl()  # new line

        try:
            command_checkout = command_clone
            if already_cloned:
                command_checkout = command_pull

            os.chdir(temp_dir)
            subprocess.check_call(command_checkout.split())
        except subprocess.CalledProcessError as e:
            self.print_fail()
            raise DeployError(("Cloning "
                               if not already_cloned else "Updating ") +
                              "repository '%s' failed" % repository)

        if before_deploy:
            os.chdir(temp_dir)
            for before_cmd in before_deploy:
                self.print_nl()  # new line
                self.print("Running '" + before_cmd + "'...")
                self.print_nl()  # new line
                try:
                    subprocess.check_call(before_cmd.split())
                except subprocess.CalledProcessError as e:
                    self.print_nl()
                    raise DeployError(
                        'Received return code %s. Cannot continue.' %
                        e.returncode)

        self.print_nl()  # new line

        self.print("Deploying '%s' (%s branch)..." % (repository, branch))

        for server in servers:
            self.print("Server '%s' (%s)..." % (server, project_dir))

            excludes = self.get_config_value(stage, 'exclude', many=True)

            command_rsync_exclude = []
            for exclude in set(self.default_excludes).union(excludes):
                command_rsync_exclude.append('--exclude')
                command_rsync_exclude.append(exclude)

            if temp_dir[-1] != os.sep:
                temp_dir += os.sep

            server_user = self.get_config_value(stage, 'user')
            ssh_port = self.get_config_value(stage, 'ssh_port')
            ssh_identity = self.get_config_value(stage, 'ssh_identity')

            if not server_user:
                raise DeployError("Server user not specified")

            command_rsync_ssh_part = 'ssh'
            if ssh_port:
                command_rsync_ssh_part += ' -p ' + ssh_port
            if ssh_identity:
                key_path = os.path.expanduser(os.path.expandvars(ssh_identity))
                if not os.path.exists(key_path):
                    raise DeployError("SSH identity key '%s' does not exists" %
                                      ssh_identity)
                command_rsync_ssh_part += ' -i ' + ssh_identity

            command_rsync_server_part = '%s@%s:%s' % (server_user, server,
                                                      project_dir)

            if server in ['127.0.0.1', 'local', 'localhost']:
                command_rsync_server_part = project_dir
                command_rsync_ssh_part = 'ssh'

            command_rsync = []
            command_rsync.append(self.binaries['rsync'])
            command_rsync.append('-avzuh')
            command_rsync.append('--itemize-changes')
            if dry_run:
                command_rsync.append('--dry-run')
            command_rsync.extend(command_rsync_exclude)
            command_rsync.append('-e')
            command_rsync.append(command_rsync_ssh_part)
            command_rsync.append(temp_dir)
            command_rsync.append(command_rsync_server_part)
            
            self.print('Sending files...')
            self.print_nl()  # new line

            try:
                subprocess.check_call(command_rsync)
            except subprocess.CalledProcessError as e:
                self.print_nl()
                raise DeployError('Received return code %s' % e.returncode)

        return True

    def get_config_value(self, section, key, many=False, fallback=None):
        try:
            raw_value = self.config.get(section, key)
        except configparser.NoOptionError:
            raw_value = fallback

        if raw_value and many:
            value = raw_value.splitlines(
            ) if '\n' in raw_value else raw_value.split(',')
            return filter(None, map(str.strip, value))

        return raw_value

    def print(self, text, color=None, prefix=True, end='\n'):
        if prefix:
            date = output('[' + time.strftime('%X') + '] ',
                          color=colors.YELLOW)
            text = date + text
        print(output(text, color), end=end)

    def print_done(self, text='DONE', end='\n'):
        return self.print(text, color=colors.GREEN, prefix=False, end=end)

    def print_fail(self, text='FAIL', end='\n'):
        return self.print(text, color=colors.RED, prefix=False, end=end)

    def print_error(self, text, prefix='ERROR: ', end='\n'):
        err = output(prefix, color=colors.RED)
        return self.print(err + text)

    def print_nl(self):
        return self.print('', prefix=False)
