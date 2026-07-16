# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/client_arena_component_system.py
from __future__ import absolute_import
import weakref
from future.moves import pickle
from future.utils import viewitems
import Event
from arena_component_system.arena_sync_object import ArenaSyncObject
from components_base.component import Component
from components_base.component_controller import ComponentController
from constants import ARENA_UPDATE, ARENA_SYNC_OBJECT_NAMES
from debug_utils import LOG_ERROR

class ClientArenaComponent(Component):

    def __init__(self, componentSystem):
        super(ClientArenaComponent, self).__init__()
        self._componentSystem = weakref.ref(componentSystem)
        self._onUpdate = {}
        self._eventManager = Event.EventManager()

    def destroy(self):
        self._onUpdate.clear()
        self._eventManager.clear()

    def update(self, updateType, argStr):
        delegate = self._onUpdate.get(updateType, None)
        if delegate is not None:
            delegate(argStr)
        return

    def addSyncDataCallback(self, syncDataObjectType, key, handler):
        captured = self._componentSystem()
        if captured is not None:
            captured.addSyncDataObjectCallback(syncDataObjectType, key, handler)
        return

    def removeSyncDataCallback(self, syncDataObjectType, key, handler):
        captured = self._componentSystem()
        if captured is not None:
            captured.removeSyncDataObjectCallback(syncDataObjectType, key, handler)
        return

    def getSyncDataObjectData(self, syncDataObjectType, key):
        return self._componentSystem().getSyncDataObjectData(syncDataObjectType, key)


class ClientArenaComponentSystem(ComponentController):

    def __init__(self, arena, bonusType, arenaType):
        super(ClientArenaComponentSystem, self).__init__('ClientArenaComponentSystem')
        self.bonusType = bonusType
        self.arenaType = arenaType
        self.arena = weakref.ref(arena)
        self._onUpdate = {ARENA_UPDATE.SYNC_OBJECTS: self.__onFullSyncObjectReceived,
         ARENA_UPDATE.SYNC_OBJECTS_DIFF: self.__onSyncObjectUpdateReceived}
        self.__syncDataObjects = {}
        for k in ARENA_SYNC_OBJECT_NAMES:
            self.__syncDataObjects[k] = ArenaSyncObject()

    def destroy(self):
        super(ClientArenaComponentSystem, self).destroy()
        self._onUpdate.clear()
        self.__syncDataObjects.clear()

    def update(self, updateType, argStr):
        for component in self._components:
            component.update(updateType, argStr)

        delegate = self._onUpdate.get(updateType, None)
        if delegate is not None:
            delegate(argStr)
        return

    def addSyncDataObjectCallback(self, syncDataObjectType, key, handler):
        syncDataObject = self.__syncDataObjects.get(syncDataObjectType, None)
        if syncDataObject is not None:
            syncDataObject.addCallback(key, handler)
        return

    def removeSyncDataObjectCallback(self, syncDataObjectType, key, handler):
        syncDataObject = self.__syncDataObjects.get(syncDataObjectType, None)
        if syncDataObject is not None:
            syncDataObject.removeCallback(key, handler)
        return

    def getSyncDataObjectData(self, syncDataObjectType, key):
        syncDataObject = self.__syncDataObjects.get(syncDataObjectType, None)
        if syncDataObject is not None:
            return syncDataObject.getData(key)
        else:
            LOG_ERROR("No arena sync data object found for object type '{}:{}'. Returning None.".format(syncDataObjectType, ARENA_SYNC_OBJECT_NAMES.get(syncDataObjectType, '<Unknown>')))
            return

    def __onFullSyncObjectReceived(self, argStr):
        o = pickle.loads(argStr)
        for key, syncObject in viewitems(self.__syncDataObjects):
            fullSyncData = o.get(key, None)
            if fullSyncData is not None:
                syncObject.synchronize(True, fullSyncData)

        return

    def __onSyncObjectUpdateReceived(self, argStr):
        diff = pickle.loads(argStr)
        for key, syncObject in viewitems(self.__syncDataObjects):
            syncDataDiff = diff.get(key, None)
            if syncDataDiff is not None:
                syncObject.synchronize(False, syncDataDiff)

        return
