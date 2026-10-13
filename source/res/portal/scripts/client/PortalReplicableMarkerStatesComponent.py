# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalReplicableMarkerStatesComponent.py
import Event
import CGF
import logging
from gui.battle_control import avatar_getter
from script_component.DynamicScriptComponent import DynamicScriptComponent
from portal_constants import PORTAL_FRONTIER_MARKERS
from TeleportReplicableComponent import TeleportReplicableComponent
from portal_common_cgf.portal_2d_markers.components import PortalReplicableMarkerStatesComponent as replicableMarkerStatesComponentBase
from portal_client_cgf.portal_2d_markers.components import PortalAreaMarker
_logger = logging.getLogger(__name__)

class PortalReplicableMarkerStatesComponent(DynamicScriptComponent, replicableMarkerStatesComponentBase):

    def __init__(self, *args, **kwargs):
        super(PortalReplicableMarkerStatesComponent, self).__init__(*args, **kwargs)
        self.__eventManager = Event.EventManager()
        self.onMarkerStateChanged = Event.SafeEvent(self.__eventManager)
        self.onMarkerProgressChanged = Event.SafeEvent(self.__eventManager)
        self.onMarkersInitialized = Event.SafeEvent(self.__eventManager)
        self.activeMarkerComponent = None
        return

    def onDestroy(self):
        self.__eventManager.clear()
        self.__eventManager = None
        TeleportReplicableComponent.onTeleportLinked -= self.__onTeleportLinked
        super(PortalReplicableMarkerStatesComponent, self).onDestroy()
        return

    @property
    def gameObject(self):
        return self.entity.entityGameObject

    def _onAvatarReady(self):
        TeleportReplicableComponent.onTeleportLinked += self.__onTeleportLinked

    def set_markerID(self, prev):
        self.onMarkerStateChanged(self.gameObject, self.markerID)

    def set_maxProgress(self, prev):
        self.onMarkerProgressChanged(self.gameObject, self.currentProgress, self.maxProgress)

    def set_currentProgress(self, prev):
        self.onMarkerProgressChanged(self.gameObject, self.currentProgress, self.maxProgress)

    def initTeleportTunnelMarkers(self, teleportGO, frontierName):
        hm = CGF.HierarchyManager(self.spaceID)
        markerGOQuery = hm.findComponentsInHierarchy(teleportGO, PortalAreaMarker)
        markerComponents = [ markerComp for _, markerComp in markerGOQuery ]
        frontierMarkers = getattr(PORTAL_FRONTIER_MARKERS, frontierName.upper())
        teleportMarkers = frontierMarkers['teleport']
        for markerComponent in markerComponents:
            markerComponent.marker2DEntryID = teleportMarkers['markers2d'][markerComponent.stateID]
            markerComponent.markerMinimapEntryID = teleportMarkers['markersMinimap'][markerComponent.stateID]

        self.onMarkersInitialized(teleportGO)

    def initCampMarkers(self, campGO, markerComponents):
        campName = campGO.name
        battleState = avatar_getter.getArenaInfo().portalBattleStateComponent
        frontierName = battleState.getCampFrontier(campName)
        if not frontierName:
            _logger.error('There is no campFrontier in config! %s', campName)
            return
        frontierMarkers = getattr(PORTAL_FRONTIER_MARKERS, frontierName.upper())
        campMarkers = frontierMarkers['camp']
        for markerComponent in markerComponents:
            markerComponent.marker2DEntryID = campMarkers['markers2d'][markerComponent.stateID]
            markerComponent.markerMinimapEntryID = campMarkers['markersMinimap'][markerComponent.stateID]

        self.onMarkersInitialized(campGO)

    def __onTeleportLinked(self, teleportGO):
        if not self.gameObject or teleportGO.id != self.gameObject.id:
            return
        else:
            sourceComponent = teleportGO.findComponentByType(TeleportReplicableComponent)
            index = sourceComponent.index
            teleports = CGF.Query(self.spaceID, (CGF.GameObject, TeleportReplicableComponent)).values()
            linkedTeleports = [ teleportGO for teleportGO, component in teleports if component.index == index ]
            if len(linkedTeleports) != 2:
                return
            battleState = avatar_getter.getArenaInfo().portalBattleStateComponent
            frontierName = None
            for teleport in linkedTeleports:
                frontierName = battleState.getTeleportFrontier(teleport.name)
                if frontierName:
                    break

            for teleport in linkedTeleports:
                markersComponent = teleport.findComponentByType(PortalReplicableMarkerStatesComponent)
                markersComponent.initTeleportTunnelMarkers(teleport, frontierName)

            return
