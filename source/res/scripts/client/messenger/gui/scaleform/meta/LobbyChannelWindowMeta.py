# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/LobbyChannelWindowMeta.py
from messenger.gui.Scaleform.view.lobby.SimpleChannelWindow import SimpleChannelWindow

class LobbyChannelWindowMeta(SimpleChannelWindow):

    def onWarningClose(self):
        self._printOverrideError('onWarningClose')

    def as_getMembersDPS(self):
        return self.flashObject.as_getMembersDP() if self._isDAAPIInited() else None

    def as_hideMembersListS(self):
        return self.flashObject.as_hideMembersList() if self._isDAAPIInited() else None

    def as_showWarningS(self, warning):
        return self.flashObject.as_showWarning(warning) if self._isDAAPIInited() else None
