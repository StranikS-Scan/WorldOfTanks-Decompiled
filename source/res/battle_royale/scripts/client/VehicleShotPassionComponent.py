# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleShotPassionComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from Event import EventsSubscriber
ShotPassionInfo = namedtuple('ShotPassionInfo', ('endTime', 'stage'))

class VehicleShotPassionComponent(BigWorld.DynamicScriptComponent):
    EQUIPMENT_NAME = BattleRoyaleEquipments.SHOT_PASSION

    def __init__(self, *args):
        super(VehicleShotPassionComponent, self).__init__()
        self.__es = EventsSubscriber()
        self.__onUpdated()
        self.__es.subscribeToEvent(self.entity.guiSessionProvider.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)

    def getInfo(self):
        return ShotPassionInfo(self.endTime, self.stage)

    def set_endTime(self, prev):
        self.__onUpdated()

    def set_stage(self, prev):
        self.__onUpdated()

    def onDestroy(self):
        self.__onUpdated(ShotPassionInfo(0.0, 0))
        self.__es.unsubscribeFromAllEvents()
        self.__es = None
        return

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__onUpdated()

    def __onUpdated(self, info=None):
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, info or self.getInfo())
