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

def usage():
    print __doc__

if __name__ == '__main__':
    project_path = os.getcwd()
    conf_file = 'durant.conf'
    conf_path = os.path.realpath(os.path.join(project_path, conf_file))

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
                print 'Checking environment...',

                # checking and configuring the needed commands
                binaries = {}
                commands = ['git', 'rsync']
                for command in commands:
                    try:
                        binaries[command] = subprocess.check_output(['which', command]).strip()
                    except subprocess.CalledProcessError:
                        print '\nERR: %s not available. Please install it and retry.' % command
                        sys.exit(1)

                print 'DONE'

                print 'Checking config file...',

                if not os.path.exists(conf_file):
                    print '\nERR: Config file not found'
                    sys.exit(1)
                else:
                    config = SafeConfigParser()
                    config.readfp(open(conf_path))
                    if not config.has_section(stage):
                        print '\nERR: Config section for "%s" stage not found' % stage
                        sys.exit(1)
                    else:
                        print 'DONE'
                       
                        start = time.time()

                        servers_value = config.get(stage, 'server')
                        servers = servers_value.splitlines() if '\n' in servers_value else servers_value.split(',')
                        servers = filter(None, map(str.strip, servers))
                        
                        before_deploy_value = config.get(stage, 'before_deploy')
                        before_deploy = before_deploy_value.splitlines() if '\n' in before_deploy_value else before_deploy_value.split(',')
                        before_deploy = filter(None, map(str.strip, before_deploy))                         
                        
                        print 'Preparing for deploy...'
                        
                        print 'Cloning repository on local machine...'

                        already_cloned = False
                        # check if the temp directory is empty
                        if os.listdir(config.get(stage, 'temp-dir')):
                            # seems that there are files inside the directory
                            # check if there is already the same repo cloned
                            if os.path.exists(config.get(stage, 'temp-dir') + '/.git'):
                                os.chdir(config.get(stage, 'temp-dir'))
                                if subprocess.check_output([binaries['git'], 'config', '--get', 'remote.origin.url']).strip() == config.get(stage, 'repository'):
                                    already_cloned = True
                                    print 'Repository already cloned, updating instead...'    
                                else:    
                                    print 'ERR: Temp directory is not empty and the existing repository differs from the target repository'
                                    sys.exit(1)
                            else:
                                print 'ERR: Temp directory is not empty, cannot clone'
                                sys.exit(1)

                        command_clone = '%s clone --depth 1 --branch %s %s %s' % (
                            binaries['git'],
                            config.get(stage, 'branch'),
                            config.get(stage, 'repository'),
                            config.get(stage, 'temp-dir')
                        )
                        command_pull = '%s pull origin %s' % (
                            binaries['git'],
                            config.get(stage, 'branch')
                        )

                        try:
                            if not already_cloned:
                                command_checkcout = command_clone
                            else:
                                command_checkout = command_pull

                            os.chdir(config.get(stage, 'temp-dir'))
                            subprocess.check_call(command_checkout.split())
                        except subprocess.CalledProcessError as err:
                            print "\nERR: " + "Cloning" if not already_cloned else "Updating" + " repository '%s' failed" % config.get(stage, 'repository') 
                            sys.exit(1)
                        
                        if before_deploy:
                            os.chdir(config.get(stage, 'temp-dir'))
                            for before_cmd in before_deploy:                                                                
                                print '\nRunning ' + before_cmd
                                try:
                                    subprocess.check_call(before_cmd.split())
                                except subprocess.CalledProcessError as err:
                                    print '\nERR: Received return code %s. Cannot continue.' % err.returncode
                                    print '\nDeployment failed'
                                    sys.exit(1)

                        for server in servers:
                            print "Deploying '%s' (%s branch) repository to %s..." % (
                                config.get(stage, 'repository'),
                                config.get(stage, 'branch'),
                                server
                            )                        

                            excludes_value = config.get(stage, 'exclude')
                            excludes = excludes_value.splitlines() if '\n' in excludes_value else excludes_value.split(',')
                            excludes = filter(None, map(str.strip, excludes))
                        
                            command_rsync_exclude = ''
                            for exclude in excludes:
                                command_rsync_exclude += ' --exclude ' + exclude

                            temp_dir = config.get(stage, 'temp-dir')
                            if temp_dir[-1] != os.sep:
                                temp_dir += os.sep

                            command_rsync = '%s -avzuh %s -e ssh %s %s %s@%s:%s' % (
                                binaries['rsync'],
                                '--dry-run' if dry_run else '',
                                command_rsync_exclude,
                                temp_dir,
                                config.get(stage, 'user'), 
                                server,
                                config.get(stage, 'project-dir')
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

                        print 'Deployment complete (%.3f sec)' % (end-start)
        else:
            usage()
            sys.exit(1)
                
