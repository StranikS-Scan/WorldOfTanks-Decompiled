# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_header_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_clan_info_model import PremDashboardHeaderClanInfoModel
from gui.impl.gen.view_models.views.lobby.subscription.subscription_card_model import SubscriptionCardModel

class PremDashboardHeaderModel(ViewModel):
    __slots__ = ('onShowBadges', 'onEmailButtonClicked', 'onRenamingButtonClicked')

    def __init__(self, properties=18, commands=3):
        super(PremDashboardHeaderModel, self).__init__(properties=properties, commands=commands)

    @property
    def userName(self):
        return self._getViewModel(0)

    @property
    def subscriptionCard(self):
        return self._getViewModel(1)

    @property
    def clanInfo(self):
        return self._getViewModel(2)

    @property
    def personalReserves(self):
        return self._getViewModel(3)

    @property
    def clanReserves(self):
        return self._getViewModel(4)

    def getPrefixBadgeId(self):
        return self._getString(5)

    def setPrefixBadgeId(self, value):
        self._setString(5, value)

    def getSuffixBadgeId(self):
        return self._getString(6)

    def setSuffixBadgeId(self, value):
        self._setString(6, value)

    def getBadgeContent(self):
        return self._getString(7)

    def setBadgeContent(self, value):
        self._setString(7, value)

    def getIsDynamicBadge(self):
        return self._getBool(8)

    def setIsDynamicBadge(self, value):
        self._setBool(8, value)

    def getIsInClan(self):
        return self._getBool(9)

    def setIsInClan(self, value):
        self._setBool(9, value)

    def getHasClanReserves(self):
        return self._getBool(10)

    def setHasClanReserves(self, value):
        self._setBool(10, value)

    def getIsWarningIconVisible(self):
        return self._getBool(11)

    def setIsWarningIconVisible(self, value):
        self._setBool(11, value)

    def getEmailButtonLabel(self):
        return self._getResource(12)

    def setEmailButtonLabel(self, value):
        self._setResource(12, value)

    def getShowEmailActionTooltip(self):
        return self._getBool(13)

    def setShowEmailActionTooltip(self, value):
        self._setBool(13, value)

    def getIsSubscriptionEnable(self):
        return self._getBool(14)

    def setIsSubscriptionEnable(self, value):
        self._setBool(14, value)

    def getIsRenamingButtonVisible(self):
        return self._getBool(15)

    def setIsRenamingButtonVisible(self, value):
        self._setBool(15, value)

    def getIsRenamingButtonEnabled(self):
        return self._getBool(16)

    def setIsRenamingButtonEnabled(self, value):
        self._setBool(16, value)

    def getIsRenamingProcessVisible(self):
        return self._getBool(17)

    def setIsRenamingProcessVisible(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(PremDashboardHeaderModel, self)._initialize()
        self._addViewModelProperty('userName', UserNameModel())
        self._addViewModelProperty('subscriptionCard', SubscriptionCardModel())
        self._addViewModelProperty('clanInfo', PremDashboardHeaderClanInfoModel())
        self._addViewModelProperty('personalReserves', UserListModel())
        self._addViewModelProperty('clanReserves', UserListModel())
        self._addStringProperty('prefixBadgeId', '')
        self._addStringProperty('suffixBadgeId', '')
        self._addStringProperty('badgeContent', '')
        self._addBoolProperty('isDynamicBadge', False)
        self._addBoolProperty('isInClan', False)
        self._addBoolProperty('hasClanReserves', False)
        self._addBoolProperty('isWarningIconVisible', False)
        self._addResourceProperty('emailButtonLabel', R.invalid())
        self._addBoolProperty('showEmailActionTooltip', False)
        self._addBoolProperty('isSubscriptionEnable', False)
        self._addBoolProperty('isRenamingButtonVisible', False)
        self._addBoolProperty('isRenamingButtonEnabled', False)
        self._addBoolProperty('isRenamingProcessVisible', False)
        self.onShowBadges = self._addCommand('onShowBadges')
        self.onEmailButtonClicked = self._addCommand('onEmailButtonClicked')
        self.onRenamingButtonClicked = self._addCommand('onRenamingButtonClicked')
