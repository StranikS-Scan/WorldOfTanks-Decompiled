# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RetrainCrewWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RetrainCrewWindowMeta(AbstractWindowView):

    def submit(self, data):
        self._printOverrideError('submit')

    def changeRetrainType(self, retrainTypeIndex):
        self._printOverrideError('changeRetrainType')

    def as_setCommonDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCommonData(data)

    def as_updateDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateData(data)
