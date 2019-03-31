# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Helpers/CallbackHelpers.py
# Compiled at: 2010-05-25 20:46:16
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
