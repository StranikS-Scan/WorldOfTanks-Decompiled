# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/CallbackHelpers.py
import BigWorld

def IgnoreCallbackIfDestroyed(function):

    def checkIfDestroyed(self, *args, **kwargs):
        return function(self, *args, **kwargs) if not self.isDestroyed else None

    return checkIfDestroyed
