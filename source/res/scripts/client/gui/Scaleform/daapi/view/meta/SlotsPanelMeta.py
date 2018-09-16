# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SlotsPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SlotsPanelMeta(BaseDAAPIComponent):

    def getSlotTooltipBody(self, orderID):
        self._printOverrideError('getSlotTooltipBody')

    def as_setPanelPropsS(self, data):
        """
        :param data: Represented by SlotsPanelPropsVO (AS)
        """
        return self.flashObject.as_setPanelProps(data) if self._isDAAPIInited() else None

    def as_setSlotsS(self, orders):
        """
        :param orders: Represented by Vector.<SlotVO> (AS)
        """
        return self.flashObject.as_setSlots(orders) if self._isDAAPIInited() else None

    def as_updateSlotS(self, data):
        """
        :param data: Represented by SlotVO (AS)
        """
        return self.flashObject.as_updateSlot(data) if self._isDAAPIInited() else None
