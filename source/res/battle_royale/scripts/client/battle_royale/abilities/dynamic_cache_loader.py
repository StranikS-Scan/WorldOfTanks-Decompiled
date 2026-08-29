# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/dynamic_cache_loader.py
from __future__ import absolute_import, division
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
from items import vehicles
if IS_CLIENT:
    import Vehicle
else:

    class Vehicle(object):
        pass


_logger = logging.getLogger(__name__)

def _getTrapOrRepairPointDescr(equipmentID):
    _logger.info(vehicles.g_cache.equipments())
    return vehicles.g_cache.equipments()[equipmentID].influenceZone


def _getPlayerVehicleImpl(who):
    playerEntityRef = who.findRead(NetworkComponents.NetworkEntity)
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
        self.__visual = None
        self.fireIDs = []
        return

    def activate(self):
        queue = CGF.CommandQueue(self.spaceID)
        self.gameObject = queue.createGameObject()
        queue.createComponent(self.gameObject, CGF.HierarchyComponent)
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
        queue.activateGameObject(self.gameObject)
        self.guiSessionProvider.onUpdateObservedVehicleData += self._onUpdateObservedVehicleData
        return

    def deactivate(self):
        self.guiSessionProvider.onUpdateObservedVehicleData -= self._onUpdateObservedVehicleData
        if self.__visual is not None:
            CGF.removeGameObject(self.__visual)
            self.__visual = None
        if self.gameObject is not None:
            self.gameObject.destroy()
        self.gameObject = None
        player = BigWorld.player()
        if player is not None:
            for id_ in self.fireIDs:
                player.terrainEffects.stop(id_)

        del self.fireIDs[:]
        return

    def __onResourceLoaded(self, effectP, position, scaleRatio, pointDescr, resourceRefs):
        if effectP in resourceRefs.failedIDs:
            return
        elif self.gameObject is None:
            return
        else:
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
            queue = CGF.CommandQueue(self.spaceID)
            self.__visual = g = queue.createGameObject()
            queue.createComponent(g, CGF.TransformComponent, position)
            queue.createComponent(g, CGF.HierarchyComponent, self.gameObject)
            sequenceComponent = queue.assignComponent(g, SequenceComponent(resourceRefs[effectP]))
            sequenceComponent.createTerrainEffect(position, scale=scale, loopCount=-1)
            queue.activateGameObject(g)
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


class DynamicObjectsCacheLoaderSystem(CGF.System):
    DynamicObjectsCacheActivated = CGF.ActivateReaction(CGF.ReactRw(DynamicObjectsCacheLoader))
    DynamicObjectsCacheDeactivated = CGF.DeactivateReaction(CGF.ReactRw(DynamicObjectsCacheLoader))
    Reactions = CGF.Reactions(DynamicObjectsCacheActivated, DynamicObjectsCacheDeactivated)

    def update(self):
        for loader in self.reaction(self.DynamicObjectsCacheDeactivated):
            loader.deactivate()

        for loader in self.reaction(self.DynamicObjectsCacheActivated):
            loader.activate()
