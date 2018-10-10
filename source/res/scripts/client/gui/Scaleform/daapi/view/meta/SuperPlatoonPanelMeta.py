# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SuperPlatoonPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class SuperPlatoonPanelMeta(PlayersPanel):

    def as_setPlatoonTitleS(self, title):
        return self.flashObject.as_setPlatoonTitle(title) if self._isDAAPIInited() else None
