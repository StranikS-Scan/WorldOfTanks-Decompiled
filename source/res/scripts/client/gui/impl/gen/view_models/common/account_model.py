# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/account_model.py
from frameworks.wulf import ViewModel

class AccountModel(ViewModel):
    __slots__ = ()
    IGR_TYPE_NONE = 0
    IGR_TYPE_BASE = 1
    IGR_TYPE_PREMIUM = 2

    def __init__(self, properties=10, commands=0):
        super(AccountModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(0)

    def setUserName(self, value):
        self._setString(0, value)

    def getFakeUserName(self):
        return self._getString(1)

    def setFakeUserName(self, value):
        self._setString(1, value)

    def getAnonymizer(self):
        return self._getBool(2)

    def setAnonymizer(self, value):
        self._setBool(2, value)

    def getClanAbbrev(self):
        return self._getString(3)

    def setClanAbbrev(self, value):
        self._setString(3, value)

    def getIgrType(self):
        return self._getNumber(4)

    def setIgrType(self, value):
        self._setNumber(4, value)

    def getIsTeamKiller(self):
        return self._getBool(5)

    def setIsTeamKiller(self, value):
        self._setBool(5, value)

    def getIsKilled(self):
        return self._getBool(6)

    def setIsKilled(self, value):
        self._setBool(6, value)

    def getDatabaseID(self):
        return self._getNumber(7)

    def setDatabaseID(self, value):
        self._setNumber(7, value)

    def getBadge(self):
        return self._getString(8)

    def setBadge(self, value):
        self._setString(8, value)

    def getSuffixBadge(self):
        return self._getString(9)

    def setSuffixBadge(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(AccountModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('fakeUserName', '')
        self._addBoolProperty('anonymizer', False)
        self._addStringProperty('clanAbbrev', '')
        self._addNumberProperty('igrType', 0)
        self._addBoolProperty('isTeamKiller', False)
        self._addBoolProperty('isKilled', False)
        self._addNumberProperty('databaseID', 0)
        self._addStringProperty('badge', '')
        self._addStringProperty('suffixBadge', '')
