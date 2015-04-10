from __future__ import print_function

import sys
import time
import durant

from durant.cli import output
from durant.colors import colors

def usage():
    print(durant.__doc__)

def version():
    print('Version %s' % durant.__version__)

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
                start = time.time()

                d = durant.Deployer()
                
                d.print('Starting deployment\n', color=colors.YELLOW)

                try:
                    d.deploy(stage, dry_run)
                    
                    end = time.time()
                   
                    d.print_nl()
                    d.print('Deployment complete (%.3f seconds)' % (end - start), color=colors.YELLOW) 
                except Exception as e:
                    end = time.time()

                    d.print_error(str(e))
                    d.print_nl()
                    d.print('Deployment failed (%.3f seconds)' % (end - start), color=colors.YELLOW) 
                    sys.exit(1)
        else:
            usage()
            sys.exit(1)

if __name__ == "__main__":
    main()

