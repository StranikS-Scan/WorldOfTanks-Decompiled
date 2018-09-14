# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortIntelligenceWindowMeta(AbstractWindowView):

    def requestClanFortInfo(self, index):
        self._printOverrideError('requestClanFortInfo')

    def as_setClanFortInfoS(self, clanFortVO):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanFortInfo(clanFortVO)

    def as_setDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(value)

    def as_setStatusTextS(self, statusText):
        if self._isDAAPIInited():
            return self.flashObject.as_setStatusText(statusText)

    def as_getSearchDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getSearchDP()

    def as_getCurrentListIndexS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getCurrentListIndex()

    def as_selectByIndexS(self, index):
        if self._isDAAPIInited():
            return self.flashObject.as_selectByIndex(index)

    def as_setTableHeaderS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTableHeader(data)
