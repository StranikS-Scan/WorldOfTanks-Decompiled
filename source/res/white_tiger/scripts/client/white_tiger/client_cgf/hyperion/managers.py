# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/hyperion/managers.py
import logging
import typing
from functools import partial
import BigWorld
import CGF
from Triggers import AreaTriggerComponent
from constants import IS_EDITOR
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from events_core_common.events_core_cgf.helpers import getVehicleFromGO
from wt_settings import g_wt_config
from white_tiger_common.wt_constants import WT_TEAMS
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from white_tiger.client_cgf.hyperion.components import WTHyperionNotificationComponent
if typing.TYPE_CHECKING:
    from BigWorld import Entity
    from Vehicle import Vehicle
if not IS_EDITOR:
    from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
_logger = logging.getLogger(__name__)

class HyperionTimerViewState(object):
    __slots__ = ('visible', 'totalTime', 'finishTime')

    def __init__(self, visible, totalTime, finishTime):
        self.visible = visible
        self.totalTime = totalTime
        self.finishTime = finishTime


@registerWTManager(CGF.DomainOption.DomainClient)
class WTHyperionNotificationManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __HYPERION_NOTIFICATIONS = {'boss': VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING,
     'boss_2025': VEHICLE_VIEW_STATE.WT_HYPERION_2025_WARNING_CHARGING,
     'boss_special': VEHICLE_VIEW_STATE.WT_HYPERION_2025_WARNING_CHARGING}

    def __init__(self):
        super(WTHyperionNotificationManager, self).__init__()
        vInfo = self.__guiSessionProvider.getArenaDP().getVehiclesInfoIterator()
        self.__affectedVehiclesID = set()
        self.__cd = CallbackDelayer()
        self.__notificationType = VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING
        for vehicle in vInfo:
            if g_wt_config.isAnyTypeBoss(vehicle.vehicleType.compactDescr):
                vehData = g_wt_config.getVehicleData(vehicle.vehicleType.compactDescr)
                self.__notificationType = self.__HYPERION_NOTIFICATIONS[vehData.type]

    def destroy(self):
        self.__affectedVehiclesID.clear()
        self.__cd.destroy()
        self.__cd = None
        return

    @onAddedQuery(CGF.GameObject, AreaTriggerComponent, WTHyperionNotificationComponent)
    def onAddedHyperionNotification(self, _, areaTrigger, notificationComponent):
        notificationComponent.enterReactionID = areaTrigger.addEnterReaction(self.__onHyperionZoneEnter)
        notificationComponent.exitReactionID = areaTrigger.addExitReaction(self.__onHyperionZoneLeave)

    @onRemovedQuery(CGF.GameObject, AreaTriggerComponent, WTHyperionNotificationComponent)
    def onRemovedHyperionNotification(self, _, areaTrigger, notificationComponent):
        areaTrigger.removeEnterReaction(notificationComponent.enterReactionID)
        areaTrigger.removeExitReaction(notificationComponent.exitReactionID)

    def __onHyperionZoneEnter(self, vehicleGO, hyperionNotificationGO):
        vehicle = getVehicleFromGO(vehicleGO, self.spaceID)
        if not vehicle or vehicle.health <= 0:
            return
        if vehicle.team != WT_TEAMS.HUNTERS_TEAM:
            return
        hyperionEntityGO = self.__getEntityFromGO(hyperionNotificationGO, self.spaceID)
        if not hyperionEntityGO:
            _logger.error('No hyperionEntityGO found. No notification timer will be show')
            return
        hyperionEntity = self.__findHyperion(hyperionEntityGO)
        if not hyperionEntity:
            _logger.error('No hyperionEntity found. No notification timer will be show')
            return
        chargingTimeEnd = hyperionEntity.startTime + hyperionEntity.equipment.chargingDelay
        currentTime = BigWorld.serverTime()
        countdownTime = chargingTimeEnd if chargingTimeEnd > currentTime else 0
        value = HyperionTimerViewState(True, hyperionEntity.equipment.chargingDelay if countdownTime else 0, countdownTime)
        self.__guiSessionProvider.invalidateVehicleState(self.__notificationType, value, vehicleID=vehicle.id)
        self.__affectedVehiclesID.add(vehicle.id)
        if countdownTime > 0:
            self.__cd.delayCallback(countdownTime - currentTime, partial(self.__updateNotificationTimer, vehicle))

    def __onHyperionZoneLeave(self, vehicleGO, _):
        vehicle = getVehicleFromGO(vehicleGO, self.spaceID)
        if not vehicle:
            return
        if vehicle.team != WT_TEAMS.HUNTERS_TEAM:
            return
        value = HyperionTimerViewState(False, 0, 0)
        self.__guiSessionProvider.invalidateVehicleState(self.__notificationType, value, vehicleID=vehicle.id)
        self.__affectedVehiclesID.discard(vehicle.id)

    def __getEntityFromGO(self, go, spaceID):
        hierarchyManager = CGF.HierarchyManager(spaceID)
        return None if not hierarchyManager else hierarchyManager.getTopMostParent(go)

    def __findHyperion(self, go):
        modA = BigWorld.entities.valuesOfType('WTHyperionModA')
        modB = BigWorld.entities.valuesOfType('WTHyperionModB')
        for entity in modA + modB:
            if go.id == entity.entityGameObject.id:
                return entity

    def __updateNotificationTimer(self, vehicle):
        if vehicle.id not in self.__affectedVehiclesID:
            return
        if vehicle.health <= 0:
            self.__affectedVehiclesID.discard(vehicle.id)
            return
        value = HyperionTimerViewState(True, 0, 0)
        self.__guiSessionProvider.invalidateVehicleState(self.__notificationType, value, vehicleID=vehicle.id)
