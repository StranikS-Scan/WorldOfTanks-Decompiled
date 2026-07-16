# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/influence_zones.py
import math
import CGF
import Math
import CombatSelectedArea
import math_utils
from typing import List
from battle_royale.abilities.area_abilities import AreaAbilityVisualizer
from cgf_components.marker_component import CombatMarker
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from helpers import dependency
from items import vehicles
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from InfluenceZone import InfluenceZone
else:

    class Vehicle(object):
        pass


    class InfluenceZone(object):
        pass


    class IBattleSessionProvider(object):
        pass


@registerComponent
class InfluenceZoneMultiVisualizer(object):
    editorTitle = 'Influence Zone Multi Visualizer'
    group = 'Abilities'
    domain = CGF.Domain.Client
    influencePrefab = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Influence prefab', annotations={'path': '*.prefab'})
    rotateFromCenter = ComponentProperty(type=CGF.PropertyType.Bool, value=False, editorName='Rotate from center')


class ZonePrefabLoader(object):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    ALLY_MARKER_POSTFIX = 'Ally'
    ENEMY_MARKER_POSTFIX = 'Enemy'

    def __init__(self, influenceZone, go):
        self.influenceZone = influenceZone
        self.go = go
        self.equipment = vehicles.g_cache.equipments()[influenceZone.equipmentID]
        self.__prefabGO = None
        self.__loadedPrefabPath = None
        return

    def activate(self):
        path = self.__getPrefabPath(self.equipment, self.influenceZone.team)
        self.__loadGameObject(path)
        self.__guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def deactivate(self):
        self.__guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData
        self.__removeGameObject()

    def __multipositionSpawn(self, rootUUID, spaceID, multivisualizer, influenceZone, equipment, _):
        for zonePosition in influenceZone.zonesPosition:
            localPosition = zonePosition - influenceZone.position
            if multivisualizer.rotateFromCenter:
                transform = math_utils.createRTMatrix((localPosition.yaw, 0, 0), localPosition)
            else:
                transform = math_utils.createTranslationMatrix(localPosition)

            def postloadSetup(objects, queue):
                root = objects[0]
                if queue.hasComponent(root, AreaAbilityVisualizer):
                    areaVisualizer = queue.component(root, AreaAbilityVisualizer)
                    areaVisualizer.radius = equipment.zoneRadius
                eqComponent = queue.createComponent(root, InfluenceZoneEquipmentComponent)
                eqComponent.setupEquipment(equipment)

            CGF.loadAndCreatePrefabWithParentUUID(multivisualizer.influencePrefab, spaceID, rootUUID, transform, postloadSetup)

    def __onUpdateObservedVehicleData(self, *args):
        if not self.equipment.usagePrefabEnemy or self.equipment.usagePrefab == self.equipment.usagePrefabEnemy:
            return
        path = self.__getPrefabPath(self.equipment, self.influenceZone.team)
        if path != self.__loadedPrefabPath:
            self.__removeGameObject()
            self.__loadGameObject(path)

    def __getPrefabPath(self, equipment, zoneTeamID):
        prefabPath = equipment.usagePrefab
        if equipment.usagePrefabEnemy and not self.__guiSessionProvider.getArenaDP().isAllyTeam(zoneTeamID):
            prefabPath = equipment.usagePrefabEnemy
        return prefabPath

    def __loadGameObject(self, prefabPath):

        def postloadSetup(objects, queue):
            root = objects[0]
            rootUUID = queue.gameObjectUuid(root)
            self.__prefabGO = queue.gameObject(root)
            eqComponent = queue.createComponent(root, InfluenceZoneEquipmentComponent)
            eqComponent.setupEquipment(self.equipment)
            transformComponent = queue.component(root, CGF.TransformComponent)
            hasMultiVisualizer = queue.hasComponent(root, InfluenceZoneMultiVisualizer)
            if transformComponent and not hasMultiVisualizer:
                zoneFloat = 0.1
                transformComponent.transform = math_utils.createSRTMatrix((self.equipment.radius, 1.0, self.equipment.radius), (0.0, 0.0, 0.0), (0.0, zoneFloat, 0.0))
            if hasMultiVisualizer:
                multiVisualizer = queue.component(root, InfluenceZoneMultiVisualizer)
                self.__multipositionSpawn(rootUUID, queue.spaceID, multiVisualizer, self.influenceZone, self.equipment, self.equipment.influenceZone.radius)
            if queue.hasComponent(root, CombatMarker):
                markerComponent = queue.component(root, CombatMarker)
                postfix = self.ENEMY_MARKER_POSTFIX
                if self.__guiSessionProvider.getArenaDP().isAllyTeam(self.influenceZone.team):
                    postfix = self.ALLY_MARKER_POSTFIX
                markerComponent.shape += postfix
                markerComponent.disappearanceRadius = self.equipment.radius + self.equipment.influenceZone.radius
            if queue.hasComponent(root, InfluenceZoneTerrainArea):
                terrainAreaComponent = queue.component(root, InfluenceZoneTerrainArea)
                terrainAreaComponent.dropOffset = self.influenceZone.dropOffset

        self.__loadedPrefabPath = prefabPath
        CGF.loadAndCreatePrefabWithParent(prefabPath, self.go, Math.Vector3(0, 0, 0), postloadSetup)

    def __removeGameObject(self):
        go = self.__prefabGO
        if go is not None and go.valid:
            CGF.removeGameObject(self.__prefabGO)
        self.__prefabGO = None
        return


@registerComponent
class InfluenceZoneTerrainArea(object):
    editorTitle = 'Influence Zone Terrain Area'
    group = 'Abilities'
    domain = CGF.Domain.Client
    fullZoneVisual = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Full Zone Visual', annotations={'path': '*.visual'})
    dropOffset = ComponentProperty(type=CGF.PropertyType.Float, value=1000.0, editorName='Drop Offset')

    def __init__(self):
        super(InfluenceZoneTerrainArea, self).__init__()
        self.fullZoneArea = None
        return


@registerComponent
class InfluenceZoneEquipmentComponent(object):
    editorTitle = 'Influence Zone Equipment'
    domain = CGF.Domain.Client
    userVisible = False
    radius = ComponentProperty(type=CGF.PropertyType.Float, value=0, editorName='Radius')
    zonesCount = ComponentProperty(type=CGF.PropertyType.Int, value=0, editorName='Zones Count')
    zoneRadius = ComponentProperty(type=CGF.PropertyType.Float, value=0, editorName='Zone Radius')

    def __init__(self):
        self.equipment = None
        return

    def setupEquipment(self, equipment):
        self.equipment = equipment
        self.radius = equipment.radius
        self.zonesCount = equipment.zonesCount
        self.zoneRadius = equipment.influenceZone.radius


class InfluenceZoneVisualizationSystem(CGF.System):
    CUT_OFF_ANGLE = math.radians(60)
    CUT_OFF_DISTANCE = 100
    InfluenceZoneActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(InfluenceZone))
    TerrainAreaActivated = CGF.ActivateReaction(CGF.ReactRw(InfluenceZoneTerrainArea), CGF.Ro(InfluenceZoneEquipmentComponent), CGF.Ro(CGF.TransformComponent))
    TerrainAreaDeactivated = CGF.DeactivateReaction(CGF.ReactRw(InfluenceZoneTerrainArea), CGF.Has(InfluenceZoneEquipmentComponent))
    ZonePrefabLoaderActivated = CGF.ActivateReaction(CGF.ReactRw(ZonePrefabLoader))
    ZonePrefabLoaderDeactivated = CGF.DeactivateReaction(CGF.ReactRw(ZonePrefabLoader))
    Reactions = CGF.Reactions(InfluenceZoneActivated, TerrainAreaActivated, TerrainAreaDeactivated, ZonePrefabLoaderActivated, ZonePrefabLoaderDeactivated)

    def update(self):
        for terrainArea in self.reaction(self.TerrainAreaDeactivated):
            self.terrainAreaDestroy(terrainArea)

        q = CGF.CommandQueue(self.gom)
        for go, influenceZone in self.reaction(self.InfluenceZoneActivated):
            self.onInfluenceZoneSpawn(influenceZone, go, q)

        for terrainArea, influenceZoneEquipment, transform in self.reaction(self.TerrainAreaActivated):
            self.terrainAreaInit(transform, influenceZoneEquipment, terrainArea)

        for zone in self.reaction(self.ZonePrefabLoaderDeactivated):
            zone.deactivate()

        for zone in self.reaction(self.ZonePrefabLoaderActivated):
            zone.activate()

    def onInfluenceZoneSpawn(self, influenceZone, go, queue):
        from battle_royale.abilities.dynamic_cache_loader import DynamicObjectsCacheLoader
        equipment = vehicles.g_cache.equipments()[influenceZone.equipmentID]
        if not equipment.usagePrefab:
            loader = DynamicObjectsCacheLoader(self.spaceID, influenceZone.equipmentID, influenceZone.zonesPosition, influenceZone.team)
            queue.assignComponent(go, loader)
            return
        zone = ZonePrefabLoader(CGF.ComponentLink(go, InfluenceZone), go)
        queue.assignComponent(go, zone)

    def terrainAreaInit(self, transform, influenceZoneEquipment, terrainArea):
        fullRadius = influenceZoneEquipment.radius + influenceZoneEquipment.zoneRadius
        terrainArea.fullZoneArea = CombatSelectedArea.CombatSelectedArea()
        terrainArea.fullZoneArea.setup(position=transform.worldPosition, direction=Math.Vector3(0, 0, 1), size=Math.Vector2(fullRadius * 2, fullRadius * 2), visualPath=terrainArea.fullZoneVisual, color=None, marker=None)
        terrainArea.fullZoneArea.area.setMaxHeight(transform.worldPosition.y + terrainArea.dropOffset)
        terrainArea.fullZoneArea.area.enableYCutOff(True)
        terrainArea.fullZoneArea.area.setCutOffDistance(self.CUT_OFF_DISTANCE)
        terrainArea.fullZoneArea.area.setCutOffAngle(self.CUT_OFF_ANGLE)
        return

    def terrainAreaDestroy(self, terrainArea):
        terrainArea.fullZoneArea.destroy()
        terrainArea.fullZoneArea = None
        return
