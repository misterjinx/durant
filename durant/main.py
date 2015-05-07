from __future__ import print_function

import sys
import time
import argparse
import durant

from durant.cli import output
from durant.cli import console


def version():
    return 'Version %s' % durant.__version__


def main():
    parser = argparse.ArgumentParser(description='Durant. Simple git deployment tool.',
        epilog="Use '%(prog)s <command> --help' to get detailed usage for that particular command")
    parser.add_argument('-v', '--version', action='version', version=version())

    subparsers = parser.add_subparsers(dest='command', title='available commands')

    deploy_parser = subparsers.add_parser('deploy', help='Deploy to specified stage')
    deploy_parser.add_argument('-n', '--dry-run', action='store_true', default=False,
        help='Perform a trial run, without actually deploying')
    deploy_parser.add_argument('stage', action='store',
        help='Stage to deploy to (a valid section name defined in the config file)')

    args = parser.parse_args()
    
    if args.command == 'deploy':
        console.log('Starting deployment\n')

        try:
            console.log('Checking config file...', end='')
            config = durant.Config()
            console.done()
        except Exception as e:
            console.fail()
            sys.exit(1)

        start = time.time()    

        try:            
            cmd = durant.commands.Deploy(config)        
            cmd.execute(stage=args.stage, dry_run=args.dry_run)

            deployed = True
        except Exception as e:
            console.error(str(e))
            deployed = False

        end = time.time()

        console.nl()
        console.log('Deployment %s (%.3f seconds)' %
            ('complete' if deployed else 'failed', (end - start)))

        if not deployed:
            sys.exit(1)


if __name__ == "__main__":
    main()
