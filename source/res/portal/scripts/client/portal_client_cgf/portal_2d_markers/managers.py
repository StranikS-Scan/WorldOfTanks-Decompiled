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
    def onPortalReplicableMarkerTick(self, _, markerStatesComponent):
        startTime = markerStatesComponent.autoProgressStartTime
        duration = markerStatesComponent.autoProgressDuration
        if bool(startTime) ^ bool(duration):
            _logger.error('There must be both start and end time for automatic progress')
            return
        elif startTime < 0 and duration < 0:
            return
        elif not markerStatesComponent.maxProgress < 0:
            _logger.warning('Setting maxProgress for automatic progress forbidden.')
            markerStatesComponent.maxProgress = -1
            return
        elif not markerStatesComponent.activeMarkerComponent:
            return
        else:
            activeMarker = markerStatesComponent.activeMarkerComponent
            if not activeMarker.hasProgressBar and not activeMarker.hasTimerBoard:
                _logger.error('There must be marker with progressBar or TimerBoard for automatic progress')
                return
            currentProgress = self.__calculateCurrentProgress(startTime, duration)
            restTime = int(startTime + duration - BigWorld.serverTime()) if activeMarker.hasTimerBoard else None
            portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
            if portalAreaMarkersController:
                portalAreaMarkersController.onMarkerProgressUpdated(activeMarker, currentProgress, restTime)
            return

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

    def __onMarkerStateChanged(self, go, state):
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
