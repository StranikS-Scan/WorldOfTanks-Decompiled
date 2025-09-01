# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/battle_control/interfaces.py
from gui.battle_control.arena_info.interfaces import IArenaLoadController

class IComp7VOIPController(IArenaLoadController):
    __slots__ = ()

    @property
    def isVoipSupported(self):
        raise NotImplementedError

    @property
    def isVoipEnabled(self):
        raise NotImplementedError

    @property
    def isTeamChannelAvailable(self):
        raise NotImplementedError

    @property
    def isJoined(self):
        raise NotImplementedError

    @property
    def isTeamVoipEnabled(self):
        raise NotImplementedError

    def toggleChannelConnection(self):
        raise NotImplementedError
