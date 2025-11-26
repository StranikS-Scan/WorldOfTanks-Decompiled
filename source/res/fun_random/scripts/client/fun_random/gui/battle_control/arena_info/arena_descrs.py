# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_control/arena_info/arena_descrs.py
from __future__ import absolute_import
from gui.battle_control.arena_info.arena_descrs import ArenaDescriptionWithInvitation
from gui.impl import backport
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode

class FunRandomArenaDescription(ArenaDescriptionWithInvitation, FunAssetPacksMixin, FunSubModesWatcher):

    def getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        iconRes = self.getModeIconsResRoot().battleTypes.dyn(sizeFolder).dyn(self.getFrameLabel())
        return backport.image(iconRes()) if iconRes.exists() else ''

    def getDescriptionString(self, isInBattle=True):
        return self.__getDescriptionString() or self.getModeUserName()

    @hasBattleSubMode(defReturn='')
    def __getDescriptionString(self):
        subModeName = backport.text(self.getBattleSubMode(self._visitor).getLocalsResRoot().userName())
        return self.getModeDetailedUserName(subModeName=subModeName)
