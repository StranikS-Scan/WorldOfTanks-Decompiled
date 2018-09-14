# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortSettingsWindowMeta(AbstractWindowView):

    def activateDefencePeriod(self):
        self._printOverrideError('activateDefencePeriod')

    def disableDefencePeriod(self):
        self._printOverrideError('disableDefencePeriod')

    def cancelDisableDefencePeriod(self):
        self._printOverrideError('cancelDisableDefencePeriod')

    def as_setFortClanInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setFortClanInfo(data)

    def as_setMainStatusS(self, title, msg, toolTip):
        if self._isDAAPIInited():
            return self.flashObject.as_setMainStatus(title, msg, toolTip)

    def as_setViewS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setView(value)

    def as_setDataForActivatedS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDataForActivated(data)

    def as_setCanDisableDefencePeriodS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCanDisableDefencePeriod(value)

    def as_setDataForNotActivatedS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDataForNotActivated(data)
