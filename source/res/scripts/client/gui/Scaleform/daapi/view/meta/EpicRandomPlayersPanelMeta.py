# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicRandomPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class EpicRandomPlayersPanelMeta(PlayersPanel):

    def focusedColumnChanged(self, value):
        self._printOverrideError('focusedColumnChanged')

    def as_setPlayersSwitchingAllowedS(self, isAllowed):
        return self.flashObject.as_setPlayersSwitchingAllowed(isAllowed) if self._isDAAPIInited() else None
