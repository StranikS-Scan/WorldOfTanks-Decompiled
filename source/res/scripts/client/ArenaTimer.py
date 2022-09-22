# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaTimer.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers.CallbackDelayer import CallbackDelayer
_PERIOD = 0.1

class ArenaTimer(DynamicScriptComponent):

    def __init__(self):
        super(ArenaTimer, self).__init__()
        self.__cd = CallbackDelayer()
        self.__cd.delayCallback(_PERIOD, self.__tick)
        self.__previousRemainingTime = 0

    def onDestroy(self):
        super(ArenaTimer, self).onDestroy()
        self.__cd.destroy()
        self.__cd = None
        ctrl = self.entity.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onArenaTimer(self.keyName, self.left, 0)
        return

    def __tick(self):
        remainingTime = max(0, self.endTime - BigWorld.serverTime())
        if remainingTime == self.__previousRemainingTime:
            return _PERIOD
        else:
            ctrl = self.entity.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onArenaTimer(self.keyName, self.left, max(0, remainingTime))
            self.__previousRemainingTime = remainingTime
            return _PERIOD
