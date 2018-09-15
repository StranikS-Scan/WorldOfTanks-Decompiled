# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/log/hooks.py
import logging
import traceback
import sys
import ResMgr

def formatException(excType, excValue, excTraceback):
    """This function is same as traceback.format_exception,
    but has on distinction - relative path of py files to absolute."""
    extracted = traceback.extract_tb(excTraceback)
    converted = []
    for filename, lineno, name, line in extracted:
        if filename.endswith('.py'):
            converted.append((ResMgr.resolveToAbsolutePath(filename),
             lineno,
             name,
             line))
        converted.append((filename,
         lineno,
         name,
         line))

    converted = traceback.format_list(converted)
    converted += traceback.format_exception(excType, excValue, None)
    return ''.join(converted)


def setupUserExceptionHook():
    """Replace standard exception hook to user-defined hook to
    log critical message via logging."""

    def exceptionHook(excType, excValue, excTraceback):
        logging.critical(formatException(excType, excValue, excTraceback))

    sys.excepthook = exceptionHook
