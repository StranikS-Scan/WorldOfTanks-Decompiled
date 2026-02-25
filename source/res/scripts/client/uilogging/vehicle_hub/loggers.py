# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/vehicle_hub/loggers.py
import typing
from uilogging.base.logger import MetricsLogger, createPartnerID
from uilogging.vehicle_hub.constants import LogActions, Features, Tabs, TIME_LIMIT
from uilogging.vehicle_hub.constants import LogItems

class ArmorTabLogger(MetricsLogger):
    __slots__ = ('_vehicleCD', '_partnerID', '_tooltipOpenTime')

    def __init__(self, vehCD):
        super(ArmorTabLogger, self).__init__(Features.ARMOR_INSPECTOR)
        self._vehicleCD = str(vehCD)
        self._partnerID = createPartnerID()

    @property
    def vehicleCD(self):
        return self._vehicleCD

    @property
    def partnerID(self):
        return self._partnerID

    def logOpen(self):
        self.log(action=LogActions.OPEN, item=Tabs.ARMOR_TAB, itemState=self._vehicleCD, partnerID=self._partnerID)

    def logClose(self):
        self.log(action=LogActions.CLOSE, item=Tabs.ARMOR_TAB, itemState=self._vehicleCD, partnerID=self._partnerID)

    def tooltipOpened(self):
        self.startAction(LogActions.TOOLTIP_ACTION)

    def armorTooltipClosed(self):
        self._tooltipClosed(LogItems.ARMOR_TOOLTIP)

    def _tooltipClosed(self, item):
        self.stopAction(action=LogActions.TOOLTIP_ACTION, item=item, parentScreen=Tabs.ARMOR_TAB, itemState=self._vehicleCD, partnerID=self._partnerID, timeLimit=TIME_LIMIT)
