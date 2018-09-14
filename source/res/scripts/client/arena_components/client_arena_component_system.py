# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/client_arena_component_system.py
from constants import ARENA_SYNC_OBJECTS, ARENA_UPDATE, ARENA_SYNC_OBJECT_NAMES
import Event
import cPickle
import weakref
from arena_sync_object import ArenaSyncObject
from svarog_script.py_component import Component
from svarog_script.py_component_system import ComponentSystem

class ClientArenaComponent(Component):

    def __init__(self, componentSystem):
        self.__componentSystem = weakref.ref(componentSystem)
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
        self.__componentSystem().addSyncDataObjectCallback(syncDataObjectType, key, handler)

    def removeSyncDataCallback(self, syncDataObjectType, key, handler):
        self.__componentSystem().removeSyncDataObjectCallback(syncDataObjectType, key, handler)

    def getSyncDataObjectData(self, syncDataObjectType, key):
        return self.__componentSystem().getSyncDataObjectData(syncDataObjectType, key)


class ClientArenaComponentSystem(ComponentSystem):

    def __init__(self, bonusType):
        ComponentSystem.__init__(self)
        self.bonusType = bonusType
        self._onUpdate = {ARENA_UPDATE.SYNC_OBJECTS: self.__onFullSyncObjectReceived,
         ARENA_UPDATE.SYNC_OBJECTS_DIFF: self.__onSyncObjectUpdateReceived}
        self.__syncDataObjects = {}
        for k, v in ARENA_SYNC_OBJECT_NAMES.iteritems():
            self.__syncDataObjects[k] = ArenaSyncObject()

    def destroy(self):
        ComponentSystem.destroy(self)
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
        return syncDataObject.getData(key) if syncDataObject is not None else None

    def __onFullSyncObjectReceived(self, argStr):
        object = cPickle.loads(argStr)
        for key, syncObject in self.__syncDataObjects.iteritems():
            fullSyncData = object.get(key, None)
            if fullSyncData is not None:
                syncObject.synchronize(True, fullSyncData)

        return

    def __onSyncObjectUpdateReceived(self, argStr):
        diff = cPickle.loads(argStr)
        for key, syncObject in self.__syncDataObjects.iteritems():
            syncDataDiff = diff.get(key, None)
            if syncDataDiff is not None:
                syncObject.synchronize(False, syncDataDiff)

        return
