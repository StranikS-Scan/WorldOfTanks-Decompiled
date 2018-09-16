# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LinkedSetDetailsOverlayMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LinkedSetDetailsOverlayMeta(BaseDAAPIComponent):

    def startClick(self, eventID):
        self._printOverrideError('startClick')

    def setPage(self, pageID):
        self._printOverrideError('setPage')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setDataVideoS(self, data):
        return self.flashObject.as_setDataVideo(data) if self._isDAAPIInited() else None

    def as_setColorPagesS(self, colorPages):
        return self.flashObject.as_setColorPages(colorPages) if self._isDAAPIInited() else None

    def as_setPageS(self, index):
        return self.flashObject.as_setPage(index) if self._isDAAPIInited() else None
