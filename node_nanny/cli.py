"""Command line argument parser for node usage monitor"""

from argparse import ArgumentParser
import sys
from app import MonitorUtility

class CLIParser(ArgumentParser):

    def __init__(self):
        """Define arguments for the command line interface"""
        super(CLIParser, self).__init__()
        self.add_argument('-v', '--version', action='version', version=self.app_version)

        ## Command argument
        functions = ['scan','kill','whitelist','add','remove']
        self.add_argument('command', choices = functions)

        # Subcommand arguments

        ## scan
        self.add_argument('-M', '--max-mem', )
        self.add_argument('-m', '--min-mem', )
        self.add_argument('-w', '--wait', )

        ## kill

        ## whitelist

        ## add

        ## remove

def error(self, message, print_help=True):
    """Print the error message to STDOUT and exit

    Args:
        message: The error message
        print_help: If ``True`` and no arguments were passed, print the help text.
    """

    if print_help and len(sys.argv) == 1:
        self.print_help()
        return

def execute(self):
    """Parse command line arguments and execute usage monitor"""

    try:
        args = self.parse_args()
        function = args.pop('command', self.print_help)

        util = MonitorUtility()
        util.function(**args)

    except KeyboardInterrupt:
        exit('Keyboard interrupt detected! exiting...')
