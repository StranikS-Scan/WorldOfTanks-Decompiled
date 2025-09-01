# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/user_info_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class SteamEmailStatusEnum(IntEnum):
    UNDEFINED = 0
    ADD_NEEDED = 1
    ADDED = 2
    CONFIRMATION_SENT = 3
    CONFIRMED = 4
    PROCESSING = 5


class UserInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(UserInfoModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(0)

    def setUserName(self, value):
        self._setString(0, value)

    def getBadgeID(self):
        return self._getNumber(1)

    def setBadgeID(self, value):
        self._setNumber(1, value)

    def getIsInClan(self):
        return self._getBool(2)

    def setIsInClan(self, value):
        self._setBool(2, value)

    def getClanAbbrev(self):
        return self._getString(3)

    def setClanAbbrev(self, value):
        self._setString(3, value)

    def getRoleInClan(self):
        return self._getString(4)

    def setRoleInClan(self, value):
        self._setString(4, value)

    def getEmail(self):
        return self._getString(5)

    def setEmail(self, value):
        self._setString(5, value)

    def getAnonymized(self):
        return self._getBool(6)

    def setAnonymized(self, value):
        self._setBool(6, value)

    def getSteamEmailStatus(self):
        return SteamEmailStatusEnum(self._getNumber(7))

    def setSteamEmailStatus(self, value):
        self._setNumber(7, value.value)

    def getHasSteamAccount(self):
        return self._getBool(8)

    def setHasSteamAccount(self, value):
        self._setBool(8, value)

    def getTeamKiller(self):
        return self._getBool(9)

    def setTeamKiller(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(UserInfoModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addNumberProperty('badgeID', 0)
        self._addBoolProperty('isInClan', False)
        self._addStringProperty('clanAbbrev', '')
        self._addStringProperty('roleInClan', '')
        self._addStringProperty('email', '')
        self._addBoolProperty('anonymized', False)
        self._addNumberProperty('steamEmailStatus')
        self._addBoolProperty('hasSteamAccount', False)
        self._addBoolProperty('teamKiller', False)
