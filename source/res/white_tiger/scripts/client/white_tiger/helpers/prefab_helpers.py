# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/helpers/prefab_helpers.py
from __future__ import absolute_import
import logging
from abc import ABCMeta, abstractmethod
import CGF
import GenericComponents
from typing import List
_logger = logging.getLogger(__name__)

class PrefabHandlerComponent(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(PrefabHandlerComponent, self).__init__()
        self._gameObject = None
        self._parentEntity = None
        return

    @abstractmethod
    def createGameObject(self):
        pass

    def loadGameObject(self, entity, prefabPath, gameObject, matrix):
        if gameObject is None or not gameObject.valid:
            _logger.warning('loadGameObject: invalid parent GameObject, skip prefab %s', prefabPath)
            return
        else:
            self._parentEntity = entity
            CGF.loadAndCreatePrefabWithParent(prefabPath, gameObject, matrix, self._onGameObjectLoaded)
            return

    def _onGameObjectLoaded(self, objects, queue):
        root = objects[0]
        self._gameObject = queue.gameObject(root)
        if hasattr(self._parentEntity, 'appearance') and self._parentEntity.appearance is not None:
            appearance = self._parentEntity.appearance
            queue.createComponent(root, GenericComponents.RedirectorComponent, appearance.gameObject)
        else:
            queue.createComponent(root, GenericComponents.RedirectorComponent, self._parentEntity.entityGameObject)
        return

    def destroyGameObject(self):
        if not self._gameObject:
            return
        else:
            if self._gameObject.valid:
                CGF.removeGameObject(self._gameObject)
            self._gameObject = None
            return
