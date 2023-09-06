# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/animated_hints/manager.py
import BigWorld
from PlayerEvents import g_playerEvents
from animated_hints.custom import HintCustom
from animated_hints.system import HintSystem
from animated_hints.constants import EventAction
from animated_hints.events import HintActionEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
_g_hintManager = None

class HintManager(object):

    def __init__(self):
        self.__hintSystem = HintSystem()
        self.__updateId = None
        self.__hints = {}
        return

    @staticmethod
    def instance():
        global _g_hintManager
        if _g_hintManager is None:
            _g_hintManager = HintManager()
            _g_hintManager.__start()
        return _g_hintManager

    @property
    def hintSystem(self):
        return self.__hintSystem

    def __updateHintSystem(self):
        self.__hintSystem.update()
        self.__updateId = BigWorld.callback(0.2, self.__updateHintSystem)

    def __start(self):
        self.__hintSystem.start()
        self.__updateHintSystem()
        g_playerEvents.onAvatarBecomePlayer += self.__stop
        g_playerEvents.onAvatarBecomeNonPlayer += self.__stop

    def __stop(self):
        global _g_hintManager
        if self.__hintSystem is not None:
            self.__hintSystem.stop()
            if self.__updateId is not None:
                BigWorld.cancelCallback(self.__updateId)
                self.__updateId = None
            self.__hintSystem = None
        g_playerEvents.onAvatarBecomePlayer -= self.__stop
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__stop
        _g_hintManager = None
        return

    def getHint(self, hintId):
        return self.__hints.get(hintId)

    def getHints(self):
        return self.__hints

    def addHint(self, hintParams):
        hint = HintCustom(*hintParams)
        self.__hintSystem.addHint(hint)
        self.__hints[hint.id] = hint
        return hint

    def setPenetration(self, penetrationType, isColorBlind):
        g_eventBus.handleEvent(HintActionEvent(EventAction.SetPenetration, ctx={'penetrationType': penetrationType,
         'isColorBlind': isColorBlind}), scope=EVENT_BUS_SCOPE.BATTLE)
