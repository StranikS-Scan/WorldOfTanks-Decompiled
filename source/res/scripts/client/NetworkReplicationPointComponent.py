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
            return

    def onLeaveWorld(self):
        for status in self.status:
            self.__processRemove(status)

    def setSlice_status(self, changePath, prev):
        if self.status is None:
            return
        else:
            begin, end = changePath[0]
            if begin == end:
                self.__processRemove(prev[0])
                return
            for status in self.status[begin:end]:
                self.__processAdd(status)

            return

    def setNested_status(self, changePath, _):
        if self.status is None:
            return
        else:
            self.__processUpdate(self.status[changePath[0]])
            return

    def __processCreation(self):
        for status in self.status:
            self.__processAdd(status)

    def __processAdd(self, status):
        self.storage.add(ReplicationState(status['prefabPath'], ObjectCommand.Add, status['recreateMethod'], status['networkID'], status['parentID'], status['active']))

    def __processRemove(self, status):
        self.storage.remove(status['networkID'])

    def __processUpdate(self, status):
        self.storage.update(status['networkID'], status['active'])
