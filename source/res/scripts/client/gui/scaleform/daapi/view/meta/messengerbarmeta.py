# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MessengerBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MessengerBarMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def channelButtonClick(self):
        self._printOverrideError('channelButtonClick')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by MessegerBarInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setVehicleCompareCartButtonVisibleS(self, value):
        return self.flashObject.as_setVehicleCompareCartButtonVisible(value) if self._isDAAPIInited() else None

    def as_openVehicleCompareCartPopoverS(self, value):
        return self.flashObject.as_openVehicleCompareCartPopover(value) if self._isDAAPIInited() else None

    def as_showAddVehicleCompareAnimS(self, data):
        """
        :param data: Represented by VehicleCompareAnimVO (AS)
        """
        return self.flashObject.as_showAddVehicleCompareAnim(data) if self._isDAAPIInited() else None
