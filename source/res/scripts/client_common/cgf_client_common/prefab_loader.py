# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/cgf_client_common/prefab_loader.py
from __future__ import absolute_import
import typing
import CGF
from cgf_client_common.game_object_holder import GameObjectHolder

class PrefabLoader(GameObjectHolder):

    def __init__(self, spaceID, gameObjectName=None):
        super(PrefabLoader, self).__init__(spaceID, gameObjectName)
        self._loadingQueue = []
        self.__prefabLoadRequests = set()

    def isReady(self):
        raise NotImplementedError

    def _destroy(self, queue=None):
        self._cancelPrefabLoadRequests()
        self._loadingQueue = []
        super(PrefabLoader, self)._destroy(queue)

    def loadPrefab(self, prefab, go, vector, callback):
        if not self.isReady():
            self._loadingQueue.append((prefab,
             go,
             vector,
             callback))
            return CGF.INVALID_UUID
        return self.__startPrefabLoad(prefab, go, vector, callback)

    def _flushLoadingQueue(self):
        while self._loadingQueue:
            prefab, go, vector, callback = self._loadingQueue.pop()
            self.__startPrefabLoad(prefab, go, vector, callback)

    def _clearLoadingQueue(self):
        self._loadingQueue = []

    def __startPrefabLoad(self, prefab, go, vector, callback):
        requests = self.__prefabLoadRequests
        holder = {}

        def onLoaded(objects, queue):
            requests.discard(holder.get('uuid'))
            return callback(objects, queue)

        uuid = CGF.loadAndCreatePrefabWithParent(prefab, go, vector, onLoaded)
        if uuid.valid:
            holder['uuid'] = uuid
            requests.add(uuid)
        return uuid

    def _cancelPrefabLoadRequests(self):
        for uuid in self.__prefabLoadRequests:
            CGF.cancelCreateRequest(self._spaceID, uuid)

        self.__prefabLoadRequests = set()
