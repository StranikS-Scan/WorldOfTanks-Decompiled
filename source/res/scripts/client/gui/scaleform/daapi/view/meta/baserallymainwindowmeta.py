# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyMainWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseRallyMainWindowMeta(DAAPIModule):

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def canGoBack(self):
        self._printOverrideError('canGoBack')

    def onBrowseRallies(self):
        self._printOverrideError('onBrowseRallies')

    def onCreateRally(self):
        self._printOverrideError('onCreateRally')

    def onJoinRally(self, rallyId, slotIndex, peripheryId):
        self._printOverrideError('onJoinRally')

    def onAutoMatch(self, value, values):
        self._printOverrideError('onAutoMatch')

    def autoSearchApply(self, value):
        self._printOverrideError('autoSearchApply')

    def autoSearchCancel(self, value):
        self._printOverrideError('autoSearchCancel')

    def as_loadViewS(self, flashAlias, pyAlias):
        if self._isDAAPIInited():
            return self.flashObject.as_loadView(flashAlias, pyAlias)

    def as_enableWndCloseBtnS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_enableWndCloseBtn(value)

    def as_autoSearchEnableBtnS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_autoSearchEnableBtn(value)

    def as_changeAutoSearchStateS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_changeAutoSearchState(value)

    def as_hideAutoSearchS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_hideAutoSearch()
