# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanProfileBaseViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanProfileBaseViewMeta(BaseDAAPIComponent):

    def onHeaderButtonClick(self, actionId):
        self._printOverrideError('onHeaderButtonClick')

    def viewSize(self, width, height):
        self._printOverrideError('viewSize')

    def as_setClanInfoS(self, data):
        return self.flashObject.as_setClanInfo(data) if self._isDAAPIInited() else None

    def as_setHeaderStateS(self, data):
        return self.flashObject.as_setHeaderState(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_showWaitingS(self, value):
        return self.flashObject.as_showWaiting(value) if self._isDAAPIInited() else None

    def as_showDummyS(self, data):
        return self.flashObject.as_showDummy(data) if self._isDAAPIInited() else None

    def as_hideDummyS(self):
        return self.flashObject.as_hideDummy() if self._isDAAPIInited() else None

    def as_loadBrowserS(self):
        return self.flashObject.as_loadBrowser() if self._isDAAPIInited() else None
