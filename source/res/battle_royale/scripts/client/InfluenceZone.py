# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/InfluenceZone.py
import logging
import NetworkComponents
import BigWorld
import Math
import CGF
import Vehicle
from helpers import dependency
from items import vehicles
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from AffectComponent import getInfluenceZoneType, getEffectConfig
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

def _getTrapOrRepairPointDescr(equipmentID):
    return vehicles.g_cache.equipments()[equipmentID].influenceZone


def _getPlayerVehicleImpl(who):
    playerEntityRef = who.findComponentByType(NetworkComponents.NetworkEntity)
    if playerEntityRef is None:
        return
    else:
        playerEntityImpl = playerEntityRef.implementation
        return None if not isinstance(playerEntityImpl, Vehicle.Vehicle) else playerEntityImpl


class InfluenceZone(BigWorld.Entity):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(InfluenceZone, self).__init__()
        self.__influenceZoneType = None
        return

    def onEnterWorld(self, prereqs):
        gameObject = CGF.GameObject(self.spaceID)
        self.gameObject = gameObject
        _logger.debug('onEnterWorld %s', self.id)
        pointDescr = _getTrapOrRepairPointDescr(self.equipmentID)
        self.__influenceZoneType = getInfluenceZoneType(pointDescr)
        dynObjCache = dependency.instance(IBattleDynamicObjectsCache)
        config = dynObjCache.getConfig(BigWorld.player().arenaGuiType)
        effectConfig = self.__get_effect_config(config)
        if effectConfig is not None:
            import AnimationSequence
            effectPath = effectConfig.path
            for position in self.zonesPosition:
                BigWorld.loadResourceListBG((AnimationSequence.Loader(effectPath, BigWorld.player().spaceID),), makeCallbackWeak(self.__onResourceLoaded, effectPath, position, effectConfig.scaleRatio, pointDescr))

        else:
            _logger.debug('Trap point: Effect name is not defined')
        self.gameObject.activate()
        return

    def onLeaveWorld(self):
        if self.gameObject is not None:
            self.gameObject.destroy()
        self.gameObject = None
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
            sequenceComponent = gameObject.createComponent(SequenceComponent, resourceRefs[effectP])
            yShift = -zoneDepth
            position = position + Math.Vector3(0, yShift, 0)
            sequenceComponent.createTerrainEffect(position, scale=scale, loopCount=-1)
            return

    def __get_effect_config(self, config):
        pointEffect = getEffectConfig(self.__influenceZoneType, config)
        return pointEffect.ally if self.guiSessionProvider.getArenaDP().isAllyTeam(self.team) else pointEffect.enemy
