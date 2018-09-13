# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortChoiceDivisionWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortChoiceDivisionWindowMeta(DAAPIModule):

    def selectedDivision(self, divisionID):
        self._printOverrideError('selectedDivision')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
