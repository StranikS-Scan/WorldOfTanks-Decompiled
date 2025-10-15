# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/arena_info/portal_arena_descrs.py
import BattleReplay
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
from gui.impl import backport
from gui.impl.gen import R

class PortalArenaDescription(ArenaWithLabelDescription):

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying

    def getDescriptionString(self, isInBattle=True):
        return backport.text(R.strings.arenas.type.portal.description())

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.arenas.type.portal.winString())
