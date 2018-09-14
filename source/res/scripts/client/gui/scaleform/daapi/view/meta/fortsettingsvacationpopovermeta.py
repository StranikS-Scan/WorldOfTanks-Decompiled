# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsVacationPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortSettingsVacationPopoverMeta(SmartPopOverView):

    def onApply(self, data):
        self._printOverrideError('onApply')

    def as_setTextsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTexts(data)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
