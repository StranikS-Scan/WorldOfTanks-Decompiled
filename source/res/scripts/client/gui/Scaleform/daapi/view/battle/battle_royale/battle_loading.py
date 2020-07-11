# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/battle_loading.py
from gui.Scaleform.daapi.view.meta.BattleRoyaleLoadingMeta import BattleRoyaleLoadingMeta
from gui.impl.gen.resources import R
from gui.impl import backport

class BattleLoading(BattleRoyaleLoadingMeta):

    def _populate(self):
        super(BattleLoading, self)._populate()
        arenaDP = self.sessionProvider.getArenaDP()
        self.as_setHeaderDataS({'title': backport.text(R.strings.battle_royale.fullStats.title()),
         'subTitle': backport.text(R.strings.battle_royale.fullStats.subTitle()),
         'battleType': arenaDP.getPersonalDescription().getFrameLabel(),
         'description': backport.text(R.strings.battle_royale.fullStats.description())})

    def _formatTipTitle(self, tipTitleText):
        return tipTitleText

    def _formatTipBody(self, tipBody):
        return tipBody
