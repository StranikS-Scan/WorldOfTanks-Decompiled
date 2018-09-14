# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SwitchModePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SwitchModePanelMeta(BaseDAAPIComponent):

    def switchMode(self):
        self._printOverrideError('switchMode')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setVisibleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setVisible(value)
