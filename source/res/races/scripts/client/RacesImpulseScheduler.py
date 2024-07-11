# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/RacesImpulseScheduler.py
import logging
from functools import partial
import BigWorld
import Math
import CGF
from typing import TYPE_CHECKING
import races_prefabs
from cosmic_sound import CosmicBattleSounds
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from script_component.DynamicScriptComponent import DynamicScriptComponent
if TYPE_CHECKING:
    from typing import Optional
    from Vehicle import Vehicle
    from cgf_obsolete_script.script_game_object import ScriptGameObject
_logger = logging.getLogger(__name__)

class _BaseEffectComponent(object):

    def __init__(self, entity, prefab):
        self.__entity = entity
        self.__prefab = prefab
        _logger.debug('%s: init entity[%s], prefab[%s]', self.__class__.__name__, entity.id, prefab)

    def _createVisual(self, translation=None):
        parent = self.__entity.entityGameObject
        _logger.debug('BaseEffectComponent: creating new visual. entity[%s], translation[%s]', self.__entity.id, translation)
        CGF.loadGameObjectIntoHierarchy(self.__prefab, parent, translation or Math.Vector3(), self._prefabLoaded)

    def _prefabLoaded(self, gameObject):
        pass


class _CollisionEffectComponent(_BaseEffectComponent):

    def __init__(self, entity, prefab):
        super(_CollisionEffectComponent, self).__init__(entity, prefab)
        self._gameObjects = set()

    def _prefabLoaded(self, gameObject):
        _logger.debug('CollisionEffectComponent: prefabLoaded')
        self._gameObjects.add(gameObject)
        gameObject.activate()
        BigWorld.callback(1.0, partial(self._remove, gameObject))

    def _remove(self, gameObject):
        _logger.debug('CollisionEffectComponent: removing gameObject %s. All gameObjects %s', gameObject, self._gameObjects)
        if gameObject not in self._gameObjects:
            return
        self._gameObjects.remove(gameObject)
        CGF.removeGameObject(gameObject)

    def add(self, point):
        _logger.debug('CollisionEffectComponent: add gameObject at point[%s].', point)
        self._createVisual(point)

    def clear(self):
        _logger.debug('CollisionEffectComponent: clearing up gameObjects: %s', self._gameObjects)
        for gameObject in self._gameObjects:
            CGF.removeGameObject(gameObject)

        self._gameObjects.clear()


class _ShieldEffectComponent(_BaseEffectComponent):

    def __init__(self, entity, prefab):
        super(_ShieldEffectComponent, self).__init__(entity, prefab)
        self._gameObject = None
        return

    def _prefabLoaded(self, gameObject):
        _logger.debug('ShieldEffectComponent: prefabLoaded')
        self._gameObject = gameObject
        self.__activateGameObject()

    def activate(self):
        _logger.debug('ShieldEffectComponent: activating shield effect.')
        if self._gameObject is None:
            self._createVisual()
        else:
            self.__activateGameObject()
        return

    def clear(self):
        _logger.debug('ShieldEffectComponent: clearing up gameObject: %s', self._gameObject)
        if self._gameObject is not None:
            CGF.removeGameObject(self._gameObject)
        self._gameObject = None
        return

    def __activateGameObject(self):
        _logger.debug('ShieldEffectComponent: activating gameObject: %s', self._gameObject)
        if self._gameObject:
            self._gameObject.deactivate()
            self._gameObject.activate()


class RacesImpulseScheduler(DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, *_, **__):
        super(RacesImpulseScheduler, self).__init__(*_, **__)
        self.__rammingFieldComponent = _ShieldEffectComponent(self.entity, races_prefabs.Vehicle.RAMMING_FIELD)
        self.__collisionComponent = _CollisionEffectComponent(self.entity, races_prefabs.Vehicle.COLLISION_EFFECT)

    def onDestroy(self):
        self.__rammingFieldComponent.clear()
        self.__collisionComponent.clear()
        super(RacesImpulseScheduler, self).onDestroy()

    def set_impactPoint(self, oldValue):
        _logger.debug('set_impactpoint: impactPoint=%s', self.impactPoint)
        impactPoint = self.impactPoint
        localPoint = self._getLocalImpactPoint(impactPoint)
        self.__collisionComponent.add(localPoint)
        CosmicBattleSounds.playRammingSound(self.entity.position)

    def onCollision(self):
        _logger.debug('onCollision - showing shield collision effect for vehicle[%d].', self.entity.id)
        self.__rammingFieldComponent.activate()

    def _getLocalImpactPoint(self, globalPoint):
        mi = Math.Matrix(self.entity.matrix)
        mi.invert()
        return mi.applyPoint(globalPoint)
