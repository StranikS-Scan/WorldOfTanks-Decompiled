# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/interfaces.py
from __future__ import absolute_import
from gui.battle_control.arena_info.interfaces import IArenaLoadController

class ILSVOIPController(IArenaLoadController):
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
