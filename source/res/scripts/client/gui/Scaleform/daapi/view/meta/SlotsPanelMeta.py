# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SlotsPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SlotsPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def getSlotTooltipBody(self, orderID):
        """
        :param orderID:
        :return String:
        """
        self._printOverrideError('getSlotTooltipBody')

    def as_setPanelPropsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setPanelProps(data) if self._isDAAPIInited() else None

    def as_setSlotsS(self, orders):
        """
        :param orders:
        :return :
        """
        return self.flashObject.as_setSlots(orders) if self._isDAAPIInited() else None

    def as_updateSlotS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateSlot(data) if self._isDAAPIInited() else None
