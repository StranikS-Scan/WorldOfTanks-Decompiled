# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_info_ctrl.py
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class ArenaInfoController(IArenaLoadController):
    __slots__ = ()

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_INFO_CTRL
