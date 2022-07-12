#!/usr/bin/python -E
"""Executable for the Node Nanny argument parser and the corresponding app logic"""

from node_nanny.cli import CLIParser

if __name__ == '__main__':
    CLIParser().execute()
