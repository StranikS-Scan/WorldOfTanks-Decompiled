# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/influence_zones.py
import math
import CGF
import Math
import GenericComponents
import CombatSelectedArea
import math_utils
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battle_royale.abilities.area_abilities import AreaAbilityVisualizer
from cgf_components.marker_component import CombatMarker
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
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
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    influencePrefab = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Influence prefab', annotations={'path': '*.prefab'})
    rotateFromCenter = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Rotate from center')


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

    def __multipositionSpawn(self, go, multivisualizer, influenceZone, equipment, radius):
        for zonePosition in influenceZone.zonesPosition:
            localPosition = zonePosition - influenceZone.position
            if multivisualizer.rotateFromCenter:
                transform = math_utils.createRTMatrix((localPosition.yaw, 0, 0), localPosition)
            else:
                transform = math_utils.createTranslationMatrix(localPosition)

            def postloadSetup(go):
                areaVisualizer = go.findComponentByType(AreaAbilityVisualizer)
                if areaVisualizer is not None:
                    areaVisualizer.radius = equipment.zoneRadius
                eqComponent = go.createComponent(InfluenceZoneEquipmentComponent)
                eqComponent.setupEquipment(equipment)
                return

            CGF.loadGameObjectIntoHierarchy(multivisualizer.influencePrefab, go, transform, postloadSetup)

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

        def postloadSetup(go):
            self.__prefabGO = go
            eqComponent = go.createComponent(InfluenceZoneEquipmentComponent)
            eqComponent.setupEquipment(self.equipment)
            transformComponent = go.findComponentByType(GenericComponents.TransformComponent)
            multiVisualizer = go.findComponentByType(InfluenceZoneMultiVisualizer)
            if transformComponent and not multiVisualizer:
                zoneFloat = 0.1
                transformComponent.transform = math_utils.createSRTMatrix((self.equipment.radius, 1.0, self.equipment.radius), (0.0, 0.0, 0.0), (0.0, zoneFloat, 0.0))
            if multiVisualizer is not None:
                self.__multipositionSpawn(go, multiVisualizer, self.influenceZone, self.equipment, self.equipment.influenceZone.radius)
            markerComponent = go.findComponentByType(CombatMarker)
            if markerComponent is not None:
                postfix = self.ENEMY_MARKER_POSTFIX
                if self.__guiSessionProvider.getArenaDP().isAllyTeam(self.influenceZone.team):
                    postfix = self.ALLY_MARKER_POSTFIX
                markerComponent.shape += postfix
                markerComponent.disappearanceRadius = self.equipment.radius + self.equipment.influenceZone.radius
            terrainAreaComponent = go.findComponentByType(InfluenceZoneTerrainArea)
            if terrainAreaComponent is not None:
                terrainAreaComponent.dropOffset = self.influenceZone.dropOffset
            return

        self.__loadedPrefabPath = prefabPath
        CGF.loadGameObjectIntoHierarchy(prefabPath, self.go, Math.Vector3(0, 0, 0), postloadSetup)
        self.__guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def __removeGameObject(self):
        go = self.__prefabGO
        if go is not None and go.isValid():
            CGF.removeGameObject(self.__prefabGO)
        self.__prefabGO = None
        return


@registerComponent
class InfluenceZoneTerrainArea(object):
    editorTitle = 'Influence Zone Terrain Area'
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    fullZoneVisual = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Full Zone Visual', annotations={'path': '*.visual'})
    dropOffset = ComponentProperty(type=CGFMetaTypes.FLOAT, value=1000.0, editorName='Drop Offset')

    def __init__(self):
        super(InfluenceZoneTerrainArea, self).__init__()
        self.fullZoneArea = None
        return


@registerComponent
class InfluenceZoneEquipmentComponent(object):
    editorTitle = 'Influence Zone Equipment'
    domain = CGF.DomainOption.DomainClient
    userVisible = False
    radius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0, editorName='Radius')
    zonesCount = ComponentProperty(type=CGFMetaTypes.INT, value=0, editorName='Zones Count')
    zoneRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0, editorName='Zone Radius')

    def __init__(self):
        self.equipment = None
        return

    def setupEquipment(self, equipment):
        self.equipment = equipment
        self.radius = equipment.radius
        self.zonesCount = equipment.zonesCount
        self.zoneRadius = equipment.influenceZone.radius


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class InfluenceZoneVisualizationManager(CGF.ComponentManager):
    CUT_OFF_ANGLE = math.radians(60)
    CUT_OFF_DISTANCE = 100

    @onAddedQuery(InfluenceZone, CGF.GameObject)
    def onInfluenceZoneSpawn(self, influenceZone, go):
        from battle_royale.abilities.dynamic_cache_loader import DynamicObjectsCacheLoader
        equipment = vehicles.g_cache.equipments()[influenceZone.equipmentID]
        if not equipment.usagePrefab:
            go.createComponent(DynamicObjectsCacheLoader, self.spaceID, influenceZone.equipmentID, influenceZone.zonesPosition, influenceZone.team)
            return
        go.createComponent(ZonePrefabLoader, influenceZone, go)

    @onAddedQuery(GenericComponents.TransformComponent, InfluenceZoneEquipmentComponent, InfluenceZoneTerrainArea)
    def terrainAreaInit(self, transform, influenceZoneEquipment, terrainArea):
        fullRadius = influenceZoneEquipment.radius + influenceZoneEquipment.zoneRadius
        terrainArea.fullZoneArea = CombatSelectedArea.CombatSelectedArea()
        terrainArea.fullZoneArea.setup(position=transform.worldPosition, direction=Math.Vector3(0, 0, 1), size=Math.Vector2(fullRadius * 2, fullRadius * 2), visualPath=terrainArea.fullZoneVisual, color=None, marker=None)
        terrainArea.fullZoneArea.area.setMaxHeight(transform.worldPosition.y + terrainArea.dropOffset)
        terrainArea.fullZoneArea.area.enableYCutOff(True)
        terrainArea.fullZoneArea.area.setCutOffDistance(self.CUT_OFF_DISTANCE)
        terrainArea.fullZoneArea.area.setCutOffAngle(self.CUT_OFF_ANGLE)
        return

    @onRemovedQuery(InfluenceZoneEquipmentComponent, InfluenceZoneTerrainArea)
    def terrainAreaDestroy(self, influenceZoneEquipment, terrainArea):
        terrainArea.fullZoneArea.destroy()
        terrainArea.fullZoneArea = None
        return
