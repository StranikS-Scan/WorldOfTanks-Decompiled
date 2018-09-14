# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsPeripheryPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortSettingsPeripheryPopoverMeta(SmartPopOverView):

    def onApply(self, server):
        self._printOverrideError('onApply')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setTextsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTexts(data)
