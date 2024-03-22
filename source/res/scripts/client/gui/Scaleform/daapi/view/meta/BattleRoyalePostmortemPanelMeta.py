# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyalePostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class BattleRoyalePostmortemPanelMeta(PostmortemPanel):

    def as_showDeadReasonS(self):
        return self.flashObject.as_showDeadReason() if self._isDAAPIInited() else None

    def as_setPlayerInfoS(self, playerInfo):
        return self.flashObject.as_setPlayerInfo(playerInfo) if self._isDAAPIInited() else None

    def as_setPostmortemPanelVisibleS(self, value):
        return self.flashObject.as_setPostmortemPanelVisible(value) if self._isDAAPIInited() else None
