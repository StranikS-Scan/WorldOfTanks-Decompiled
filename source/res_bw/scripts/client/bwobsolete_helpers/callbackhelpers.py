# Embedded file name: scripts/client/bwobsolete_helpers/CallbackHelpers.py
"""This module contains a number of helper functions intended simplify
implementing callback functions in a safe way.
"""
import BigWorld

def IgnoreCallbackIfDestroyed(function):

    def checkIfDestroyed(self, *args, **kwargs):
        if not isinstance(self, BigWorld.Entity):
            raise AssertionError
            return self.isDestroyed or function(self, *args, **kwargs)

    return checkIfDestroyed
