# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/wt_impulse_visual.py
from functools import partial
import AnimationSequence
import BigWorld
import Math
import SoundGroups
import WtEffects
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from helpers import dependency, newFakeModel
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.script_game_object import ScriptGameObject
import math_utils

class _TemporaryAnimatorObject(ScriptGameObject):
    _DEFAULT_SEQUENCE_TIME = 1.0
    _DEFAULT_SEQUENCE_RADIUS = 1.0

    def __init__(self, worldID, entityID, radius, preparingTime, modelAnimator):
        super(_TemporaryAnimatorObject, self).__init__(worldID)
        self.__entityID = entityID
        self.__scale = radius / self._DEFAULT_SEQUENCE_RADIUS
        self.__preparingTime = preparingTime
        self.__model = newFakeModel()
        modelAnimator.bindTo(AnimationSequence.ModelWrapperContainer(self.__model, self.worldID))
        modelAnimator.loopCount = 1.0
        modelAnimator.speed = self._DEFAULT_SEQUENCE_TIME / preparingTime

    def activate(self):
        entity = BigWorld.entities.get(self.__entityID)
        if entity is not None:
            node = entity.model.node('')
            if node is not None:
                transform = math_utils.createSRTMatrix(Math.Vector3(self.__scale, self.__scale, self.__scale), Math.Vector3(), Math.Vector3())
                node.attach(self.__model, transform)
        super(_TemporaryAnimatorObject, self).activate()
        return

    def deactivate(self):
        if self.__model is not None and self.__model.attached:
            entity = BigWorld.entities.get(self.__entityID)
            if entity is not None:
                node = entity.model.node('')
                if node is not None:
                    node.detach(self.__model)
        super(_TemporaryAnimatorObject, self).deactivate()
        return

    def destroy(self):
        self.__model = None
        super(_TemporaryAnimatorObject, self).destroy()
        return


class ImpulseVisualObject(ScriptGameObject):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _EXPLOSION_TIME = 1.0

    def __init__(self, worldID, vehicleProxy, equipment, modelAnimators):
        super(ImpulseVisualObject, self).__init__(worldID)
        self.__modelAnimators = modelAnimators
        self.__vProxy = vehicleProxy
        self.__equipment = equipment

    def activate(self):
        if self.__startPreparing():
            super(ImpulseVisualObject, self).activate()

    def deactivate(self):
        for component in self._components:
            self.removeComponent(component)

        super(ImpulseVisualObject, self).deactivate()

    def destroy(self):
        self.__modelAnimators = None
        self.__equipment = None
        super(ImpulseVisualObject, self).destroy()
        return

    def __startPreparing(self):
        if self.__vProxy is not None and self.__vProxy.isAlive():
            effectDescr = self.wtImpulseDescriptor()
            if effectDescr is None:
                return False
            effectPath = effectDescr.onStart.stunEffect.path
            if effectPath not in self.__modelAnimators.failedIDs:
                animator = self.__modelAnimators.pop(effectPath)
                scale = self.__equipment.stunRadius
                preparingTime = self.__equipment.prepareSeconds
                self.__createSequenceComponent(animator, scale, preparingTime, self.__onEndPreparing)
                vehicle = BigWorld.player().vehicle
                if vehicle is not None and VEHICLE_EVENT_TYPE.EVENT_HUNTER in vehicle.typeDescriptor.type.tags:
                    if self.__vProxy.position.distSqrTo(vehicle.position) <= scale ** 2:
                        BigWorld.player().soundNotifications.play('ev_wt_t55a_vo_ability_emp')
                if BigWorld.player().playerVehicleID == self.__vProxy.id:
                    SoundGroups.g_instance.playSoundPos('ev_white_tiger_gameplay_wt_emi_pc', self.__vProxy.position)
                else:
                    SoundGroups.g_instance.playSoundPos('ev_white_tiger_gameplay_wt_emi_npc', self.__vProxy.position)
                return True
        return False

    def __onEndPreparing(self, wrapper):
        self.removeComponent(wrapper)
        self.__startExplosion()
        return True

    def __startExplosion(self):
        if self.__vProxy is None:
            return
        else:
            effectDescr = self.wtImpulseDescriptor()
            if effectDescr is None:
                return
            explosionDescr = effectDescr.onEnd
            self.__startExplosionComponent(explosionDescr.stunEffect.path, self.__equipment.stunRadius, self._EXPLOSION_TIME)
            self.__startExplosionComponent(explosionDescr.damageEffect.path, self.__equipment.damageRadius, self._EXPLOSION_TIME)
            return

    def __startExplosionComponent(self, path, scale, preparingTime):
        if path not in self.__modelAnimators.failedIDs:
            animator = self.__modelAnimators.pop(path)
            self.__createSequenceComponent(animator, scale, preparingTime, self.__onEndExplosion)

    def __onEndExplosion(self, wrapper):
        self.removeComponent(wrapper)
        if not self._components and self.__vProxy is not None:
            self.__vProxy.appearance.removeComponent(self)
        return True

    def __createSequenceComponent(self, modelAnimator, scale, preparingTime, doneCallback):
        wrapper = _TemporaryAnimatorObject(self.worldID, self.__vProxy.id, scale, preparingTime, modelAnimator)
        wrapper.createComponent(WtEffects.SequenceTimer, modelAnimator, partial(doneCallback, wrapper))
        self.addComponent(wrapper)

    @classmethod
    def wtImpulseDescriptor(cls):
        arenaGuiType = cls.__sessionProvider.arenaVisitor.getArenaGuiType()
        return cls.__dynObjectsCache.getConfig(arenaGuiType).impulseEffect
