import os
import subprocess

from durant.cli import console
from durant.commands import Command

from durant.exceptions import DependencyError
from durant.exceptions import ConfigError
from durant.exceptions import DeployError


class Deploy(Command):
    default_excludes = ['.git', '.gitignore', '.gitmodules', '.gitkeep']
    
    commands = ['git', 'rsync']
    binaries = {}

    def check_environment(self):
        # checking and configuring the needed commands
        for command in self.commands:
            try:
                self.binaries[command] = subprocess.check_output([
                    'which', command
                ]).strip()
            except subprocess.CalledProcessError:
                console.fail()
                raise DependencyError(
                    '%s not available. Please install it and retry.' % command)

    def before_run(self):
        console.log('Checking environment...', end='')
        self.check_environment()
        console.done()

    def run(self, stage, dry_run=False):
        console.log('Preparing for deploy...', end='')

        if not self.config.has_stage(stage):
            console.fail()
            raise ConfigError("Config section for '%s' stage not found" %
                              stage)

        console.done()

        console.log('Cloning repository on local machine...')

        servers = self.config.get(stage, 'server', many=True)
        before_deploy = self.config.get(stage, 'before_deploy',
                                              many=True)

        temp_dir = self.config.get(stage, 'temp_dir')
        repository = self.config.get(stage, 'repository')
        remote = self.config.get(stage, 'remote', fallback='origin')
        branch = self.config.get(stage, 'branch', fallback='master')
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
                    console.log('Repository already cloned, updating instead...')
                else:
                    console.fail()
                    raise DeployError('Temp directory is not empty and the existing repository '\
                        'differs from the target repository')
            else:
                console.fail()
                raise DeployError('Temp directory is not empty, cannot clone')

        command_clone = '%s clone --depth 1 --origin %s --branch %s %s %s' % (
            self.binaries['git'], remote, branch, repository, temp_dir
        )
        command_pull = '%s pull %s %s' % (self.binaries['git'], remote, branch)

        console.nl()  # new line

        try:
            command_checkout = command_clone
            if already_cloned:
                command_checkout = command_pull

            os.chdir(temp_dir)
            subprocess.check_call(command_checkout.split())
        except subprocess.CalledProcessError as e:
            console.fail()
            raise DeployError(("Cloning "
                               if not already_cloned else "Updating ") +
                              "repository '%s' failed" % repository)

        if before_deploy:
            os.chdir(temp_dir)
            for before_cmd in before_deploy:
                console.nl()  # new line
                console.log("Running '" + before_cmd + "'...")
                console.nl()  # new line
                try:
                    subprocess.check_call(before_cmd.split())
                except subprocess.CalledProcessError as e:
                    console.nl()
                    raise DeployError(
                        'Received return code %s. Cannot continue.' %
                        e.returncode)

        console.nl()  # new line

        console.log("Deploying '%s' (%s branch)..." % (repository, branch))

        for server in servers:
            console.log("Server '%s' (%s)..." % (server, project_dir))

            excludes = self.config.get(stage, 'exclude', many=True)

            command_rsync_exclude = []
            for exclude in set(self.default_excludes).union(excludes):
                command_rsync_exclude.append('--exclude')
                command_rsync_exclude.append(exclude)

            if temp_dir[-1] != os.sep:
                temp_dir += os.sep

            server_user = self.config.get(stage, 'user')
            ssh_port = self.config.get(stage, 'ssh_port')
            ssh_identity = self.config.get(stage, 'ssh_identity')

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
            
            console.log('Sending files...')
            console.nl()  # new line

            try:
                subprocess.check_call(command_rsync)
            except subprocess.CalledProcessError as e:
                console.nl()
                raise DeployError('Received return code %s' % e.returncode)

        return True       