# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.lobby.seniority_awards.tooltip.seniority_awards_tooltip import SeniorityAwardsTooltip
from gui.impl.lobby.seniority_awards.seniority_awards_helper import getVehicleCD, getRewardCategoryForUI
from helpers import dependency, time_utils
from frameworks.wulf import ViewSettings, WindowLayer
from gui.game_control.seniority_awards_controller import WDR_CURRENCY
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getSeniorityAwardsBonuses
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_award_view_model import SeniorityRewardAwardViewModel, ShopOnOpenState
from gui.impl.lobby.seniority_awards.seniority_awards_sounds import SENIORITY_REWARD_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showShop
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
_logger = logging.getLogger(__name__)
_T50_2_STYLE_NAME = backport.text(R.strings.vehicle_customization.special_style.t50_2())
_AT_BADGE = backport.text(R.strings.badge.badge_56())
_BT_BADGE = backport.text(R.strings.badge.badge_57())
_AT_NICKNAME_BADGE = backport.text(R.strings.badge.badge_58())
_BT_NICKNAME_BADGE = backport.text(R.strings.badge.badge_59())
_EXCLUDED_BONUSES = ('slots', 'vehicles')
_BONUSES_ORDER = ({'getLabel': _T50_2_STYLE_NAME},
 {'getName': 'crystal'},
 {'getName': 'credits'},
 {'getIcon': 'personalBook'},
 {'getIcon': 'universalBook'},
 {'getName': 'premium_plus'},
 {'getName': 'battle_bonus'},
 {'getName': 'goodies',
  'getIcon': 'credits'},
 {'getName': 'goodies',
  'getIcon': 'xp'},
 {'getName': 'dossier_badge',
  'getLabel': _AT_NICKNAME_BADGE},
 {'getName': 'dossier_badge',
  'getLabel': _BT_NICKNAME_BADGE},
 {'getName': 'dossier_badge',
  'getLabel': _AT_BADGE},
 {'getName': 'dossier_badge',
  'getLabel': _BT_BADGE},
 {'getIcon': 'projectionDecal'},
 {'getName': 'dossier_achievement'},
 {'getName': 'customizations',
  'getIcon': 'emblem'},
 {'getName': 'customizations',
  'getIcon': 'style'})

def _keySortOrder(bonus, _):
    for index, criteria in enumerate(_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_BONUSES_ORDER)


class SeniorityRewardAwardView(ViewImpl):
    __slots__ = ('__bonuses', '__specialCurrencies', '__tooltipData')
    _COMMON_SOUND_SPACE = SENIORITY_REWARD_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __seniorityAwardsCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = SeniorityRewardAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeniorityRewardAwardView, self).__init__(settings)
        self.__bonuses = []
        self.__specialCurrencies = {}
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(SeniorityRewardAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.seniority_awards.SeniorityAwardsTooltip():
            return SeniorityAwardsTooltip(str(self.viewModel.getCategory()), self.__seniorityAwardsCtrl.yearsInGame)
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _onLoading(self, data, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._onLoading(*args, **kwargs)
        if data is None:
            _logger.error('Rewards data is None')
            return
        else:
            self.__updateBonuses(data)
            self.__tooltipData = {}
            with self.viewModel.transaction() as vm:
                self.__setBonuses(vm)
                self.__setSpecialCurrency(vm)
                vm.setShopOnOpenState(self.__getShopOnOpenState())
                category = getRewardCategoryForUI()
                vm.setCategory(category.lower())
            return

    def _onLoaded(self, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._onLoaded(*args, **kwargs)
        timestamp = time_utils.getServerUTCTime()
        AccountSettings.setNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, timestamp)

    def _finalize(self):
        self.__bonuses = None
        super(SeniorityRewardAwardView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onOpenBtnClick, self.__onOpenBtnClick), (self.viewModel.onShopBtnClick, self.__onShopBtnClick), (self.__seniorityAwardsCtrl.onUpdated, self.__onSettingsChange))

    def __getShopOnOpenState(self):
        if self.__needBlockShopTransition:
            return ShopOnOpenState.NOT_AVAILABLE
        return ShopOnOpenState.DISABLED if not self.__seniorityAwardsCtrl.isAvailable else ShopOnOpenState.AVAILABLE

    @property
    def __needBlockShopTransition(self):
        return not self.__specialCurrencies.get(WDR_CURRENCY)

    def __setBonuses(self, viewModel):
        bonusesList = viewModel.getBonuses()
        bonusesList.clear()
        for index, (bonus, tooltip) in enumerate(self.__bonuses):
            tooltipId = str(index)
            bonus.setTooltipId(tooltipId)
            bonus.setIndex(index)
            bonusesList.addViewModel(bonus)
            self.__tooltipData[tooltipId] = tooltip

        bonusesList.invalidate()

    def __setSpecialCurrency(self, viewModel):
        currencyCount = self.__specialCurrencies.get(WDR_CURRENCY)
        if currencyCount:
            viewModel.setSpecialCurrencyCount(currencyCount)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__tooltipData:
            return self.__tooltipData[tooltipId]
        vehicleCD = getVehicleCD(event.getArgument('vehicleCD'))
        if vehicleCD is None:
            return
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(int(vehicleCD), True))
        else:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD]) if tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT else None

    def __updateBonuses(self, data):
        seniorityAwards = getSeniorityAwardsBonuses(data, excluded=_EXCLUDED_BONUSES, sortKey=lambda b: _keySortOrder(*b))
        self.__bonuses = seniorityAwards.bonuses or []
        self.__specialCurrencies = seniorityAwards.currencies or {}

    def __onOpenBtnClick(self):
        self.destroyWindow()

    def __onShopBtnClick(self):
        if self.viewModel.getShopOnOpenState() == ShopOnOpenState.AVAILABLE:
            showShop(getPlayerSeniorityAwardsUrl())

    def __onSettingsChange(self):
        with self.viewModel.transaction() as vm:
            vm.setShopOnOpenState(self.__getShopOnOpenState())


class SeniorityRewardAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, data=None, viewID=None):
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(viewID, data=data), layer=WindowLayer.TOP_WINDOW)
