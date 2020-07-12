# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CalloutPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CalloutPanelMeta(BaseDAAPIComponent):

    def onHideCompleted(self):
        self._printOverrideError('onHideCompleted')

    def onHideStart(self):
        self._printOverrideError('onHideStart')

    def as_setDataS(self, action, vehicleType, vehicleName, leftText, rightText, keyText):
        return self.flashObject.as_setData(action, vehicleType, vehicleName, leftText, rightText, keyText) if self._isDAAPIInited() else None

    def as_setHideDataS(self, wasAnswered, answeredAction):
        return self.flashObject.as_setHideData(wasAnswered, answeredAction) if self._isDAAPIInited() else None
