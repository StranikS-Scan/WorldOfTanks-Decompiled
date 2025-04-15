# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlinePlatoonPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel

class FrontlinePlatoonPanelMeta(PlayersPanel):

    def as_setPlatoonTitleS(self, title):
        return self.flashObject.as_setPlatoonTitle(title) if self._isDAAPIInited() else None

    def as_setMaxDisplayedInviteMessagesS(self, maxInvites):
        return self.flashObject.as_setMaxDisplayedInviteMessages(maxInvites) if self._isDAAPIInited() else None
