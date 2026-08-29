# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/dome/managers.py
import logging
import typing
import BigWorld
import CGF
from functools import partial
from helpers import dependency
from constants import MarkerItem
from Triggers import AreaTriggerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_components.cgf_helpers import getVehicleFromGO
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.helpers.PrefabHelper import AppearancePrefabHandler
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from white_tiger_common.common_cgf.dome.helpers import WT_DOME_COMPONENTS
from white_tiger.client_cgf.dome.components import WTDomeClientComponent
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTTimerViewState
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playDomeSound
from white_tiger.client_cgf.dome.components import WTDomeClientInDomeHoundEffectComponent
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

@registerWTManager(CGF.DomainOption.DomainClient)
class WTDomeClientManager(CGF.ComponentManager):

    @onAddedQuery(*WT_DOME_COMPONENTS)
    def onAddedDome(self, go, domeComponent):
        if domeComponent.affectedTeam == -1:
            domeComponent.onReplicationDone += self.__onReplicationDone
        else:
            self.__onReplicationDone(domeComponent)

    def __onReplicationDone(self, domeComponent):
        go = domeComponent.entity.entityGameObject
        go.createComponent(WTDomeClientComponent)


@registerWTManager(CGF.DomainOption.DomainClient)
class WTDomeUIManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COMPONENTS = WT_DOME_COMPONENTS + (AreaTriggerComponent, WTDomeClientComponent)

    def __init__(self):
        super(WTDomeUIManager, self).__init__()
        self.__durations = {}
        self.__markers = {}
        self.__affectedTeamInDomePrefabHandlers = {}
        self.__inDomePrefabHandlerPath = None
        return

    def destroy(self):
        for domeID, prefabHandlersOnVehicle in self.__affectedTeamInDomePrefabHandlers.items():
            WTDomeUIManager.__clearPrefabHandlers(domeID, prefabHandlersOnVehicle)

        self.__affectedTeamInDomePrefabHandlers.clear()
        self.__durations.clear()
        self.__markers.clear()
        self.__durations = None
        self.__markers = None
        return

    @onAddedQuery(*_COMPONENTS)
    def onAdded(self, go, domeComponent, trigger, domeClient):
        self.__onAdded(go, domeComponent, trigger, domeClient)

    @onRemovedQuery(*_COMPONENTS)
    def onRemoved(self, go, domeComponent, trigger, domeClient):
        self.__onRemoved(go, domeComponent, trigger, domeClient)

    @onAddedQuery(CGF.GameObject, WTDomeClientComponent, WTDomeClientInDomeHoundEffectComponent)
    def onAddedEffectComponent(self, go, clientComponent, effectComponent):
        self.__inDomePrefabHandlerPath = effectComponent.effectPrefab
        self.__affectedTeamInDomePrefabHandlers[go.id] = {}

    def __onAdded(self, go, domeComponent, trigger, domeClient):
        duration = domeComponent.duration
        self.__durations[go.id] = WTTimerViewState(False, duration, BigWorld.serverTime() + duration)
        self.__createMarker(domeComponent)
        affectedTeam = domeComponent.affectedTeam
        domeClient.enterReactionID = trigger.addEnterReaction(partial(self.__onVehicleEntered, go.id, affectedTeam))
        domeClient.exitReactionID = trigger.addExitReaction(partial(self.__onVehicleExited, go.id, affectedTeam))

    def __onRemoved(self, go, domeComponent, trigger, domeClient):
        self.__durations.pop(go.id)
        self.__removeMarker(domeComponent)
        trigger.removeEnterReaction(domeClient.enterReactionID)
        trigger.removeExitReaction(domeClient.exitReactionID)
        prefabHandlersForDomID = self.__affectedTeamInDomePrefabHandlers.pop(go.id, None)
        if prefabHandlersForDomID is not None:
            WTDomeUIManager.__clearPrefabHandlers(go.id, prefabHandlersForDomID)
        return

    def __onVehicleEntered(self, domeID, affectedTeam, go, _):
        vehicle = getVehicleFromGO(go, self.spaceID)
        if not vehicle:
            return
        if vehicle.team == affectedTeam:
            prefabHandler = self.__affectedTeamInDomePrefabHandlers.get(domeID)[vehicle.id] = AppearancePrefabHandler(lambda : go is not None and vehicle is not None and domeID in self.__affectedTeamInDomePrefabHandlers and vehicle.id in self.__affectedTeamInDomePrefabHandlers.get(domeID))
            prefabHandler.load(vehicle.appearance, self.__inDomePrefabHandlerPath, lambda : None)
            self.__playInOutSound(vehicle, True)
            self.__showSN(vehicle, domeID, True)

    def __onVehicleExited(self, domeID, affectedTeam, go, _):
        vehicle = getVehicleFromGO(go, self.spaceID)
        if not vehicle:
            return
        else:
            if vehicle.team == affectedTeam:
                prefabHandler = self.__affectedTeamInDomePrefabHandlers.get(domeID).pop(vehicle.id, None)
                if prefabHandler is not None:
                    prefabHandler.unload()
                self.__playInOutSound(vehicle, False)
                self.__showSN(vehicle, domeID, False)
            return

    def __showSN(self, vehicle, domeID, visible):
        snTimerValue = self.__durations[domeID]
        snTimerValue.visible = visible
        vehicle.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_DOME, snTimerValue, vehicleID=vehicle.id)

    def __createMarker(self, domeComponent):
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl:
            marker = ctrl.createMarker(domeComponent.entity.matrix, MarkerItem.DOME)
            self.__markers[domeComponent.entity.id] = ctrl.addMarker(marker)

    def __removeMarker(self, domeComponent):
        marker = self.__markers.pop(domeComponent.entity.id)
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl:
            ctrl.removeMarker(marker)

    @staticmethod
    def __clearPrefabHandlers(domeID, prefabHandlersForDomID):
        for _, prefabHandler in prefabHandlersForDomID.items():
            prefabHandler.destroy()

        prefabHandlersForDomID.clear()

    @staticmethod
    def __playInOutSound(vehicle, isEntered):
        player = BigWorld.player()
        if player is None:
            return
        else:
            if player.id == vehicle.avatarID:
                playDomeSound(isEntered)
            return
