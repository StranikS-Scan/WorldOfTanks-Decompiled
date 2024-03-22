# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PvePlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class PvePlayersPanelMeta(PlayersPanel):

    def as_setCountLivesVisibilityS(self, value):
        return self.flashObject.as_setCountLivesVisibility(value) if self._isDAAPIInited() else None

    def as_setRightPanelVisibilityS(self, value):
        return self.flashObject.as_setRightPanelVisibility(value) if self._isDAAPIInited() else None
