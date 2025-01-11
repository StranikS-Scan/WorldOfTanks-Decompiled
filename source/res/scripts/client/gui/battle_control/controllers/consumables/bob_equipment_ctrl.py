# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/bob_equipment_ctrl.py
import typing
import BigWorld
import CGF
from constants import EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from items import vehicles
from points_of_interest.components import PoiStateComponent
from points_of_interest_shared import PoiEquipmentNamesByPoiType
if typing.TYPE_CHECKING:
    from PoiComponent import PoiComponent

class BobEquipmentController(equipment_ctrl.EquipmentsController):

    def startControl(self, *args):
        super(BobEquipmentController, self).startControl(*args)
        g_eventBus.addListener(events.PointOfInterestEvent.ADDED, self.__onPoiAdded, scope=EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        g_eventBus.removeListener(events.PointOfInterestEvent.ADDED, self.__onPoiAdded, scope=EVENT_BUS_SCOPE.BATTLE)
        super(BobEquipmentController, self).stopControl()

    def clear(self, leave=True):
        super(BobEquipmentController, self).clear(leave)
        if not leave:
            self.__rediscoverPoi()

    def __onPoiAdded(self, event):
        ctx = event.ctx
        point = ctx['point']
        self.__addPoiByType(point.type)

    def __rediscoverPoi(self):
        statesQuery = CGF.Query(BigWorld.player().spaceID, PoiStateComponent)
        for poiState in statesQuery:
            self.__addPoiByType(poiState.type)

    def __addPoiByType(self, poiType):
        equipment = self.__getPoiEquipment(poiType)
        if equipment is not None:
            self.setEquipment(intCD=equipment.compactDescr, quantity=0, stage=EQUIPMENT_STAGES.EXHAUSTED, timeRemaining=0, totalTime=0)
        return

    @staticmethod
    def __getPoiEquipment(poiType):
        cache = vehicles.g_cache
        name = PoiEquipmentNamesByPoiType[poiType]
        equipmentID = cache.equipmentIDs().get(name)
        return cache.equipments()[equipmentID] if equipmentID is not None else None


class BobReplayEquipmentController(equipment_ctrl.EquipmentsReplayPlayer, BobEquipmentController):
    pass
