# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyalePostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class BattleRoyalePostmortemPanelMeta(PostmortemPanel):

    def as_setPostmortemPanelCanBeVisibleS(self, value):
        return self.flashObject.as_setPostmortemPanelCanBeVisible(value) if self._isDAAPIInited() else None
