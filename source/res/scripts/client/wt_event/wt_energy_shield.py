# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/wt_energy_shield.py
import logging
from functools import partial
import BigWorld
import Math
import AnimationSequence
import WtEffects
from gui.shared.utils.graphics import isRendererPipelineDeferred
from svarog_script.script_game_object import ScriptGameObject
from vehicle_systems.tankStructure import TankPartNames, ColliderTypes
from vehicle_systems.stricted_loading import makeCallbackWeak
from math_utils import createRTMatrix
from helpers import dependency, newFakeModel
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
_logger = logging.getLogger(__name__)
_shieldPartMap = {TankPartNames.TURRET: TankPartNames.TURRET,
 TankPartNames.GUN: TankPartNames.TURRET,
 TankPartNames.CHASSIS: TankPartNames.HULL,
 TankPartNames.HULL: TankPartNames.HULL}

class _ExplosionEffectObject(ScriptGameObject):

    def __init__(self, entityID, partName, transform, animator):
        super(_ExplosionEffectObject, self).__init__(BigWorld.player().spaceID)
        self.__fakeModel = None
        self.__entityID = entityID
        self.__partName = partName
        self.__transform = transform
        self.__fakeModel = newFakeModel()
        animator.bindTo(AnimationSequence.ModelWrapperContainer(self.__fakeModel, self.worldID))
        animator.loopCount = 1
        return

    def activate(self):
        vehicle = BigWorld.entities.get(self.__entityID)
        if vehicle is not None and vehicle.appearance is not None:
            node = vehicle.appearance.compoundModel.node(self.__partName)
            if node is not None:
                node.attach(self.__fakeModel, self.__transform)
        super(_ExplosionEffectObject, self).activate()
        return

    def deactivate(self):
        super(_ExplosionEffectObject, self).deactivate()
        if self.__fakeModel is not None and self.__fakeModel.attached:
            vehicle = BigWorld.entities.get(self.__entityID)
            if vehicle is not None and vehicle.appearance is not None:
                node = vehicle.appearance.compoundModel.node(self.__partName)
                if node is not None:
                    node.detach(self.__fakeModel)
        return

    def destroy(self):
        self.__fakeModel = None
        super(_ExplosionEffectObject, self).destroy()
        return


class WtEnergyShield(ScriptGameObject):
    __dybObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    modelData = property(lambda self: self.__additionalModelData())

    def __init__(self, worldID, entityID):
        super(WtEnergyShield, self).__init__(worldID)
        self._entityID = entityID

    def connect(self, appearance):
        appearance.collisions.connect(appearance.id, ColliderTypes.HANGAR_VEHICLE_COLLIDER, WtEnergyShieldConfig.bspCollisionData(appearance.compoundModel))

    def deactivate(self):
        for component in self._components:
            self.removeComponent(component)

        super(WtEnergyShield, self).deactivate()

    def destroy(self):
        if self._entityID is not None:
            vehicle = BigWorld.entities.get(self._entityID)
            if vehicle is not None and vehicle.appearance is not None:
                appearance = vehicle.appearance
                if appearance.collisions is not None:
                    appearance.collisions.removeAttachment(WtEnergyShieldConfig.partIndex(TankPartNames.TURRET))
                    appearance.collisions.removeAttachment(WtEnergyShieldConfig.partIndex(TankPartNames.HULL))
        super(WtEnergyShield, self).destroy()
        return

    def processHit(self, shotPoint):
        vehicle = BigWorld.entities.get(self._entityID)
        if vehicle is None or vehicle.appearance is None:
            return False
        collisions = vehicle.appearance.collisions
        if collisions is None:
            return False
        healthPercentMin = WtEnergyShieldConfig.shieldDescriptor().healthPercentage
        courrentPercentHealth = float(vehicle.health) / vehicle.typeDescriptor.maxHealth
        if courrentPercentHealth < healthPercentMin:
            return False
        partIndex = WtEnergyShieldConfig.partIndex(shotPoint.componentName)
        minBounds, maxBounds, _ = collisions.getBoundingBox(partIndex)
        collisionLength = max(abs(minBounds[0] - maxBounds[0]), abs(minBounds[1] - maxBounds[1]))
        shotMatrix = shotPoint.matrix
        isFakePart, shieldPartName = WtEnergyShieldConfig.isFakeShieldPart(shotPoint.componentName)
        if isFakePart:
            compound = vehicle.model
            nodeTransform = Math.Matrix(compound.node(shotPoint.componentName))
            shieldTransform = Math.Matrix(compound.node(shieldPartName))
            shieldTransform.invert()
            shotMatrix.postMultiply(nodeTransform)
            shotMatrix.postMultiply(shieldTransform)
        collisionData = collisions.collideLocalEx(partIndex, shotMatrix.applyPoint(Math.Vector3(0.0, 0.0, -collisionLength)), shotMatrix.applyPoint(Math.Vector3(0.0, 0.0, 0.1)))
        distance, position, normal, _ = collisionData
        if distance > 0.0:
            nodeTransform = Math.Matrix(vehicle.model.node(shotPoint.componentName))
            nodeTransform.invert()
            worldTransform = createRTMatrix(Math.Vector3(normal.yaw, normal.pitch, 0.0), position)
            worldTransform.postMultiply(nodeTransform)
            self.__addEffect(shotPoint.componentName, worldTransform)
            return True
        else:
            return False

    def __addEffect(self, partName, transform):
        shieldDescr = WtEnergyShieldConfig.shieldDescriptor()
        effectDescr = shieldDescr.hitEffect
        effectPath = effectDescr.path if isRendererPipelineDeferred() else effectDescr.path_fwd
        BigWorld.loadResourceListBG((AnimationSequence.Loader(effectPath, self.worldID),), makeCallbackWeak(self.__onEffectLoaded, partName, transform, effectPath))

    def __removeEffect(self, effObject):
        self.removeComponent(effObject)
        return True

    def __onEffectLoaded(self, partName, transform, resName, resourceRefs):
        if resName in resourceRefs.failedIDs:
            _logger.error('[WtES] resource loading is failed - %s', resName)
            return
        animator = resourceRefs[resName]
        handler = _ExplosionEffectObject(self._entityID, partName, transform, animator)
        handler.createComponent(WtEffects.SequenceTimer, animator, partial(self.__removeEffect, handler))
        self.addComponent(handler)


class WtEnergyShieldConfig(object):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __partMap = {TankPartNames.TURRET: TankPartNames.TURRET,
     TankPartNames.GUN: TankPartNames.TURRET,
     TankPartNames.CHASSIS: TankPartNames.HULL,
     TankPartNames.HULL: TankPartNames.HULL}

    @classmethod
    def hasEnergyShield(cls, appearance):
        return appearance.isAlive and 'event_boss' in appearance.typeDescriptor.type.tags

    @classmethod
    def bspModelNames(cls):
        shieldDescr = cls.shieldDescriptor()
        return ((cls.partIndex(TankPartNames.HULL), shieldDescr.bspModels.hull), (cls.partIndex(TankPartNames.TURRET), shieldDescr.bspModels.turret))

    @classmethod
    def bspCollisionData(cls, compoundModel):
        return ((cls.partIndex(TankPartNames.HULL), compoundModel.node(TankPartNames.HULL)), (cls.partIndex(TankPartNames.TURRET), compoundModel.node(TankPartNames.TURRET)))

    @classmethod
    def shieldDescriptor(cls):
        arenaGuiType = cls.__sessionProvider.arenaVisitor.getArenaGuiType()
        config = cls.__dynObjectsCache.getConfig(arenaGuiType)
        return config.energyShieldEffect if config is not None else None

    @classmethod
    def partIndex(cls, partName):
        return TankPartNames.getIdx(_shieldPartMap[partName]) + len(TankPartNames.ALL)

    @classmethod
    def isFakeShieldPart(cls, partName):
        shieldPart = _shieldPartMap[partName]
        return (shieldPart != partName, shieldPart)

    @classmethod
    def partName(cls, index):
        pass
