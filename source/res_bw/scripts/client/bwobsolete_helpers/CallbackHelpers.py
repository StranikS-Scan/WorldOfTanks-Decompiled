# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/CallbackHelpers.py
"""This module contains a number of helper functions intended simplify
implementing callback functions in a safe way.
"""
import BigWorld

def IgnoreCallbackIfDestroyed(function):

    def checkIfDestroyed(self, *args, **kwargs):
        assert isinstance(self, BigWorld.Entity)
        if not self.isDestroyed:
            return function(self, *args, **kwargs)

    return checkIfDestroyed
