# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/server_info_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PingStatus(IntEnum):
    REQUESTED = 0
    HIGH = 1
    NORM = 2
    LOW = 3


class ServerInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ServerInfoModel, self).__init__(properties=properties, commands=commands)

    def getServerName(self):
        return self._getString(0)

    def setServerName(self, value):
        self._setString(0, value)

    def getStatus(self):
        return PingStatus(self._getNumber(1))

    def setStatus(self, value):
        self._setNumber(1, value.value)

    def _initialize(self):
        super(ServerInfoModel, self)._initialize()
        self._addStringProperty('serverName', '')
        self._addNumberProperty('status')
