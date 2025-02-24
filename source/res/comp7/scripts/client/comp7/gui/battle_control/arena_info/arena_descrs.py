# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/arena_info/arena_descrs.py
import BattleReplay
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
from gui.impl import backport
from gui.impl.gen import R

class Comp7BattlesDescription(ArenaWithLabelDescription):

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying

    def getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        iconRes = R.images.comp7.gui.maps.icons.battleTypes.dyn(sizeFolder).dyn(self.getFrameLabel())
        return backport.image(iconRes()) if iconRes.exists() else ''
