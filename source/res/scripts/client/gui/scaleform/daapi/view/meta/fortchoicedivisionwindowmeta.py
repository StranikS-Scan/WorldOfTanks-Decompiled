# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortChoiceDivisionWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortChoiceDivisionWindowMeta(AbstractWindowView):

    def selectedDivision(self, divisionID):
        self._printOverrideError('selectedDivision')

    def changedDivision(self, divisionID):
        self._printOverrideError('changedDivision')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
