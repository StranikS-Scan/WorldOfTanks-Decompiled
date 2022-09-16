# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/account_dashboard_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.bonus_xp_model import BonusXpModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.dog_tags_model import DogTagsModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.excluded_maps_model import ExcludedMapsModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.header_model import HeaderModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.parental_control_model import ParentalControlModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.premium_account_model import PremiumAccountModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.premium_quests_model import PremiumQuestsModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.reserve_stock_model import ReserveStockModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.subscriptions_entry_point_model import SubscriptionsEntryPointModel

class AccountDashboardModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=11, commands=1):
        super(AccountDashboardModel, self).__init__(properties=properties, commands=commands)

    @property
    def header(self):
        return self._getViewModel(0)

    @staticmethod
    def getHeaderType():
        return HeaderModel

    @property
    def dogTags(self):
        return self._getViewModel(1)

    @staticmethod
    def getDogTagsType():
        return DogTagsModel

    @property
    def premiumAccount(self):
        return self._getViewModel(2)

    @staticmethod
    def getPremiumAccountType():
        return PremiumAccountModel

    @property
    def excludedMaps(self):
        return self._getViewModel(3)

    @staticmethod
    def getExcludedMapsType():
        return ExcludedMapsModel

    @property
    def premiumQuests(self):
        return self._getViewModel(4)

    @staticmethod
    def getPremiumQuestsType():
        return PremiumQuestsModel

    @property
    def reserveStock(self):
        return self._getViewModel(5)

    @staticmethod
    def getReserveStockType():
        return ReserveStockModel

    @property
    def bonusXp(self):
        return self._getViewModel(6)

    @staticmethod
    def getBonusXpType():
        return BonusXpModel

    @property
    def parentalControl(self):
        return self._getViewModel(7)

    @staticmethod
    def getParentalControlType():
        return ParentalControlModel

    @property
    def subscriptions(self):
        return self._getViewModel(8)

    @staticmethod
    def getSubscriptionsType():
        return SubscriptionsEntryPointModel

    def getIsParentalControlEnabled(self):
        return self._getBool(9)

    def setIsParentalControlEnabled(self, value):
        self._setBool(9, value)

    def getIsPlayerSubscriptionsEntrypointHidden(self):
        return self._getBool(10)

    def setIsPlayerSubscriptionsEntrypointHidden(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(AccountDashboardModel, self)._initialize()
        self._addViewModelProperty('header', HeaderModel())
        self._addViewModelProperty('dogTags', DogTagsModel())
        self._addViewModelProperty('premiumAccount', PremiumAccountModel())
        self._addViewModelProperty('excludedMaps', ExcludedMapsModel())
        self._addViewModelProperty('premiumQuests', PremiumQuestsModel())
        self._addViewModelProperty('reserveStock', ReserveStockModel())
        self._addViewModelProperty('bonusXp', BonusXpModel())
        self._addViewModelProperty('parentalControl', ParentalControlModel())
        self._addViewModelProperty('subscriptions', SubscriptionsEntryPointModel())
        self._addBoolProperty('isParentalControlEnabled', True)
        self._addBoolProperty('isPlayerSubscriptionsEntrypointHidden', False)
        self.onClose = self._addCommand('onClose')
