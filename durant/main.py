"""Durant. Simple git deployment tool.

Usage:
durant.py [OPTIONS] deploy <stage>

Options:
-n, --dry-run   Perform a trial run, without actually deploying
-v, --version   Show version number
-h, --help      Show this screen
"""


import sys
from durant.deployer import Deployer

def usage():
    print __doc__

def main():
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
                d = Deployer()
               
                try:
                    print 'Checking environment...',

                    d.check_environment()

                    print 'DONE'

                    print 'Checking config file...',

                    d.check_config()

                    print 'DONE'

                    d.deploy(stage, dry_run)
                except Exception, e:
                    print '\nERR: ' + str(e)
                    sys.exit(1)
        else:
            usage()
            sys.exit(1)

if __name__ == "__main__":
    main()

