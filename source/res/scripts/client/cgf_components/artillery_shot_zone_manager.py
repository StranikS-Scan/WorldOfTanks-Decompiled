# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/artillery_shot_zone_manager.py
import BigWorld
import CGF
import Math
from constants import ArtilleryZoneType
from cgf_script.managers_registrator import autoregister
from GenericComponents import TerrainSelectedAreaComponent, TransformComponent
zoneTypes = {ArtilleryZoneType.EXPLOSION: 'content/Interface/CheckPoint/shot_zone_explosion_rework.visual',
 ArtilleryZoneType.SHOT: 'content/Interface/CheckPoint/shot_zone_shot_rework.visual',
 ArtilleryZoneType.FRIENDLY: 'content/Interface/CheckPoint/shot_zone_friendly_rework.visual'}

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ArtilleryShotZoneManager(CGF.ComponentManager):

    def __init__(self):
        super(ArtilleryShotZoneManager, self).__init__()
        self.__activeZones = {}

    def addArtilleryShotZone(self, shotId, pos, radius, zoneType=ArtilleryZoneType.SHOT):
        go = CGF.GameObject(BigWorld.player().spaceID, 'ShotZone')
        go.createComponent(TransformComponent, pos)
        go.createComponent(TerrainSelectedAreaComponent, zoneTypes[zoneType], Math.Vector2(2 * radius, 2 * radius), 0.2, 4294967295L)
        go.activate()
        self.__activeZones[shotId] = go

    def removeArtilleryShotZone(self, shotId):
        if shotId in self.__activeZones:
            go = self.__activeZones[shotId]
            CGF.removeGameObject(go)
            del self.__activeZones[shotId]
