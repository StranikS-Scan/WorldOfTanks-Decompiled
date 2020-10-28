# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventTankRentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventTankRentMeta(BaseDAAPIComponent):

    def onEventRentClick(self):
        self._printOverrideError('onEventRentClick')

    def onToQuestsClick(self):
        self._printOverrideError('onToQuestsClick')

    def as_setRentDataS(self, data):
        return self.flashObject.as_setRentData(data) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None
