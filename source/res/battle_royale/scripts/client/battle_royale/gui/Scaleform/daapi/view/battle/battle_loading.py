# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/battle_loading.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.meta.BattleRoyaleLoadingMeta import BattleRoyaleLoadingMeta
from gui.impl import backport
from gui.impl.gen.resources import R
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleLoading(BattleRoyaleLoadingMeta):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def _populate(self):
        super(BattleLoading, self)._populate()
        arenaDP = self.sessionProvider.getArenaDP()
        self.as_setHeaderDataS({'battleType': arenaDP.getPersonalDescription().getFrameLabel(),
         'battleTypeIconPathBig': self._getBattleTypeIconPath('c_136x136'),
         'battleTypeIconPathSmall': self._getBattleTypeIconPath('c_64x64'),
         'title': backport.text(R.strings.battle_royale.fullStats.title()),
         'subTitle': backport.text(R.strings.battle_royale.fullStats.subTitle()),
         'description': backport.text(R.strings.battle_royale.fullStats.description())})

    def _formatTipTitle(self, tipTitleText):
        return tipTitleText

    def _formatTipBody(self, tipBody):
        return tipBody

    def _getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        arenaDP = self.sessionProvider.getArenaDP()
        if self.__battleRoyaleController.isStPatrick():
            resRoot = R.images.battle_royale.gui.maps.st_patrick.icons.battleTypes
        else:
            resRoot = R.images.gui.maps.icons.battleTypes
        iconRes = resRoot.dyn(sizeFolder).dyn(arenaDP.getPersonalDescription().getFrameLabel())
        return backport.image(iconRes()) if iconRes.exists() else ''

    def _makeVisualTipVO(self, arenaDP, tip=None):
        vo = {'tipIcon': self.gui.resourceManager.getImagePath(tip.icon) if tip is not None else None}
        return vo
