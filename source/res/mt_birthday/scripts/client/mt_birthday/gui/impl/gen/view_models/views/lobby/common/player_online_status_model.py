# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/common/player_online_status_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PlayerOnlineStatus(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'
    IN_BATTLE = 'inBattle'


class PlayerOnlineStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PlayerOnlineStatusModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return PlayerOnlineStatus(self._getString(0))

    def setStatus(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(PlayerOnlineStatusModel, self)._initialize()
        self._addStringProperty('status', PlayerOnlineStatus.OFFLINE.value)
