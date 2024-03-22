# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/dynamic_cache_loader.py
import logging
import BigWorld
import NetworkComponents
import Math
import CGF
import ResMgr
from constants import IS_CLIENT
from helpers import dependency
from helpers.EffectsList import effectsFromSection
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.stricted_loading import makeCallbackWeak
import GenericComponents
from items import vehicles
if IS_CLIENT:
    import Vehicle
else:

    class Vehicle(object):
        pass


_logger = logging.getLogger(__name__)

def _getTrapOrRepairPointDescr(equipmentID):
    print vehicles.g_cache.equipments()
    return vehicles.g_cache.equipments()[equipmentID].influenceZone


def _getPlayerVehicleImpl(who):
    playerEntityRef = who.findComponentByType(NetworkComponents.NetworkEntity)
    if playerEntityRef is None:
        return
    else:
        playerEntityImpl = playerEntityRef.implementation
        return None if not isinstance(playerEntityImpl, Vehicle.Vehicle) else playerEntityImpl


class DynamicObjectsCacheLoader(object):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, spaceID, equipmentID, zonesPosition, team):
        self.spaceID = spaceID
        self.equipmentID = equipmentID
        self.zonesPosition = zonesPosition
        self.team = team
        self.__influenceZoneType = None
        self.fireIDs = []
        return

    def activate(self):
        gameObject = CGF.GameObject(self.spaceID)
        self.gameObject = gameObject
        pointDescr = _getTrapOrRepairPointDescr(self.equipmentID)
        from AffectComponent import getInfluenceZoneType
        self.__influenceZoneType = getInfluenceZoneType(pointDescr)
        dynObjCache = dependency.instance(IBattleDynamicObjectsCache)
        config = dynObjCache.getConfig(BigWorld.player().arenaGuiType)
        effectConfig = self.__getEffectConfig(config)
        if effectConfig is not None:
            import AnimationSequence
            effectPath = effectConfig.path
            if pointDescr.fireEffectName:
                player = BigWorld.player()
                if player is None:
                    return
                environmentEffectsConfigFile = 'scripts/dynamic_objects.xml'
                settingsData = ResMgr.openSection(environmentEffectsConfigFile + '/' + pointDescr.fireEffectName)
                if settingsData is None:
                    return
                fireEffect = effectsFromSection(settingsData)
                firePoints = []
                firePoints.extend(self.zonesPosition)
                for position in firePoints:
                    self.fireIDs.append(player.terrainEffects.addNew(position, fireEffect.effectsList, fireEffect.keyPoints, None))

            for position in self.zonesPosition:
                BigWorld.loadResourceListBG((AnimationSequence.Loader(effectPath, BigWorld.player().spaceID),), makeCallbackWeak(self.__onResourceLoaded, effectPath, position, effectConfig.scaleRatio, pointDescr))

        else:
            _logger.debug('Trap point: Effect name is not defined')
        self.gameObject.activate()
        self.guiSessionProvider.onUpdateObservedVehicleData += self._onUpdateObservedVehicleData
        return

    def deactivate(self):
        self.guiSessionProvider.onUpdateObservedVehicleData -= self._onUpdateObservedVehicleData
        if self.gameObject is not None:
            self.gameObject.destroy()
        self.gameObject = None
        player = BigWorld.player()
        for id_ in self.fireIDs:
            player.terrainEffects.stop(id_)

        return

    def __onResourceLoaded(self, effectP, position, scaleRatio, pointDescr, resourceRefs):
        if effectP in resourceRefs.failedIDs:
            return
        else:
            gameObject = self.gameObject
            if gameObject is None:
                return
            x = z = pointDescr.radius
            if scaleRatio:
                y = x / scaleRatio
                zoneHeight = y * pointDescr.height / (pointDescr.height + pointDescr.depth)
                zoneDepth = y - zoneHeight
            else:
                zoneHeight = pointDescr.height
                zoneDepth = pointDescr.depth
            scale = (x, zoneHeight + zoneDepth, z)
            from battleground.components import SequenceComponent
            yShift = -zoneDepth
            position = position + Math.Vector3(0, yShift, 0)
            g = CGF.GameObject(self.spaceID)
            g.createComponent(GenericComponents.TransformComponent, position)
            g.createComponent(GenericComponents.HierarchyComponent, self.gameObject)
            sequenceComponent = g.createComponent(SequenceComponent, resourceRefs[effectP])
            sequenceComponent.createTerrainEffect(position, scale=scale, loopCount=-1)
            g.activate()
            g.transferOwnershipToWorld()
            return

    def __getEffectConfig(self, config):
        from AffectComponent import getEffectConfig
        pointEffect = getEffectConfig(self.__influenceZoneType, config)
        if not pointEffect:
            return None
        else:
            return pointEffect.ally if self.guiSessionProvider.getArenaDP().isAllyTeam(self.team) else pointEffect.enemy

    def _onUpdateObservedVehicleData(self, vehicleID, *args):
        self.deactivate()
        self.activate()
