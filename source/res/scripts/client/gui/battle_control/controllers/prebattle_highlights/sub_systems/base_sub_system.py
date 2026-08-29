# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/sub_systems/base_sub_system.py
from __future__ import absolute_import

class BasePbhSubSystem(object):

    def __init__(self, readyCallback):
        self._readyCallback = readyCallback

    def subscribe(self):
        raise NotImplementedError

    def unsubscribe(self):
        raise NotImplementedError

    def isReady(self):
        raise NotImplementedError

    def startFlow(self):
        raise NotImplementedError

    def stopFlow(self):
        raise NotImplementedError

    def clear(self):
        self._readyCallback = None
        return
