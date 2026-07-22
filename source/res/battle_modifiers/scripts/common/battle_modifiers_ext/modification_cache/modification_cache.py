# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/modification_cache/modification_cache.py
from collections import deque
from typing import Optional, Any

class ModificationCache(object):
    DEFAULT_LAYER_COUNT = 0
    __slots__ = ('_modifications', '_maxLayerCount', '_layerIdQueue')

    def __init__(self, layerCount=None):
        if layerCount is None:
            layerCount = self.DEFAULT_LAYER_COUNT
        self._modifications = {}
        self._maxLayerCount = layerCount
        self._layerIdQueue = deque()
        return

    def clear(self):
        self._modifications.clear()
        self._layerIdQueue.clear()

    def _addLayer(self, layerId, initValue=None):
        if len(self._layerIdQueue) == self._maxLayerCount:
            del self._modifications[self._layerIdQueue.popleft()]
        self._layerIdQueue.append(layerId)
        self._modifications[layerId] = initValue
