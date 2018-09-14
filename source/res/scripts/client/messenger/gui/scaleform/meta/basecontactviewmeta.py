# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/BaseContactViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BaseContactViewMeta(BaseDAAPIComponent):

    def onOk(self, data):
        self._printOverrideError('onOk')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_updateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_update(data)

    def as_setOkBtnEnabledS(self, isEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_setOkBtnEnabled(isEnabled)

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)

    def as_closeViewS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_closeView()
