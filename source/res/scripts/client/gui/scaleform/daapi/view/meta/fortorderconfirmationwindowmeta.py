# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderConfirmationWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortOrderConfirmationWindowMeta(AbstractWindowView):

    def submit(self, count):
        self._printOverrideError('submit')

    def getTimeStr(self, time):
        self._printOverrideError('getTimeStr')

    def as_setDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(value)

    def as_setSettingsS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setSettings(value)
