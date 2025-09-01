# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NetworkReplicationPointComponent.py
import logging
import CGF
from BigWorld import DynamicScriptComponent
from cgf_network import ClientReplicableDataSingleton, ReplicationState, ObjectCommand
_logger = logging.getLogger(__name__)

class NetworkReplicationPointComponent(DynamicScriptComponent):

    def __init__(self):
        super(NetworkReplicationPointComponent, self).__init__()
        self.storage = CGF.findSingleton(self.entity.spaceID, ClientReplicableDataSingleton)
        if self.storage is None:
            _logger.error('Failed to find a ClientReplicableDataSingleton')
            return
        else:
            self.__processCreation()
            self.__processRemoved()
            return

    def onLeaveWorld(self):
        for status in self.status:
            self.__createRemoveState(status['networkID'])

    def setSlice_removed(self, changePath, _):
        if self.removed is None:
            return
        else:
            begin, end = changePath[0]
            for nid in self.removed[begin:end]:
                self.__createRemoveState(nid)

            return

    def setSlice_status(self, changePath, _):
        if self.status is None:
            return
        else:
            begin, end = changePath[0]
            if begin == end:
                return
            for status in self.status[begin:end]:
                self.__createAddState(status)

            return

    def setNested_status(self, changePath, _):
        if self.status is None:
            return
        else:
            self.__createUpdateState(self.status[changePath[0]])
            return

    def __processCreation(self):
        for status in self.status:
            self.__createAddState(status)

    def __processRemoved(self):
        for nid in self.removed:
            self.__createRemoveState(nid)

    def __createAddState(self, status):
        self.storage.add(ReplicationState(status['prefabPath'], ObjectCommand.Add, status['recreateMethod'], status['networkID'], status['parentID'], status['active']))

    def __createRemoveState(self, nid):
        self.storage.remove(nid)

    def __createUpdateState(self, status):
        self.storage.update(status['networkID'], status['active'])
