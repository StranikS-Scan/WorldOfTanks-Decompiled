# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleFrozenMantle.py
import logging
import GenericComponents
import BigWorld
import CGF
import Math
import math_utils
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from Event import EventsSubscriber
_logger = logging.getLogger(__name__)

class _Effect(object):
    _dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, parent, vehicle, radius):
        self._parent = parent
        self._vehicle = vehicle
        self._prefab = None
        self.__destroyed = False
        self._radius = radius
        return

    def start(self):
        self._load()

    def destroy(self):
        if self._prefab is not None:
            if self._prefab.isValid():
                CGF.removeGameObject(self._prefab)
            self._prefab = None
        self._parent = None
        self._vehicle = None
        self.__destroyed = True
        return

    def _load(self):
        path = self._getPath()
        parent = self._getParent()
        position = self._getPosition()
        CGF.loadGameObjectIntoHierarchy(path, parent, position, self._onLoaded)

    def _onLoaded(self, prefab):
        if not self.__destroyed:
            self._prefab = prefab
            self._updateRadius()
            self._prefab.activate()
        else:
            CGF.removeGameObject(prefab)

    def _getPath(self):
        isAlly = self._vehicle.guiSessionProvider.getArenaDP().isAllyTeam(self._vehicle.publicInfo['team'])
        return self._getDynObjectsCacheConfig().getFriendPrefab() if isAlly else self._getDynObjectsCacheConfig().getEnemyPrefab()

    def _getParent(self):
        return self._parent

    def _getPosition(self):
        return Math.Vector3()

    def _getDynObjectsCacheConfig(self):
        arenaGuiType = self._vehicle.guiSessionProvider.arenaVisitor.getArenaGuiType()
        return self._dynObjectsCache.getConfig(arenaGuiType)

    def _updateRadius(self):
        if self._prefab is None:
            _logger.error('Failed to update Effect radius. Missing prefab.')
            return
        else:
            terrainSelectedArea = self._prefab.findComponentByType(GenericComponents.TerrainSelectedAreaComponent)
            if terrainSelectedArea is None:
                _logger.error('Failed to update Effect radius. Missing TerrainSelectedArea component.')
                return
            terrainSelectedArea.size = Math.Vector2(self._radius * 2, self._radius * 2)
            transformComponent = self._prefab.findComponentByType(GenericComponents.TransformComponent)
            if transformComponent is None:
                _logger.error('Failed to update Effect radius. Missing TransformComponent component.')
                return
            transformComponent.transform = math_utils.createSRTMatrix(Math.Vector3(self._radius, 1.0, self._radius), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
            return


class HWVehicleFrozenMantle(BigWorld.DynamicScriptComponent):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self):
        super(HWVehicleFrozenMantle, self).__init__()
        self._es = EventsSubscriber()
        self._es.subscribeToEvent(self.entity.onAppearanceReady, self._onAppearanceReady)
        self.__effect = None
        self.__isShowed = False
        self.__showZone()
        return

    def onDestroy(self):
        if self._es is not None:
            self._es.unsubscribeFromAllEvents()
            self._es = None
        if self.__effect is not None:
            self.__effect.destroy()
            self.__effect = None
        self.__isShowed = False
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def set_radius(self, prev):
        self.__showZone()

    def _onAppearanceReady(self):
        appearance = self.entity.appearance
        if appearance is None or not appearance.isConstructed:
            return
        elif self.entity.health <= 0:
            return
        else:
            self.__showZone()
            return

    def __showZone(self):
        if self.radius > 0.0 and self.entity.appearance is not None and not self.__isShowed:
            if self.__effect is None:
                self.__effect = _Effect(self.entity.entityGameObject, self.entity, self.radius)
            self.__effect.start()
            self.__isShowed = True
        return
