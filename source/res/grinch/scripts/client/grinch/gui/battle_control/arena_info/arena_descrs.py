# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/arena_info/arena_descrs.py
import BattleReplay
from grinch.skeletons.battle_controller import IGrinchController
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
from helpers import dependency

class GrinchArenaDescription(ArenaWithLabelDescription):
    _grinchController = dependency.descriptor(IGrinchController)

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying

    def getScreenIcon(self):
        return self._grinchController.prbHintManager.getHintImagePath()
