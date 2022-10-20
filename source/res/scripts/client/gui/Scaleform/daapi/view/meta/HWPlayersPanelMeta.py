# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HWPlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class HWPlayersPanelMeta(PlayersPanel):

    def as_setPlayerBuffS(self, isAlly, index, image):
        return self.flashObject.as_setPlayerBuff(isAlly, index, image) if self._isDAAPIInited() else None
