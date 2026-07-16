# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiComponent.py
from __future__ import absolute_import
import logging
import weakref
import typing
import CGF
import GenericComponents
import Math
from typing import List
from helpers import dependency, fixed_dict
from points_of_interest.components import PoiStateComponent
from points_of_interest_shared import PoiType, PoiStatus
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class PoiComponent(DynamicScriptComponent):

    def __init__(self):
        super(PoiComponent, self).__init__()
        self.__sessionProvider = dependency.instance(IBattleSessionProvider)
        self.__dynObjectsCache = dependency.instance(IBattleDynamicObjectsCache)
        self.__prefabGo = None
        self.__createVisual()
        return

    @property
    def _poiVisualConfig(self):
        return self.__dynObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getPointOfInterestConfig()

    def onDestroy(self):
        from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
        g_eventBus.handleEvent(events.PointOfInterestEvent(events.PointOfInterestEvent.REMOVED, {'point': weakref.proxy(self)}), scope=EVENT_BUS_SCOPE.BATTLE)
        self.entity.entityGameObject.removeComponent(PoiStateComponent)
        self.__removeVisual()
        super(PoiComponent, self).onDestroy()

    def set_progress(self, prev):
        component = self.entity.entityGameObject.findWrite(PoiStateComponent)
        if component is not None:
            component.progress = self.progress
        return

    def set_invader(self, prev):
        component = self.entity.entityGameObject.findWrite(PoiStateComponent)
        if component is not None:
            component.invader = self.invader
        return

    def set_status(self, prev):
        component = self.entity.entityGameObject.findWrite(PoiStateComponent)
        if component is not None:
            component.status = self.__getStatus()
        return

    def _onAvatarReady(self):
        if self.entity.entityGameObject is None:
            _logger.warning('Entity game object is not valid! Could not create PoiComponent')
            return
        else:
            status = self.__getStatus()
            queue = CGF.CommandQueue(self.spaceID)
            queue.createComponent(self.entity.entityGameObject, PoiStateComponent, self.pointID, PoiType(self.type), self.progress, self.invader, status)
            from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
            g_eventBus.handleEvent(events.PointOfInterestEvent(events.PointOfInterestEvent.ADDED, {'point': weakref.proxy(self)}), scope=EVENT_BUS_SCOPE.BATTLE)
            return

    def __createVisual(self):
        parent = self.entity.entityGameObject
        CGF.loadAndCreatePrefabWithParent(self._poiVisualConfig.getPointOfInterestPrefab(self.radius), parent, Math.Vector3(), self.__onPrefabLoaded)

    def __removeVisual(self):
        if self.__prefabGo is not None:
            self.__prefabGo.destroy()
        self.__prefabGo = None
        return

    def __onPrefabLoaded(self, objects, queue):
        root = objects[0]
        self.__prefabGo = queue.gameObject(root)
        self.__updateRadius(root, queue)
        queue.activateGameObject(root)

    def __updateRadius(self, root, queue):
        terrainSelectedArea = queue.component(root, GenericComponents.TerrainSelectedAreaComponent)
        if terrainSelectedArea is None:
            _logger.error('Failed to update PoI %s radius. Missing TerrainSelectedArea component.', self.entity.id)
            return
        else:
            terrainSelectedArea.size = Math.Vector2(self.radius * 2, self.radius * 2)
            return

    def __getStatus(self):
        return fixed_dict.getStatusWithTimeInterval(self.status, PoiStatus)
