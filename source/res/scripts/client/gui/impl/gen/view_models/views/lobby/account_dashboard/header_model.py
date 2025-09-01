# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/header_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.header.user_info_model import UserInfoModel

class HeaderModel(UserInfoModel):
    __slots__ = ('onShowBadges', 'onAccountInfoButtonClick')

    def __init__(self, properties=17, commands=2):
        super(HeaderModel, self).__init__(properties=properties, commands=commands)

    def getBadgeID(self):
        return self._getString(10)

    def setBadgeID(self, value):
        self._setString(10, value)

    def getSuffixBadgeID(self):
        return self._getString(11)

    def setSuffixBadgeID(self, value):
        self._setString(11, value)

    def getClanDescription(self):
        return self._getString(12)

    def setClanDescription(self, value):
        self._setString(12, value)

    def getClanIcon(self):
        return self._getString(13)

    def setClanIcon(self, value):
        self._setString(13, value)

    def getIsTeamKiller(self):
        return self._getBool(14)

    def setIsTeamKiller(self, value):
        self._setBool(14, value)

    def getIsEmailPending(self):
        return self._getBool(15)

    def setIsEmailPending(self, value):
        self._setBool(15, value)

    def getEmailButtonLabel(self):
        return self._getResource(16)

    def setEmailButtonLabel(self, value):
        self._setResource(16, value)

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
