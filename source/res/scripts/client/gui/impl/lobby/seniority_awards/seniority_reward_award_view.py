# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
import re
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from helpers import dependency, time_utils
from frameworks.wulf import ViewSettings, WindowLayer
from gui.game_control.seniority_awards_controller import SACOIN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getSeniorityAwardsRewardsAndBonuses
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_tooltip_constants import SeniorityAwardsTooltipConstants
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_award_view_model import SeniorityRewardAwardViewModel
from gui.impl.lobby.seniority_awards.seniority_awards_sounds import SENIORITY_REWARD_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName, Vehicle
from gui.shared.event_dispatcher import showShop
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
_logger = logging.getLogger(__name__)
REG_EXP_QUEST_SUBTYPE = ':([Y, y]\\d*)|:([A,a,B,b][T,t])'
_T50_2_STYLE_NAME = backport.text(R.strings.vehicle_customization.special_style.t50_2())
_EXCLUDED_BONUSES = ('slots',)
_BONUSES_ORDER = ({'getLabel': _T50_2_STYLE_NAME},
 {'getName': 'crystal'},
 {'getName': 'credits'},
 {'getIcon': 'personalBook'},
 {'getIcon': 'universalBook'},
 {'getOverlayType': 'equipmentModernized'},
 {'getName': 'premium_plus'},
 {'getIconSmall': 'bonus_battle'},
 {'getName': 'goodies',
  'getIcon': 'credits'},
 {'getName': 'goodies',
  'getIcon': 'xp'},
 {'getName': 'badge'},
 {'getName': 'customizations',
  'getIcon': 'style'},
 {'getIcon': 'projectionDecal'},
 {'getName': 'dossier_achievement'},
 {'getName': 'customizations',
  'getIcon': 'emblem'})

def _keySortOrder(bonus, _):
    for index, criteria in enumerate(_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_BONUSES_ORDER)


_SENIORITY_VEHICLES_ORDER = ('ussr:R197_KV_1S_MZ', 'germany:G158_VK2801_105_SPXXI', 'usa:A134_M24E2_SuperChaffee', 'usa:A130_Super_Hellcat', 'ussr:R160_T_50_2')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _vehiclesSortOrder(vehicleCD, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    return _SENIORITY_VEHICLES_ORDER.index(vehicle.name) if vehicle and vehicle.name in _SENIORITY_VEHICLES_ORDER else len(_SENIORITY_VEHICLES_ORDER)


def _getSeniorityAwardsRewardType(completedQuests):
    yearGroup = None
    betaTestGroup = None
    for questID in completedQuests:
        seniorityLvlSearch = re.search(REG_EXP_QUEST_SUBTYPE, questID)
        if seniorityLvlSearch is not None:
            yearGroup = yearGroup or seniorityLvlSearch.groups()[0]
            betaTestGroup = betaTestGroup or seniorityLvlSearch.groups()[1]

    return '{}_{}'.format(yearGroup, betaTestGroup) if yearGroup and betaTestGroup else yearGroup or betaTestGroup


class SeniorityRewardAwardView(ViewImpl):
    __slots__ = ('__bonuses', '__vehicles', '__specialCurrencies', '__tooltipData')
    _COMMON_SOUND_SPACE = SENIORITY_REWARD_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = SeniorityRewardAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeniorityRewardAwardView, self).__init__(settings)
        self.__bonuses = []
        self.__vehicles = []
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
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _onLoading(self, completedQuests, data, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._onLoading(*args, **kwargs)
        saRewardType = _getSeniorityAwardsRewardType(completedQuests)
        self.__updateBonuses(data)
        self.__tooltipData = {}
        with self.viewModel.transaction() as vm:
            self.__setRewards(vm)
            self.__setBonuses(vm)
            self.__setSpecialCurrency(vm)
            vm.setIsShopOnOpenLocked(self.__needBlockShopTransition)
            if saRewardType is not None:
                vm.setCategory(saRewardType.upper())
        return

    def _onLoaded(self, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._onLoaded(*args, **kwargs)
        timestamp = time_utils.getServerUTCTime()
        AccountSettings.setNotifications(SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP, timestamp)

    def _initialize(self, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._initialize(*args, **kwargs)
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick

    def _finalize(self):
        self.__bonuses = None
        self.__vehicles = None
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        super(SeniorityRewardAwardView, self)._finalize()
        return

    @property
    def __needBlockShopTransition(self):
        return not self.__specialCurrencies.get(SACOIN)

    def __setRewards(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        for vehicleCD in self.__vehicles:
            vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
            vehicleModel = VehicleModel()
            fillVehicleModel(vehicleModel, vehicleItem)
            vehiclesList.addViewModel(vehicleModel)

        vehiclesList.invalidate()

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
        currencyCount = self.__specialCurrencies.get(SACOIN)
        if currencyCount:
            viewModel.setSpecialCurrencyCount(currencyCount)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__tooltipData:
            return self.__tooltipData[tooltipId]
        vehicleCD = event.getArgument('vehicleCD')
        if vehicleCD is None:
            return
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(int(vehicleCD), True))
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD])
        else:
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SENIORITY_AWARD_VEHICLE, specialArgs=(vehicleCD,
             100,
             None,
             None,
             None,
             None,
             True,
             True)) if tooltipId == SeniorityAwardsTooltipConstants.TOOLTIP_VEHICLE_REWARD else None

    def __updateBonuses(self, data):
        seniorityAwards = getSeniorityAwardsRewardsAndBonuses(data, excluded=_EXCLUDED_BONUSES, sortKey=lambda b: _keySortOrder(*b))
        self.__bonuses = seniorityAwards.bonuses or []
        self.__vehicles = sorted(seniorityAwards.vehicles, key=_vehiclesSortOrder) or []
        self.__specialCurrencies = seniorityAwards.currencies or {}

    @staticmethod
    def __getVehImgResource(vehicleName):
        return getIconResourceName(getNationLessName(vehicleName))

    def __onOpenBtnClick(self):
        if not self.viewModel.getIsShopOnOpenLocked():
            showShop(getPlayerSeniorityAwardsUrl())
        self.destroyWindow()


class SeniorityRewardAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, completedQuests=None, data=None, viewID=None):
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(viewID, completedQuests=completedQuests, data=data), layer=WindowLayer.TOP_WINDOW)
