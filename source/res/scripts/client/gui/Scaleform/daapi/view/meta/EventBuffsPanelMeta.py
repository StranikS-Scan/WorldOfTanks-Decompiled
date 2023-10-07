# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBuffsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBuffsPanelMeta(BaseDAAPIComponent):

    def as_addBuffSlotS(self, id, imageName, tooltipText):
        return self.flashObject.as_addBuffSlot(id, imageName, tooltipText) if self._isDAAPIInited() else None

    def as_removeBuffSlotS(self, id):
        return self.flashObject.as_removeBuffSlot(id) if self._isDAAPIInited() else None
