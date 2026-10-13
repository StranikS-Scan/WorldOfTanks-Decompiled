# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/portal_2d_markers/managers.py
import logging
import CGF
import GenericComponents
import BigWorld
import typing
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, onProcessQuery
from constants import IS_EDITOR
from portal_common_cgf.portal_helpers import registerPortalManager, isLowPreset
if IS_EDITOR:
    from portal_common_cgf.portal_2d_markers.components import PortalReplicableMarkerStatesComponent
else:
    from PortalReplicableMarkerStatesComponent import PortalReplicableMarkerStatesComponent
    from CampReplicableComponent import CampReplicableComponent
    from TeleportReplicableComponent import TeleportReplicableComponent
    from portal_client_cgf.portal_2d_markers.components import PortalAreaMarker
    from portal_constants import PORTAL_BATTLE_CTRL_ID
    from portal.gui.battle_control.controllers.portal_gui_controllers import getPortalBattleMarkersController
    from gui.battle_control import avatar_getter
    from items.utils import isclose
    from portal_common.portal_constants import TeleportMarkerStatesIDs
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from portal.gui.battle_control.controllers.markers.portal_markers_ctrl import PortalMarkersController

def everyNTime(n=1):

    def decorator(func):

        def wrapper(*args, **kwargs):
            wrapper.counter += 1
            return func(*args, **kwargs) if wrapper.counter % n == 0 or args[2] == 0.0 else None

        wrapper.counter = 0
        return wrapper

    return decorator


@registerPortalManager(CGF.DomainOption.DomainClient)
class PortalReplicableMarkerStatesManager(CGF.ComponentManager):

    def activate(self):
        TeleportReplicableComponent.onTeleportingChanged += self.__onTeleportReplicableStateChanged
        TeleportReplicableComponent.onCooldownChanged += self.__onTeleportReplicableStateChanged

    def deactivate(self):
        TeleportReplicableComponent.onCooldownChanged -= self.__onTeleportReplicableStateChanged
        TeleportReplicableComponent.onTeleportingChanged -= self.__onTeleportReplicableStateChanged

    @onAddedQuery(CGF.GameObject, PortalReplicableMarkerStatesComponent)
    def onPortalReplicableMarkerStatesAdded(self, go, markerStatesComponent):
        _logger.debug('Added PortalReplicableMarkerStates on GO %s', go.name)
        markerStatesComponent.onMarkersInitialized += self.__onMarkersInitialized
        markerStatesComponent.onMarkerStateChanged += self.__onMarkerStateChanged
        markerStatesComponent.onMarkerProgressChanged += self.__onMarkerProgressChanged

    @onAddedQuery(CGF.GameObject, GenericComponents.TransformComponent, CampReplicableComponent, PortalReplicableMarkerStatesComponent)
    def onCampMarkerStatesAdded(self, go, transformComponent, campComponent, markerStatesComponent):
        _logger.debug('Added PortalReplicableMarkerStates on campGO  %s', go.name)
        hm = CGF.HierarchyManager(self.spaceID)
        markerGOQuery = hm.findComponentsInHierarchy(go, PortalAreaMarker)
        markerComponents = [ markerComp for _, markerComp in markerGOQuery ]
        markerStatesComponent.initCampMarkers(go, markerComponents)

    @onAddedQuery(CGF.GameObject, GenericComponents.TransformComponent, TeleportReplicableComponent, PortalReplicableMarkerStatesComponent)
    def onTeleportMarkerStatesAdded(self, go, transformComponent, teleportComponent, markerStatesComponent):
        _logger.debug('Added PortalReplicableMarkerStates on teleportGO  %s', go.name)

    @onProcessQuery(CGF.GameObject, PortalReplicableMarkerStatesComponent, period=1.0)
    def onPortalReplicableMarkerTick(self, go, markerStatesComponent):
        if not markerStatesComponent.activeMarkerComponent:
            return
        else:
            activeMarker = markerStatesComponent.activeMarkerComponent
            if not activeMarker.hasProgressBar and not activeMarker.hasTimerBoard:
                return
            teleportComponent = go.findComponentByType(TeleportReplicableComponent)
            if teleportComponent:
                currentProgress, restTime = self.__getPersonalTeleportProgress(teleportComponent, activeMarker)
                if currentProgress is None:
                    currentProgress, restTime = self.__getAutoProgress(markerStatesComponent, activeMarker)
            else:
                currentProgress, restTime = self.__getAutoProgress(markerStatesComponent, activeMarker)
            if currentProgress is None and restTime is None:
                return
            portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
            if portalAreaMarkersController:
                portalAreaMarkersController.onMarkerProgressUpdated(activeMarker, currentProgress, restTime)
            return

    def __getAutoProgress(self, markerStatesComponent, activeMarker):
        startTime = markerStatesComponent.autoProgressStartTime
        duration = markerStatesComponent.autoProgressDuration
        if bool(startTime) ^ bool(duration):
            _logger.error('There must be both start and end time for automatic progress')
            return (None, None)
        elif startTime < 0 and duration < 0:
            return (None, None)
        elif not markerStatesComponent.maxProgress < 0:
            _logger.warning('Setting maxProgress for automatic progress forbidden.')
            markerStatesComponent.maxProgress = -1
            return (None, None)
        else:
            currentProgress = self.__calculateCurrentProgress(startTime, duration)
            restTime = int(startTime + duration - BigWorld.serverTime()) if activeMarker.hasTimerBoard else None
            return (currentProgress, restTime)

    @onRemovedQuery(CGF.GameObject, PortalReplicableMarkerStatesComponent)
    def onPortalReplicableMarkerStatesRemoved(self, go, markerStatesComponent):
        _logger.debug('Removed PortalReplicableMarkerStates from go  %s', go.name)
        markerStatesComponent.onMarkersInitialized -= self.__onMarkersInitialized
        markerStatesComponent.onMarkerStateChanged -= self.__onMarkerStateChanged
        markerStatesComponent.onMarkerProgressChanged -= self.__onMarkerProgressChanged

    def __calculateCurrentProgress(self, startTime, duration):
        maxProgress = 100
        restTime = startTime + duration - BigWorld.serverTime()
        return maxProgress - float(restTime) / duration * 100 if duration and restTime > 0 else 100

    def __getPersonalTeleportProgress(self, teleportComponent, activeMarker):
        attachedVehicleID = avatar_getter.getVehicleIDAttached()
        if not attachedVehicleID:
            return (None, None)
        else:
            tunnelComponents = [ comp for _, comp in self.__getTunnelTeleports(teleportComponent.index) ]
            if activeMarker.stateID == TeleportMarkerStatesIDs.TELEPORT_OCCUPIED:
                timeSpan = self.__findTeleportingTimeSpan(tunnelComponents, attachedVehicleID)
            elif activeMarker.stateID == TeleportMarkerStatesIDs.TELEPORT_COOLDOWN:
                timeSpan = self.__findCooldownTimeSpan(tunnelComponents, attachedVehicleID)
            else:
                return (None, None)
            return (None, None) if not timeSpan else self.__progressFromTimeSpan(BigWorld.serverTime(), timeSpan[0], timeSpan[1], activeMarker)

    def __findTeleportingTimeSpan(self, tunnelComponents, vehicleID):
        for comp in tunnelComponents:
            for index, vid in enumerate(comp.teleportingVehicleIDs):
                if vid != vehicleID:
                    continue
                startTime = comp.teleportingStartTimes[index] if index < len(comp.teleportingStartTimes) else 0.0
                finishTime = comp.teleportingFinishTimes[index] if index < len(comp.teleportingFinishTimes) else 0.0
                if startTime > 0 and finishTime > startTime:
                    return (startTime, finishTime)

        return (None, None)

    def __findCooldownTimeSpan(self, tunnelComponents, vehicleID):
        for comp in tunnelComponents:
            for index, vid in enumerate(comp.cooldownVehicleIDs):
                if vid != vehicleID:
                    continue
                startTime = comp.cooldownStartTimes[index] if index < len(comp.cooldownStartTimes) else 0.0
                finishTime = comp.cooldownFinishTimes[index] if index < len(comp.cooldownFinishTimes) else 0.0
                if finishTime > 0:
                    return (startTime, finishTime)

        return (None, None)

    def __progressFromTimeSpan(self, serverTime, startTime, finishTime, activeMarker):
        restTime = finishTime - serverTime
        duration = finishTime - startTime
        if duration > 0:
            progress = (serverTime - startTime) / duration * 100.0
        else:
            progress = 0.0 if serverTime < finishTime else 100.0
        currentProgress = max(0.0, min(100.0, progress))
        timerRestTime = int(restTime) if activeMarker.hasTimerBoard else None
        return (currentProgress, timerRestTime)

    def __onMarkerStateChanged(self, go, state):
        if go.findComponentByType(TeleportReplicableComponent):
            state = self.__getPersonalTeleportState(go)
        self.__applyMarkerState(go, state)

    def __applyMarkerState(self, go, state):
        hm = CGF.HierarchyManager(self.spaceID)
        children = hm.getChildrenIncludingInactive(go) or []
        markerStateComponent = go.findComponentByType(PortalReplicableMarkerStatesComponent)
        if not markerStateComponent:
            _logger.error('Received marker update but no PortalReplicableMarkerStatesComponent found')
            return
        self.__invalidateMarkerState(markerStateComponent)
        for child in children:
            childMarkerComponent = child.findComponentByType(PortalAreaMarker)
            if not childMarkerComponent:
                continue
            if state == childMarkerComponent.stateID:
                child.activate()
                markerStateComponent.activeMarkerComponent = childMarkerComponent
            child.deactivate()

    def __onTeleportReplicableStateChanged(self, go, *_):
        teleportComponent = go.findComponentByType(TeleportReplicableComponent)
        if not teleportComponent:
            return
        for tunnelGO, _tunnelComp in self.__getTunnelTeleports(teleportComponent.index):
            if tunnelGO.findComponentByType(PortalReplicableMarkerStatesComponent):
                self.__applyMarkerState(tunnelGO, self.__getPersonalTeleportState(tunnelGO))

    def __getPersonalTeleportState(self, go):
        teleportComponent = go.findComponentByType(TeleportReplicableComponent)
        if not teleportComponent:
            return TeleportMarkerStatesIDs.DEFAULT_TELEPORT
        attachedVehicleID = avatar_getter.getVehicleIDAttached()
        tunnelComponents = [ comp for _, comp in self.__getTunnelTeleports(teleportComponent.index) ]
        for comp in tunnelComponents:
            if self.__isVehicleTeleporting(comp, attachedVehicleID):
                return TeleportMarkerStatesIDs.TELEPORT_OCCUPIED

        for comp in tunnelComponents:
            if attachedVehicleID in comp.cooldownVehicleIDs:
                return TeleportMarkerStatesIDs.TELEPORT_COOLDOWN

        return TeleportMarkerStatesIDs.DEFAULT_TELEPORT

    def __getTunnelTeleports(self, index):
        query = CGF.Query(self.spaceID, (CGF.GameObject, TeleportReplicableComponent))
        return [ (go, comp) for go, comp in query if comp.index == index ]

    def __isVehicleTeleporting(self, comp, vehicleID):
        vehicleIDs = comp.teleportingVehicleIDs
        finishTimes = comp.teleportingFinishTimes
        for i, vid in enumerate(vehicleIDs):
            if vid == vehicleID and i < len(finishTimes) and not isclose(finishTimes[i], 0.0):
                return True

        return False

    @everyNTime(n=3 if isLowPreset() else 1)
    def __onMarkerProgressChanged(self, go, currentProgress, maxProgress):
        markerStateComponent = go.findComponentByType(PortalReplicableMarkerStatesComponent)
        if not markerStateComponent:
            _logger.error('Received progress update but no PortalReplicableMarkerStatesComponent found')
            return
        else:
            hasStartTime = not markerStateComponent.autoProgressStartTime < 0
            hasDuration = not markerStateComponent.autoProgressDuration < 0
            if hasStartTime or hasDuration:
                _logger.error('Received progress update for marker with auto progress')
                return
            if not markerStateComponent.activeMarkerComponent:
                return
            activeMarker = markerStateComponent.activeMarkerComponent
            if not activeMarker.hasProgressBar:
                _logger.error('Received progress update for marker without progressBar')
                return
            if activeMarker.hasTimerBoard:
                _logger.error('TimerBoard forbidden for explicit progress management. Use auto progress')
                return
            portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
            if portalAreaMarkersController:
                progress = float(currentProgress) / maxProgress * 100
                portalAreaMarkersController.onMarkerProgressUpdated(activeMarker, progress, None)
            return

    def __onMarkersInitialized(self, go):
        markerStatesComponent = go.findComponentByType(PortalReplicableMarkerStatesComponent)
        self.__onMarkerStateChanged(go, markerStatesComponent.markerID)

    @staticmethod
    def __invalidateMarkerState(markerStateComponent):
        markerStateComponent.activeMarkerComponent = None
        return


@registerPortalManager(CGF.DomainOption.DomainClient)
class PortalAreaMarkerManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, PortalAreaMarker, GenericComponents.TransformComponent)
    def onPortalAreaMarkerAdded(self, go, areaMarker, transform):
        _logger.debug('Added PortalAreaMarker on GO  %s', go.name)
        areaMarker.id = go.id
        hm = CGF.HierarchyManager(self.spaceID)
        parentGO = hm.getParent(go)
        if not parentGO:
            _logger.error('Marker must have parentGO')
            return
        parentTransform = parentGO.findComponentByType(GenericComponents.TransformComponent)
        portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            parentTranslation = parentTransform.worldTransform.translation
            markerOffset = transform.position
            portalAreaMarkersController.addMarkerToZone(areaMarker, parentTranslation + markerOffset)

    @onRemovedQuery(CGF.GameObject, PortalAreaMarker)
    def onPortalAreaMarkerRemoved(self, go, areaMarker):
        _logger.debug('Removed PortalAreaMarker from go  %s', go.name)
        portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            portalAreaMarkersController.removeMarkerFromZone(areaMarker)
