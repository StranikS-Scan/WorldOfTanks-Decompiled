# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/header_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import UserInfoModel

class HeaderModel(UserInfoModel):
    __slots__ = ('onShowBadges', 'onAccountInfoButtonClick')

    def __init__(self, properties=18, commands=2):
        super(HeaderModel, self).__init__(properties=properties, commands=commands)

    def getBadgeID(self):
        return self._getString(11)

    def setBadgeID(self, value):
        self._setString(11, value)

    def getSuffixBadgeID(self):
        return self._getString(12)

    def setSuffixBadgeID(self, value):
        self._setString(12, value)

    def getClanDescription(self):
        return self._getString(13)

    def setClanDescription(self, value):
        self._setString(13, value)

    def getClanIcon(self):
        return self._getString(14)

    def setClanIcon(self, value):
        self._setString(14, value)

    def getIsTeamKiller(self):
        return self._getBool(15)

    def setIsTeamKiller(self, value):
        self._setBool(15, value)

    def getIsEmailPending(self):
        return self._getBool(16)

    def setIsEmailPending(self, value):
        self._setBool(16, value)

    def getEmailButtonLabel(self):
        return self._getResource(17)

    def setEmailButtonLabel(self, value):
        self._setResource(17, value)

    def _initialize(self):
        super(HeaderModel, self)._initialize()
        self._addStringProperty('badgeID', '')
        self._addStringProperty('suffixBadgeID', '')
        self._addStringProperty('clanDescription', '')
        self._addStringProperty('clanIcon', '')
        self._addBoolProperty('isTeamKiller', False)
        self._addBoolProperty('isEmailPending', False)
        self._addResourceProperty('emailButtonLabel', R.invalid())
        self.onShowBadges = self._addCommand('onShowBadges')
        self.onAccountInfoButtonClick = self._addCommand('onAccountInfoButtonClick')
