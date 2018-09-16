# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tutorial_helper.py
from debug_utils import LOG_ERROR

def getTutorialGlobalStorage():
    try:
        from tutorial.control.context import GlobalStorage
    except ImportError:
        LOG_ERROR('Can not load package tutorial')
        GlobalStorage = None

    return GlobalStorage
