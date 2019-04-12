# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_header_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_header_clan_info_model import PremDashboardHeaderClanInfoModel

class PremDashboardHeaderModel(ViewModel):
    __slots__ = ('onShowBadges',)

    @property
    def userName(self):
        return self._getViewModel(0)

    @property
    def clanInfo(self):
        return self._getViewModel(1)

    @property
    def personalReserves(self):
        return self._getViewModel(2)

    @property
    def clanReserves(self):
        return self._getViewModel(3)

    def getPrefixBadgeId(self):
        return self._getString(4)

    def setPrefixBadgeId(self, value):
        self._setString(4, value)

    def getSuffixBadgeId(self):
        return self._getString(5)

    def setSuffixBadgeId(self, value):
        self._setString(5, value)

    def getIsInClan(self):
        return self._getBool(6)

    def setIsInClan(self, value):
        self._setBool(6, value)

    def getHasClanReserves(self):
        return self._getBool(7)

    def setHasClanReserves(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(PremDashboardHeaderModel, self)._initialize()
        self._addViewModelProperty('userName', UserNameModel())
        self._addViewModelProperty('clanInfo', PremDashboardHeaderClanInfoModel())
        self._addViewModelProperty('personalReserves', UserListModel())
        self._addViewModelProperty('clanReserves', UserListModel())
        self._addStringProperty('prefixBadgeId', '')
        self._addStringProperty('suffixBadgeId', '')
        self._addBoolProperty('isInClan', False)
        self._addBoolProperty('hasClanReserves', False)
        self.onShowBadges = self._addCommand('onShowBadges')
