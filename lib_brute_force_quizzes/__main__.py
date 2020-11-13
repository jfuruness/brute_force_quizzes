#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module runs all command line arguments."""

__authors__ = ["Justin Furuness"]
__credits__ = ["Justin Furuness"]
__Lisence__ = "BSD"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"

from argparse import ArgumentParser, Action
from logging import DEBUG
from sys import argv

from .brute_force_quizzes import Brute_Force_Quizzes
from .utils import config_logging


def main():
    """Does all the command line options available
    See top of file for in depth description"""

    parser = ArgumentParser(description="lib_brute_force_quizzes, see github")

    parser.add_argument("--brute_force_quizzes", dest="brute_force", default=False, action='store_true')
    parser.add_argument("--brute_force", dest="brute_force", default=False, action='store_true')
    parser.add_argument("--debug", dest="debug", default=False, action='store_true')
    parser.add_argument("--test", dest="test", default=False, action='store_true')
    parser.add_argument("--username", type=str, dest="username", default=None)
    parser.add_argument("--password", type=str, dest="password", default=None)
    parser.add_argument("--format", dest="format", default=False, action="store_true")




    args = parser.parse_args()
    if args.debug:
        config_logging(DEBUG)

    if args.brute_force:
        Brute_Force_Quizzes(args.username, args.password).run()
    if args.format:
        Brute_Force_Quizzes(args.username, args.password).format(from_main=True)

if __name__ == "__main__":
    main()
