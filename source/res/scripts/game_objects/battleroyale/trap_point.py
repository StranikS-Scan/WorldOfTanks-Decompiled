# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/game_objects/battleroyale/trap_point.py
import Triggers
import Math
import BigWorld
import weakref
import NetworkComponents
from constants import IS_CLIENT
from debug_utils import LOG_DEBUG_DEV
from game_objects.battleroyale import TrapPoint
from functools import partial
from items import vehicles
from soft_exception import SoftException
if IS_CLIENT:
    from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
    from helpers import dependency
spaceID = None
g_areaOffset = Math.Vector3(0.0, -5000.0, 0.0)

def _getTrappointDescr():
    for eqItem in vehicles.g_cache.equipments().values():
        if eqItem.name == 'trappoint':
            return eqItem

    raise SoftException("Couldn't find Trappoint equipment! Trappoint is not initialized!!!")


_g_trapDescr = _getTrappointDescr()

def buildCommon(gameObject):
    trigger = gameObject.createComponent(Triggers.AreaTriggerComponent)
    radius = _g_trapDescr.radius
    gameObject.createComponent(Triggers.CylinderAreaComponent, g_areaOffset, radius, 10000)

    def zoneEnter(who, where):
        TrapPoint.onVehicleEnterTrap(_g_trapDescr, who, where)

    def zoneExit(who, where):
        TrapPoint.onVehicleExitTrap(who, where)

    trigger.addEnterReaction(zoneEnter)
    trigger.addExitReaction(zoneExit)


def buildClient(gameObject):
    networkEntity = gameObject.findComponentByType(NetworkComponents.NetworkEntity)
    team = networkEntity.implementation.data.get('team', -1)
    dynObjCache = dependency.instance(IBattleDynamicObjectsCache)
    trapPointEffects = dynObjCache.getConfig(BigWorld.player().arenaGuiType).getTrapPointEffect()
    effect = trapPointEffects.enemy if team != BigWorld.player().team else trapPointEffects.ally
    if effect is not None:

        def onResourceLoaded(gameObjectRef, effectP, resourceRefs):
            if effectP in resourceRefs.failedIDs:
                return
            else:
                gameObjectEntityRef = gameObjectRef()
                x = z = _g_trapDescr.radius
                y = _g_trapDescr.height
                scale = (x, y, z)
                if gameObjectEntityRef is not None:
                    from battleground.loot_object import SequenceComponent
                    sequenceComponent = gameObject.createComponent(SequenceComponent, resourceRefs[effectP])
                    sequenceComponent.createTerrainEffect(gameObjectEntityRef.position, scale=scale, loopCount=-1)
                return

        import AnimationSequence
        effectPath = effect.path
        BigWorld.loadResourceListBG((AnimationSequence.Loader(effectPath, BigWorld.player().spaceID),), partial(onResourceLoaded, weakref.ref(networkEntity.implementation), effectPath))
    else:
        LOG_DEBUG_DEV('Trap point: Effect name is not defined')
    return


def buildServer(gameObject):
    LOG_DEBUG_DEV('Trap point BUILD SERVER')
    timeTrigger = gameObject.createComponent(Triggers.TimeTriggerComponent, _g_trapDescr.timer)

    def onTimeToDeath(who):
        LOG_DEBUG_DEV('Trap point time to destroy')
        TrapPoint.killComponent(who)

    timeTrigger.addFireReaction(onTimeToDeath)
