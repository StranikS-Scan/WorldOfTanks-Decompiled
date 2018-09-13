# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HeaderTutorialWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class HeaderTutorialWindowMeta(DAAPIModule):

    def goNextStep(self):
        self._printOverrideError('goNextStep')

    def goPrevStep(self):
        self._printOverrideError('goPrevStep')

    def setStep(self, step):
        self._printOverrideError('setStep')

    def requestToLeave(self):
        self._printOverrideError('requestToLeave')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
