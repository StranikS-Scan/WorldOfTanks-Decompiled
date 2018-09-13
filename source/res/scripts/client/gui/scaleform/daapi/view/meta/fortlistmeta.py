# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class FortListMeta(BaseRallyListView):

    def changeDivisionIndex(self, index):
        self._printOverrideError('changeDivisionIndex')

    def as_getDivisionsDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getDivisionsDP()

    def as_setSelectedDivisionS(self, index):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedDivision(index)

    def as_setDetailsS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setDetails(value)

    def as_setCreationEnabledS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCreationEnabled(value)
