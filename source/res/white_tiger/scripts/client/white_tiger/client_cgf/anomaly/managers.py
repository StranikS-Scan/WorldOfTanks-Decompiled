# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/anomaly/managers.py
import typing
import functools
import BigWorld
import SoundGroups
import CGF
from GenericComponents import TransformComponent, RemoveGoDelayedComponent
from cgf_network import NetworkEntity
from Triggers import AreaTriggerComponent
from helpers import dependency
from constants import MarkerItem, IS_EDITOR
from debug_utils import LOG_ERROR
from shared_utils import nextTick
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from events_core_common.events_core_cgf.helpers import getVehicleFromGO
from skeletons.gui.battle_session import IBattleSessionProvider
from wt_settings import g_wt_config
from white_tiger_common.common_cgf.cgf_helpers import registerWTManager
from white_tiger_common.common_cgf.anomaly.components import AnomalyZoneComponent
from white_tiger.client_cgf.effects.components import WTAnomalyDisappearComponent, WTAnimatorLinkComponent, WTAnomalyBinocularComponent
if not IS_EDITOR:
    from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
    from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTTimerViewState
if typing.TYPE_CHECKING:
    from typing import Dict, Set
    from Vehicle import Vehicle

@registerWTManager(CGF.DomainOption.DomainClient)
class AnomalyManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __ANOMALY_START_3D_SOUND = 'ev_wt_gameplay_anomaly_start'
    __ANOMALY_STOP_3D_SOUND = 'ev_wt_gameplay_anomaly_stop'
    __ANOMALY_START_2D_SOUND = 'ev_wt_gameplay_anomaly_in'
    __ANOMALY_STOP_2D_SOUND = 'ev_wt_gameplay_anomaly_out'
    __POSTPONED_DESTRUCTION_DELAY = 1.0

    def __init__(self):
        super(AnomalyManager, self).__init__()
        self.__anomaliesData = {}
        self.__affectedVehicles = {}
        self.__disappearEffectsData = {}

    def destroy(self):
        self.__removeDisappearGOs()
        self.__disappearEffectsData.clear()
        self.__disappearEffectsData = None
        self.__anomaliesData.clear()
        self.__anomaliesData = None
        self.__affectedVehicles.clear()
        self.__affectedVehicles = None
        binoculars = BigWorld.binoculars()
        if not binoculars:
            return
        else:
            binoculars.setIsFlame(False)
            binoculars.setIsTiles(False)
            return

    @onAddedQuery(CGF.GameObject, AreaTriggerComponent, AnomalyZoneComponent, NetworkEntity)
    def onAdded(self, anomalyGO, areaTrigger, anomalyZone, _):
        anomalyZone.enterReactionID = areaTrigger.addEnterReaction(self.__onAnomalyZoneEntered)
        anomalyZone.exitReactionID = areaTrigger.addExitReaction(self.__onAnomalyZoneLeave)
        nextTick(self.__anomalyAppear(anomalyGO))

    @onRemovedQuery(CGF.GameObject, AreaTriggerComponent, AnomalyZoneComponent, TransformComponent, NetworkEntity)
    def onRemoved(self, anomalyGO, areaTrigger, anomalyZone, anomalyTransform, _):
        areaTrigger.removeEnterReaction(anomalyZone.enterReactionID)
        areaTrigger.removeExitReaction(anomalyZone.exitReactionID)
        self.__playDisappearEffect(anomalyTransform)
        self.__removeMarker(anomalyGO)
        self.__stop3DSound(anomalyGO)

    def __onAnomalyZoneEntered(self, vehicleGO, anomalyGO):
        vehicle = getVehicleFromGO(vehicleGO, self.spaceID)
        if not vehicle or vehicle.health <= 0:
            return
        alreadyInAnomaly = self.__isVehicleAlreadyInAnomaly(vehicle)
        if self.__affectedVehicles.get(vehicle.id):
            self.__affectedVehicles[vehicle.id].add(anomalyGO.id)
        else:
            self.__affectedVehicles[vehicle.id] = {anomalyGO.id}
        if not alreadyInAnomaly:
            self.__updateSN(vehicle, isVisible=True)
            self.__updateBinocularVisibility(vehicle, anomalyGO, isVisible=True)
            self.__update2DSound(vehicle, isEnter=True)

    def __onAnomalyZoneLeave(self, vehicleGO, anomalyGO):
        vehicle = getVehicleFromGO(vehicleGO, self.spaceID)
        if not vehicle:
            return
        if self.__affectedVehicles.get(vehicle.id):
            self.__affectedVehicles[vehicle.id].discard(anomalyGO.id)
            if not self.__affectedVehicles[vehicle.id]:
                del self.__affectedVehicles[vehicle.id]
        alreadyInAnomaly = self.__isVehicleAlreadyInAnomaly(vehicle)
        if not alreadyInAnomaly:
            self.__updateSN(vehicle, isVisible=False)
            self.__updateBinocularVisibility(vehicle, anomalyGO, isVisible=False)
            self.__update2DSound(vehicle, isEnter=False)

    def __anomalyAppear(self, go):
        entity = self.__getEntityByGO(go)
        if not entity:
            LOG_ERROR('No entity found for anomaly go', go.id)
            return
        self.__anomaliesData[go.id] = {}
        self.__createMarker(entity, go)
        self.__play3Dsound(entity, go)

    def __createMarker(self, entity, go):
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl:
            marker = ctrl.createMarker(entity.matrix, MarkerItem.ANOMALY)
            self.__anomaliesData[go.id].update({'markerID': ctrl.addMarker(marker)})

    def __removeMarker(self, go):
        markerID = self.__anomaliesData.get(go.id, {}).get('markerID', None)
        ctrl = self.sessionProvider.shared.areaMarker
        if ctrl and markerID:
            ctrl.removeMarker(markerID)
            del self.__anomaliesData[go.id]['markerID']
        return

    def __getEntityByGO(self, go):
        networkEntities = BigWorld.entities.valuesOfType('NetworkEntity')
        for entity in networkEntities:
            if entity.isConnected and go.id == entity.gameObject.id:
                return entity

    def __updateSN(self, vehicle, isVisible):
        if g_wt_config.isAnyTypeBoss(vehicle.typeDescriptor.type.compactDescr):
            return
        value = WTTimerViewState(isVisible, 0, 0)
        self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_ANOMALY, value, vehicleID=vehicle.id)

    def __isVehicleAlreadyInAnomaly(self, vehicle):
        if vehicle.id in self.__affectedVehicles:
            if len(self.__affectedVehicles[vehicle.id]) > 1:
                return True
        return False

    @onAddedQuery(CGF.GameObject, WTAnomalyDisappearComponent, TransformComponent)
    def onAddEffect(self, animatorGO, disappearComponent, transform):
        CGF.loadGameObject(disappearComponent.prefab, animatorGO.spaceID, transform.worldTransform, self.__onLoaded)

    def __onLoaded(self, disappearGO):
        self.__disappearEffectsData[disappearGO.id] = disappearGO

    def __playDisappearEffect(self, anomalyTransform):
        disappearGO = next(iter(self.__disappearEffectsData.values()))
        if not disappearGO or not disappearGO.isValid():
            return
        disappearTransform = disappearGO.findComponentByType(TransformComponent)
        disappearTransform.position = anomalyTransform.position
        animatorLink = disappearGO.findComponentByType(WTAnimatorLinkComponent)
        animator = animatorLink.linkToAnimator()
        duration = animator.getDuration()
        animator.start()
        disappearGO.createComponent(RemoveGoDelayedComponent, duration)
        del self.__disappearEffectsData[disappearGO.id]

    def __removeDisappearGOs(self):
        for disappearGO, _ in self.__disappearEffectsData.values():
            if disappearGO and disappearGO.isValid():
                CGF.removeGameObject(disappearGO)

    def __updateBinocularVisibility(self, vehicle, anomalyGO, isVisible):
        if vehicle.avatarID != BigWorld.player().id:
            return
        if BigWorld.isForwardPipeline():
            return
        binocularEffects = self.__getBinocularEffects(anomalyGO)
        if not binocularEffects:
            LOG_ERROR('No binocular effects found for anomaly go', anomalyGO.id)
            return
        binoculars = BigWorld.binoculars()
        if not binoculars:
            return
        if isVisible:
            for effect in binocularEffects:
                binoculars.loadConfig(effect)

        binoculars.setIsFlame(isVisible)
        binoculars.setIsTiles(isVisible)

    def __getBinocularEffects(self, anomalyGO):
        binocularComponent = anomalyGO.findComponentByType(WTAnomalyBinocularComponent)
        if binocularComponent:
            return binocularComponent.binocularsEffects
        LOG_ERROR('No WTAnomalyBinocularComponent in anomaly go', anomalyGO.id)

    def __update2DSound(self, vehicle, isEnter):
        if vehicle.avatarID != BigWorld.player().id:
            return
        if isEnter:
            SoundGroups.g_instance.playSound2D(self.__ANOMALY_START_2D_SOUND)
        else:
            SoundGroups.g_instance.playSound2D(self.__ANOMALY_STOP_2D_SOUND)

    def __play3Dsound(self, entity, go):
        soundObject = SoundGroups.g_instance.WWgetSoundObject('sound_anomaly_' + str(entity.id), entity.matrix)
        soundObject.play(self.__ANOMALY_START_3D_SOUND)
        self.__anomaliesData[go.id].update({'soundObject': soundObject})

    def __stop3DSound(self, go):
        soundObject = self.__anomaliesData.get(go.id, {}).get('soundObject')
        if soundObject:
            soundObject.play(self.__ANOMALY_STOP_3D_SOUND)
            BigWorld.callback(self.__POSTPONED_DESTRUCTION_DELAY, functools.partial(self.__postponedDestruction, go.id))

    def __postponedDestruction(self, goID):
        if goID in self.__anomaliesData:
            del self.__anomaliesData[goID]['soundObject']
