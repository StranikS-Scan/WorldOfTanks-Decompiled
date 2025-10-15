# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/edge_drawer/managers.py
import CGF
import BigWorld
import GUI
from AvatarInputHandler import cameras
from EdgeDrawer import HighlightComponent
from HealthComponent import HealthComponent
from GenericComponents import TransformComponent
from cgf_script.managers_registrator import onProcessQuery, onAddedQuery, onRemovedQuery
from portal.gui.battle_control.controllers.portal_gui_controllers import getPortalBattleMarkersController
from portal_client_cgf.portal_2d_markers.components import PortalAreaMarker
from portal_common_cgf.portal_components import BossComponent
from portal_client_cgf.portal_components import BossHPMarkerComponent
from portal_common_cgf.portal_helpers import registerPortalManager
from portal_constants import PORTAL_BATTLE_CTRL_ID

@registerPortalManager(CGF.DomainOption.DomainClient)
class BossEdgeDrawer(CGF.ComponentManager):
    _ENEMY_COLOR = 1
    _COLLIDE_DISTANCE = 1500
    _EDGE_DRAWING_DISTANCE = 250

    def __init__(self):
        super(BossEdgeDrawer, self).__init__()
        BigWorld.enableEdgeDrawerVisual(True)

    @onAddedQuery(CGF.GameObject, BossComponent, HealthComponent)
    def onBossAdded(self, bossGO, bossComponent, healthComponent):
        healthComponent.onHealthChanged += self.__onHealthChanged

    @onAddedQuery(CGF.GameObject, BossHPMarkerComponent, PortalAreaMarker)
    def onBossHPMarkerAdded(self, markerGO, bossHPMarkerComponent, portalAreaMarker):
        hm = CGF.HierarchyManager(self.spaceID)
        bossGO = hm.getParent(markerGO)
        healthComponent = bossGO.findComponentByType(HealthComponent)
        if healthComponent is None:
            return
        else:
            portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
            portalAreaMarkersController.onMarkerProgressUpdated(portalAreaMarker, maxHP=healthComponent.maxHealth)
            return

    @onRemovedQuery(CGF.GameObject, BossComponent, HealthComponent)
    def onBossRemoved(self, bossGO, bossComponent, healthComponent):
        healthComponent.onHealthChanged -= self.__onHealthChanged

    @onProcessQuery(CGF.GameObject, BossComponent, TransformComponent, tickGroup='Simulation')
    def onTick(self, go, boss, transform):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if not vehicle:
            return
        elif vehicle.position.distTo(transform.position) >= self._EDGE_DRAWING_DISTANCE:
            self.removeHighlight(go)
            return
        else:
            gameObjectID = self.__getGameObjectUnderCrosshair()
            if gameObjectID is None:
                return
            targetIDs = self.__collectAllChildIDs(go)
            if gameObjectID in targetIDs:
                self.addHighlight(go)
            else:
                self.removeHighlight(go)
            return

    def addHighlight(self, go):
        highlighter = go.findComponentByType(HighlightComponent)
        if highlighter is None:
            go.createComponent(HighlightComponent, self._ENEMY_COLOR, 0, False, False)
        return

    def removeHighlight(self, go):
        highlighter = go.findComponentByType(HighlightComponent)
        if highlighter is not None:
            go.removeComponentByType(HighlightComponent)
        return

    def __onHealthChanged(self, oldHeath, currentHeath, maxHeath):
        query = CGF.Query(self.spaceID, (CGF.GameObject, BossHPMarkerComponent, PortalAreaMarker))
        for _, __, portalAreaMarker in query:
            portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
            portalAreaMarkersController.onMarkerProgressUpdated(portalAreaMarker, maxHP=maxHeath)
            portalAreaMarkersController.onMarkerProgressUpdated(portalAreaMarker, currentHP=currentHeath)

    def __getGameObjectUnderCrosshair(self):
        player = BigWorld.player()
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        res = BigWorld.collideDynamicStatic(player.spaceID, wpoint, wpoint + ray * self._COLLIDE_DISTANCE, 1, player.playerVehicleID, -1, 0)
        return res[5] if res is not None else None

    def __collectAllChildIDs(self, go):
        hm = CGF.HierarchyManager(self.spaceID)
        gameObjectIDs = [go.id]
        children = hm.getChildren(go)
        if children is not None:
            for child in children:
                gameObjectIDs.extend(self.__collectAllChildIDs(child))

        return gameObjectIDs
