# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RallyMainWindowWithSearchMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyMainWindow import BaseRallyMainWindow

class RallyMainWindowWithSearchMeta(BaseRallyMainWindow):

    def onAutoMatch(self, value, values):
        self._printOverrideError('onAutoMatch')

    def autoSearchApply(self, value):
        self._printOverrideError('autoSearchApply')

    def autoSearchCancel(self, value):
        self._printOverrideError('autoSearchCancel')

    def as_autoSearchEnableBtnS(self, value):
        return self.flashObject.as_autoSearchEnableBtn(value) if self._isDAAPIInited() else None

    def as_changeAutoSearchStateS(self, value):
        return self.flashObject.as_changeAutoSearchState(value) if self._isDAAPIInited() else None

    def as_changeAutoSearchBtnsStateS(self, waitingPlayers, searchEnemy):
        return self.flashObject.as_changeAutoSearchBtnsState(waitingPlayers, searchEnemy) if self._isDAAPIInited() else None

    def as_hideAutoSearchS(self):
        return self.flashObject.as_hideAutoSearch() if self._isDAAPIInited() else None

    def as_changeAutoSearchMainLabelS(self, value):
        return self.flashObject.as_changeAutoSearchMainLabel(value) if self._isDAAPIInited() else None

    def as_changeAutoSearchTimeDirectionS(self, value):
        return self.flashObject.as_changeAutoSearchTimeDirection(value) if self._isDAAPIInited() else None

    def as_changeAutoSearchCountDownSecondsS(self, value):
        return self.flashObject.as_changeAutoSearchCountDownSeconds(value) if self._isDAAPIInited() else None
