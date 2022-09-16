# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/comp7_equipment_ctrl.py
import typing
import BigWorld
import CGF
import Event
from constants import EQUIPMENT_STAGES
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from items import vehicles
from points_of_interest.components import PoiStateComponent
from points_of_interest_shared import PoiEquipmentNamesByPoiType
if typing.TYPE_CHECKING:
    from helpers.fixed_dict import RoleEquipmentState
    from PoiComponent import PoiComponent

class Comp7EquipmentController(equipment_ctrl.EquipmentsController):

    def __init__(self, setup):
        super(Comp7EquipmentController, self).__init__(setup)
        self.onRoleEquipmentStateChanged = Event.Event(self._eManager)
        self.onRoleEquipmentCounterChanged = Event.Event(self._eManager)
        self.__roleEquipmentState = None
        self.__roleEquipmentCounter = None
        self.__roleEquipmentPreviousState = None
        return

    def startControl(self, *args):
        super(Comp7EquipmentController, self).startControl(*args)
        g_eventBus.addListener(events.PointOfInterestEvent.ADDED, self.__onPoiAdded, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.RoleSkillEvent.STATE_CHANGED, self.__onRoleEquipmentStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.RoleSkillEvent.COUNTER_CHANGED, self.__onRoleEquipmentCounterChanged, scope=EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        g_eventBus.removeListener(events.PointOfInterestEvent.ADDED, self.__onPoiAdded, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.RoleSkillEvent.STATE_CHANGED, self.__onRoleEquipmentStateChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.RoleSkillEvent.COUNTER_CHANGED, self.__onRoleEquipmentCounterChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        super(Comp7EquipmentController, self).stopControl()

    def clear(self, leave=True):
        if leave:
            self.__roleEquipmentState = None
            self.__roleEquipmentCounter = None
            self.__roleEquipmentPreviousState = None
        super(Comp7EquipmentController, self).clear(leave)
        if not leave:
            self.__rediscoverPoi()
            self.__rediscoverRoleSkill()
        return

    def getRoleEquipmentState(self):
        return self.__roleEquipmentState

    def getRoleEquipmentCounter(self):
        return self.__roleEquipmentCounter

    def getRoleEquipmentPreviousState(self):
        return self.__roleEquipmentPreviousState

    def __onPoiAdded(self, event):
        ctx = event.ctx
        point = ctx['point']
        self.__addPoiByType(point.type)

    def __rediscoverPoi(self):
        statesQuery = CGF.Query(BigWorld.player().spaceID, PoiStateComponent)
        for poiState in statesQuery:
            self.__addPoiByType(poiState.type)

    def __rediscoverRoleSkill(self):
        from VisualScriptEquipment import VisualScriptEquipment
        vehicle = avatar_getter.getPlayerVehicle()
        if vehicle is not None and vehicle.entityGameObject is not None:
            equipmentComponent = vehicle.entityGameObject.findComponentByType(VisualScriptEquipment)
            if equipmentComponent is not None:
                equipmentComponent.update()
        return

    def __addPoiByType(self, poiType):
        equipment = self.__getPoiEquipment(poiType)
        if equipment is not None:
            self.setEquipment(intCD=equipment.compactDescr, quantity=0, stage=EQUIPMENT_STAGES.EXHAUSTED, timeRemaining=0, totalTime=0)
        return

    def __onRoleEquipmentStateChanged(self, event):
        ctx = event.ctx
        state = ctx['state']
        previousState = ctx['previousState']
        self.__roleEquipmentState = state
        self.__roleEquipmentPreviousState = previousState
        self.onRoleEquipmentStateChanged(state, previousState)

    def __onRoleEquipmentCounterChanged(self, event):
        ctx = event.ctx
        value = ctx['value']
        self.__roleEquipmentCounter = value
        self.onRoleEquipmentCounterChanged(value)

    @staticmethod
    def __getPoiEquipment(poiType):
        cache = vehicles.g_cache
        name = PoiEquipmentNamesByPoiType[poiType]
        equipmentID = cache.equipmentIDs().get(name)
        return cache.equipments()[equipmentID] if equipmentID is not None else None


class Comp7ReplayEquipmentController(equipment_ctrl.EquipmentsReplayPlayer, Comp7EquipmentController):
    pass
