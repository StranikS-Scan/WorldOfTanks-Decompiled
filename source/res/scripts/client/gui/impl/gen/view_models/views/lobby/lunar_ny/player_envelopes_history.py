# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/player_envelopes_history.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PlayerStatus(IntEnum):
    ISFRIEND = 0
    NOTFRIEND = 1
    FRIENDREQUESTINPROGRESS = 2


class PlayerEnvelopesHistory(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(PlayerEnvelopesHistory, self).__init__(properties=properties, commands=commands)

    def getPlayerID(self):
        return self._getNumber(0)

    def setPlayerID(self, value):
        self._setNumber(0, value)

    def getIsOnline(self):
        return self._getBool(1)

    def setIsOnline(self, value):
        self._setBool(1, value)

    def getNickname(self):
        return self._getString(2)

    def setNickname(self, value):
        self._setString(2, value)

    def getClanTag(self):
        return self._getString(3)

    def setClanTag(self, value):
        self._setString(3, value)

    def getReceivedEnvelopesNumber(self):
        return self._getNumber(4)

    def setReceivedEnvelopesNumber(self, value):
        self._setNumber(4, value)

    def getReceivedGoldNumber(self):
        return self._getNumber(5)

    def setReceivedGoldNumber(self, value):
        self._setNumber(5, value)

    def getSentInResponseEnvelopesNumber(self):
        return self._getNumber(6)

    def setSentInResponseEnvelopesNumber(self, value):
        self._setNumber(6, value)

    def getStatus(self):
        return PlayerStatus(self._getNumber(7))

    def setStatus(self, value):
        self._setNumber(7, value.value)

    def _initialize(self):
        super(PlayerEnvelopesHistory, self)._initialize()
        self._addNumberProperty('playerID', 0)
        self._addBoolProperty('isOnline', False)
        self._addStringProperty('nickname', '')
        self._addStringProperty('clanTag', '')
        self._addNumberProperty('receivedEnvelopesNumber', 0)
        self._addNumberProperty('receivedGoldNumber', 0)
        self._addNumberProperty('sentInResponseEnvelopesNumber', 0)
        self._addNumberProperty('status')
