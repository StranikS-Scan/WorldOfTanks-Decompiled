# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/cgf_client_common/game_object_holder.py
from __future__ import absolute_import
import typing
import CGF

class GameObjectHolder(object):

    def __init__(self, spaceID, gameObjectName=None):
        self._spaceID = spaceID
        self.__gameObjectName = gameObjectName
        queue = CGF.CommandQueue(spaceID)
        self._gameObject = queue.createGameObject(gameObjectName)

    @property
    def gameObject(self):
        return self._gameObject

    @property
    def spaceID(self):
        return self._spaceID

    def _reset(self, queue=None):
        queue = queue or CGF.CommandQueue(self._spaceID)
        self._destroy(queue)
        self._gameObject = queue.createGameObject(self.__gameObjectName)

    def _destroy(self, queue=None):
        queue = queue or CGF.CommandQueue(self._spaceID)
        if self._gameObject and self._gameObject.valid:
            queue.removeGameObject(self._gameObject)
