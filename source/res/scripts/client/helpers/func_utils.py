# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/func_utils.py
# Compiled at: 2009-09-29 15:37:47
import BigWorld
from functools import partial

def callback(delay, obj, methodName, *args):
    return BigWorld.callback(delay, partial(callMethod, obj, methodName, *args))


def callMethod(obj, methodName, *args):
    if hasattr(obj, methodName):
        getattr(obj, methodName)(*args)
