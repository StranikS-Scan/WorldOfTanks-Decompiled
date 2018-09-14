# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCLobbyViewMeta.py
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView

class BCLobbyViewMeta(LobbyView):

    def startBattle(self):
        self._printOverrideError('startBattle')

    def onAnimationsComplete(self):
        self._printOverrideError('onAnimationsComplete')

    def as_setBootcampDataS(self, data):
        """
        :param data: Represented by BCLobbySettingsVO (AS)
        """
        return self.flashObject.as_setBootcampData(data) if self._isDAAPIInited() else None

    def as_showAnimatedS(self, data):
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None

    def as_setAppearConfigS(self, data):
        return self.flashObject.as_setAppearConfig(data) if self._isDAAPIInited() else None
