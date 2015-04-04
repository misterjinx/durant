import sys
import durant

from durant.cli import output
from durant.cli import output_dots
from durant.colors import colors

def usage():
    print durant.__doc__

def version():
    print 'Version %s' % durant.__version__

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
            version()
            sys.exit(1)             
        elif 'deploy' in args:
            dry_run = True if '-n' in args or '--dry-run' in args else False
            
            try:                
                stage = args[args.index('deploy')+1]
            except IndexError:
                usage()
                sys.exit(1)
            else:
                d = durant.Deployer()
               
                try:
                    print output_dots('Checking environment', end="DONE"),

                    d.check_environment()

                    print output('DONE', colors.GREEN)

                    print output_dots('Checking config file', end="DONE"),

                    d.check_config()

                    print output('DONE', colors.GREEN)

                    d.deploy(stage, dry_run)
                except Exception, e:
                    print output('ERR: ', colors.RED) + str(e)
                    sys.exit(1)
        else:
            usage()
            sys.exit(1)

if __name__ == "__main__":
    main()

