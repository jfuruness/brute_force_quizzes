#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This package contains functions used across classes"""

__authors__ = ["Justin Furuness"]
__credits__ = ["Justin Furuness"]
__Lisence__ = "BSD"
__maintainer__ = "Justin Furuness"
__email__ = "jfuruness@gmail.com"
__status__ = "Development"


from datetime import datetime, timedelta
import functools
import logging
import os
from subprocess import check_call, check_output, DEVNULL

import shutil

# This decorator deletes paths before and after func is called
def delete_files(files=[]):
    """This decorator deletes files before and after a function.
    This is very useful for installation procedures.
    """
    def my_decorator(func):
        @functools.wraps(func)
        def function_that_runs_func(self, *args, **kwargs):
            # Inside the decorator
            # Delete the files - prob don't exist yet
            delete_paths(files)
            # Run the function
            stuff = func(self, *args, **kwargs)
            # Delete the files if they do exist
            delete_paths(files)
            return stuff
        return function_that_runs_func
    return my_decorator


def delete_paths(paths):
    """Removes directory if directory, or removes path if path"""

    if not paths:
        paths = []
    # If a single path is passed in, convert it to a list
    if not isinstance(paths, list):
        paths = [paths]
    for path in paths:
        try:
            remove_func = os.remove if os.path.isfile(path) else shutil.rmtree
            remove_func(path)
            # If the path is a file
            if os.path.isfile(path):
                # Delete the file
                os.remove(path)
            # If the path is a directory
            if os.path.isdir(path):
                # rm -rf the directory
                shutil.rmtree(path)
        # Just in case we always delete everything at the end of a run
        # So some files may not exist anymore
        except AttributeError:
            logging.debug(f"Attribute error when deleting {path}")
        except FileNotFoundError:
            logging.debug(f"File not found when deleting {path}")
        except PermissionError:
            logging.warning(f"Permission error when deleting {path}")

def now():
    return datetime.now()

def run_cmds(cmds):

    cmd = " && ".join(cmds) if isinstance(cmds, list) else cmds

    # If less than logging.info
    if logging.root.level < 20:
        logging.debug(f"Running: {cmd}")
        check_call(cmd, shell=True)
    else:
        logging.debug(f"Running: {cmd}")
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)


def apt_installed(app: str) -> bool:
    """Checks if an apt package was installed, returns bool"""

    return app in check_output("apt list --installed",
                               stderr=DEVNULL,
                               shell=True).decode('utf-8')
def _get_env_var(var_name):
    """Returns API key"""

    key = os.environ.get(var_name)
    assert key is not None, ("\n" * 20 + "Must save api key with:\n"
                             f"export {var_name}=<my_thing>\n"
                             "See installation instructions "
                             "if unclear\n")
    return key
