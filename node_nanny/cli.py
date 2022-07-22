"""Command line argument parser for node usage monitor"""

from argparse import ArgumentParser
from socket import gethostname
import sys

from node_nanny.app import MonitorUtility


class CLIParser(ArgumentParser):
    """Class for passing command line arguments to the MonitorUtility app"""

    def __init__(self, *args, **kwargs) -> None:
        """Define arguments for the command line interface"""

        super().__init__(**kwargs)

        if getattr(self, 'prog') in sys.argv[0]:
            self.setup_commands()

    def setup_commands(self):

        # Command subparser
        command = self.add_subparsers(
            dest='command',
            required=True,
            help='sub-command to run'
        )

        # Scan subcommand
        scan = command.add_parser(
            'scan',
            help='initiate a scan for memory intensive processes'
        )

        scan.add_argument(
            '-M',
            '--max-mem',
            action='store',
            type=int,
            required=False,
            default=20,
            help=('max limit on memory usage, '
                  'any process above this will be killed')
        )

        scan.add_argument(
            '-m',
            '--min-mem',
            action='store',
            type=int,
            required=False,
            default=5,
            help=('lower limit on memory usage, '
                  'processes under this amount will never be killed')
        )

        scan.add_argument(
            '-w',
            '--wait',
            action='store',
            type=int,
            required=False,
            default=5,
            help=('duration that a process found to be above '
                  'the memory limit is allowed to continue before '
                  'being killed')
        )

        # Kill subcommand
        kill = command.add_parser(
            'kill',
            help=('Kill all running processes attached to the '
                  'given username and notify the them via email')
        )

        kill.add_argument(
            '-u',
            '--user',
            action='store',
            type=str,
            required=True,
            help='username of the user whos jobs should be killed'
        )

        kill.add_argument(
            '-q',
            '--quiet',
            action='store',
            type=bool,
            required=False,
            help='suppress outgoing email notifications'
        )

        # Notification History subcommand
        history = command.add_parser(
            'history',
            help=('display a history of recently killed jobs '
                  'and corresponding email notifications')
        )

        history.add_argument(
            '-u',
            '--user',
            action='store',
            type=str,
            required=False,
            help='username of the notification history to show'
        )

        # Whitelist subcommand
        command.add_parser(
            'whitelist',
            help='display current whitelist, user and node names'
        )

        add = command.add_parser(
            'add',
            help=('whitelist the given user so their jobs are '
                  'never killed on the current node')
        )

        add.add_argument(
            '-u',
            '--user',
            action='store',
            type=str,
            required=True,
            help=('username of the user who should be added to '
                  'the whitelist')
        )

        add.add_argument(
            '-d',
            '--duration',
            action='store',
            type=int,
            required=False,
            default=100000000,
            help='how long to whitelist a user for'
        )

        whitelist_node_opts = add.add_mutually_exclusive_group()

        whitelist_node_opts.add_argument(
            '-n',
            '--node',
            action='store',
            type=str,
            required=False,
            default=gethostname(),
            help='node or list of nodes to whitelist the user on'
        )

        whitelist_node_opts.add_argument(
            '-g',
            '--global',
            action='store_true',
            help='whitelist user on all nodes'
        )

        # Remove from whitelist
        remove = command.add_parser(
            'remove',
            help='remove a user from the whitelist on the current node'
        )

        remove.add_argument(
            '-u',
            '--user',
            action='store',
            type=str,
            required=True,
            help=('username of the user who should be removed from '
                  'the whitelist')
        )

        node_opts = remove.add_mutually_exclusive_group()
        node_opts.add_argument(
            '-n',
            '--node',
            action='store',
            type=str,
            required=False,
            default=gethostname(),
            help='node or list of nodes to Un-whitelist the user on'
        )

        node_opts.add_argument(
            '-g',
            '--global',
            action='store_true',
            help='un-whitelist user on all nodes'
        )

    def error(self, message):
        """Print the error message to STDOUT and exit

        Args:
            message: The error message
        """

        # Print help when no arguments are provided
        if len(sys.argv) == 1:
            self.print_help()
            sys.exit()

        super().error(message)

    @classmethod
    def execute(cls):
        """Parse command line arguments and execute usage monitor"""

        app = cls()
        args = vars(app.parse_args())
        getattr(app, args.pop('command'))(**args)
