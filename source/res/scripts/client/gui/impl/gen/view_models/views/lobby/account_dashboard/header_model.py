# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/header_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class HeaderModel(ViewModel):
    __slots__ = ('onShowBadges', 'onAccountInfoButtonClick')

    def __init__(self, properties=11, commands=2):
        super(HeaderModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(0)

    def setUserName(self, value):
        self._setString(0, value)

    def getBadgeID(self):
        return self._getString(1)

    def setBadgeID(self, value):
        self._setString(1, value)

    def getSuffixBadgeID(self):
        return self._getString(2)

    def setSuffixBadgeID(self, value):
        self._setString(2, value)

    def getIsInClan(self):
        return self._getBool(3)

    def setIsInClan(self, value):
        self._setBool(3, value)

    def getClanAbbrev(self):
        return self._getString(4)

    def setClanAbbrev(self, value):
        self._setString(4, value)

    def getRoleInClan(self):
        return self._getString(5)

    def setRoleInClan(self, value):
        self._setString(5, value)

    def getClanDescription(self):
        return self._getString(6)

    def setClanDescription(self, value):
        self._setString(6, value)

    def getClanIcon(self):
        return self._getString(7)

    def setClanIcon(self, value):
        self._setString(7, value)

    def getIsTeamKiller(self):
        return self._getBool(8)

    def setIsTeamKiller(self, value):
        self._setBool(8, value)

    def getIsEmailPending(self):
        return self._getBool(9)

    def setIsEmailPending(self, value):
        self._setBool(9, value)

    def getEmailButtonLabel(self):
        return self._getResource(10)

    def setEmailButtonLabel(self, value):
        self._setResource(10, value)

    def _initialize(self):
        super(HeaderModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('badgeID', '')
        self._addStringProperty('suffixBadgeID', '')
        self._addBoolProperty('isInClan', False)
        self._addStringProperty('clanAbbrev', '')
        self._addStringProperty('roleInClan', '')
        self._addStringProperty('clanDescription', '')
        self._addStringProperty('clanIcon', '')
        self._addBoolProperty('isTeamKiller', False)
        self._addBoolProperty('isEmailPending', False)
        self._addResourceProperty('emailButtonLabel', R.invalid())
        self.onShowBadges = self._addCommand('onShowBadges')
        self.onAccountInfoButtonClick = self._addCommand('onAccountInfoButtonClick')
