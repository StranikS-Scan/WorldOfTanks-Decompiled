# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LegionariesFilterPopoverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LegionariesFilterPopoverMeta(DAAPIModule):

    def applyFilter(self, wins, battles, requirements):
        self._printOverrideError('applyFilter')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
