# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class VehicleBuyWindowMeta(AbstractWindowView):

    def submit(self, data):
        self._printOverrideError('submit')

    def storeSettings(self, expanded):
        self._printOverrideError('storeSettings')

    def as_setGoldS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_setGold(gold)

    def as_setCreditsS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCredits(value)

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)

    def as_setEnabledSubmitBtnS(self, enabled):
        if self._isDAAPIInited():
            return self.flashObject.as_setEnabledSubmitBtn(enabled)
