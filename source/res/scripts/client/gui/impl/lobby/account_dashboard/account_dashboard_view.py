# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/account_dashboard_view.py
import logging
import WWISE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.account_dashboard.account_dashboard_model import AccountDashboardModel
from gui.impl.lobby.account_dashboard.features.bonus_xp_feature import BonusXPFeature
from gui.impl.lobby.account_dashboard.features.dog_tags_feature import DogTagsFeature
from gui.impl.lobby.account_dashboard.features.excluded_maps_feature import ExcludedMapsFeature
from gui.impl.lobby.account_dashboard.features.header_feature import HeaderFeature
from gui.impl.lobby.account_dashboard.features.parental_control_feature import ParentalControlFeature
from gui.impl.lobby.account_dashboard.features.premium_account_feature import PremiumAccountFeature
from gui.impl.lobby.account_dashboard.features.premium_quests_feature import PremiumQuestsFeature
from gui.impl.lobby.account_dashboard.features.reserve_stock_feature import ReserveStockFeature
from gui.impl.lobby.account_dashboard.features.subscriptions_feature import SubscriptionsFeature
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.wot_plus.loggers import WotPlusAccountDashboardLogger
_logger = logging.getLogger(__name__)

class Feature(CONST_CONTAINER):
    HEADER = 'header'
    SUBSCRIPTIONS = 'subscriptions'
    PREMIUM_ACCOUNT = 'premiumAccount'
    BONUS_XP = 'bonusXp'
    RESERVER_STOCK = 'reserveStock'
    PREMIUM_QUESTS = 'premiumQuests'
    EXCLUDED_MAPS = 'excludedMaps'
    DOG_TAGS = 'dogTags'
    PARENTAL_CONTROL = 'parentalControl'


class SOUNDS(CONST_CONTAINER):
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_AD = 'STATE_hangar_place_acc_dashboard'
    EVENT_ENTER = 'ev_acc_dashboard_enter'
    EVENT_EXIT = 'ev_acc_dashboard_exit'


class AccountDashboardView(ViewImpl):
    __slots__ = ('_features', 'modelDataControllers', '_wotPlusUILogger')
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = AccountDashboardModel()
        super(AccountDashboardView, self).__init__(settings)
        self._features = {Feature.HEADER: HeaderFeature(self.viewModel),
         Feature.SUBSCRIPTIONS: SubscriptionsFeature(self.viewModel),
         Feature.PREMIUM_ACCOUNT: PremiumAccountFeature(self.viewModel),
         Feature.BONUS_XP: BonusXPFeature(self.viewModel),
         Feature.RESERVER_STOCK: ReserveStockFeature(self.viewModel),
         Feature.PREMIUM_QUESTS: PremiumQuestsFeature(self.viewModel),
         Feature.EXCLUDED_MAPS: ExcludedMapsFeature(self.viewModel),
         Feature.DOG_TAGS: DogTagsFeature(self.viewModel),
         Feature.PARENTAL_CONTROL: ParentalControlFeature(self.viewModel)}
        self._wotPlusUILogger = WotPlusAccountDashboardLogger()
        self.modelDataControllers = {}
        Waiting.show('loadPage')

    @property
    def viewModel(self):
        return self.getViewModel()

    def createPopOverContent(self, event):
        for feature in self._features.values():
            content = feature.createPopOverContent(event)
            if content:
                return content

    def createToolTipContent(self, event, contentID):
        for feature in self._features.values():
            content = feature.createToolTipContent(event, contentID)
            if content:
                return content

        _logger.error('Crew header view tried creating invalid tooltip with contentID %d', contentID)
        return None

    def _onLoading(self, *args, **kwargs):
        super(AccountDashboardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            for feature in self._features.values():
                feature.fill(tx)

    def _initialize(self, *args, **kwargs):
        super(AccountDashboardView, self)._initialize(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        WWISE.WW_setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_AD)
        WWISE.WW_eventGlobal(SOUNDS.EVENT_ENTER)
        for feature in self._features.values():
            feature.initialize()

        self._wotPlusUILogger.onViewInitialize()
        Waiting.hide('loadPage')

    def _finalize(self):
        super(AccountDashboardView, self)._finalize()
        WWISE.WW_eventGlobal(SOUNDS.EVENT_EXIT)
        self.viewModel.onClose -= self.__onClose
        for feature in self._features.values():
            feature.finalize()

        self._wotPlusUILogger.onViewFinalize()

    def __onClose(self):
        self._wotPlusUILogger.logCloseEvent()
        showHangar()
