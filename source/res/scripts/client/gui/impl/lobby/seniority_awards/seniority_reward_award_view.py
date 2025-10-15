# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
import re
import typing
import th_async
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SENIORITY_AWARDS_COINS_REMINDER_SHOWN_TIMESTAMP
from constants import SENIORITY_AWARDS_VEHICLE_OFFER
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.main_reward_bonus_model import MainRewardBonusModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.seniority_awards.tooltips.seniority_awards_compensation_tooltip import SeniorityAwardsCompensationTooltip
from gui.impl.lobby.seniority_awards.vehicle_selector import VehicleSelectorWindow
from gui.server_events.bonuses import VehiclesBonus
from helpers import dependency, time_utils
from frameworks.wulf import ViewSettings, WindowLayer, Array
from gui.game_control.seniority_awards_controller import SACOIN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl import backport
from gui.impl.pub.dialog_window import DialogButtons
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
from gui_lootboxes.gui.bonuses.bonuses_packers import LootBoxVehiclesBonusUIPacker
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
if typing.TYPE_CHECKING:
    from gui.impl.auxiliary.rewards_helper import SeniorityAwards
    from gui.impl.pub.dialog_window import DialogResult
_logger = logging.getLogger(__name__)
REG_EXP_QUEST_SUBTYPE = ':([Y, y]\\d*)|:([A,a,B,b][T,t])'
_T50_2_STYLE_NAME = backport.text(R.strings.vehicle_customization.special_style.t50_2())
_EXCLUDED_BONUSES = ('slots',)
_BONUSES_ORDER = ({'getName': 'selectableBonus'},
 {'getName': 'freeTokens_0'},
 {'getName': 'sacoin'},
 {'getName': 'freeTokens_2'},
 {'getName': 'crystal'},
 {'getName': 'credits'},
 {'getName': 'premium_plus'},
 {'getName': 'dossier_achievement'},
 {'getName': 'badge'},
 {'getLabel': _T50_2_STYLE_NAME},
 {'getName': 'customizations',
  'getIcon': 'style'},
 {'getIcon': 'projectionDecal'},
 {'getName': 'customizations',
  'getIcon': 'emblem'},
 {'getIcon': 'universalBook'},
 {'getIcon': 'recertificationForm'},
 {'getName': 'goodies',
  'getIcon': 'credits'},
 {'getName': 'goodies',
  'getIcon': 'xp'})
_MAX_MAIN_REWARDS = 2
_MAIN_BONUSES = (lambda bonus: bonus.getName() == 'selectableBonus', lambda bonus: bonus.getName() == 'credits' and bonus.getIsCompensation(), lambda bonus: bonus.getName() == 'crystal')

def _keySortOrder(bonus, _):
    for index, criteria in enumerate(_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_BONUSES_ORDER)


_SENIORITY_VEHICLES_ORDER = ('germany:G15_VK3601H_C', 'ussr:R197_KV_1S_MZ', 'germany:G158_VK2801_105_SPXXI', 'usa:A134_M24E2_SuperChaffee', 'usa:A130_Super_Hellcat', 'ussr:R160_T_50_2')

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
        if contentID == R.views.lobby.seniority_awards.tooltips.SeniorityAwardsCompensationTooltip():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData:
                return SeniorityAwardsCompensationTooltip(*tooltipData.specialArgs)
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _onLoading(self, completedQuests, data, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._onLoading(*args, **kwargs)
        saRewardType = _getSeniorityAwardsRewardType(completedQuests)
        self.__updateBonuses(data)
        self.__tooltipData = {}
        with self.viewModel.transaction() as vm:
            self.__setMainRewards(vm)
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
        self.viewModel.onOpenShop += self.__onOpenBtnClick
        self.viewModel.onSelectVehicle += self.__onSelectVehicleBtnClick

    def _finalize(self):
        self.__bonuses = None
        self.__vehicles = None
        self.viewModel.onOpenShop -= self.__onOpenBtnClick
        self.viewModel.onSelectVehicle -= self.__onSelectVehicleBtnClick
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
        for index, (bonus, tooltip) in enumerate(self.__bonuses, start=3):
            tooltipId = str(index)
            bonus.setTooltipId(tooltipId)
            bonus.setIndex(index)
            bonusesList.addViewModel(bonus)
            self.__tooltipData[tooltipId] = tooltip

        bonusesList.invalidate()

    def __setMainRewards(self, viewModel):
        mainRewardList = viewModel.getMainRewards()
        mainRewardList.clear()
        bonusesToRemove = []
        count = 0
        for criteria in _MAIN_BONUSES:
            if count >= _MAX_MAIN_REWARDS:
                break
            for bonus, tooltip in self.__bonuses:
                if count >= _MAX_MAIN_REWARDS:
                    break
                if criteria(bonus):
                    index = str(count)
                    bonus.setTooltipId(index)
                    bonus.setIndex(index)
                    mainRewardList.addViewModel(bonus)
                    self.__tooltipData[index] = tooltip
                    bonusesToRemove.append((bonus, tooltip))
                    count += 1

        for bonusToRemove in bonusesToRemove:
            self.__bonuses.remove(bonusToRemove)

        mainRewardList.invalidate()

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

    @th_async.th_async
    def __onSelectVehicleBtnClick(self, args=None):
        window = VehicleSelectorWindow(SENIORITY_AWARDS_VEHICLE_OFFER)
        window.load()
        result = yield th_async.th_await(window.wait())
        _logger.info('VehicleSelectorWindow return result=%s', result)
        if result.result == DialogButtons.CANCEL:
            return
        elif len(result.data) > 1:
            self.__replaceMainRewards(result.data)
            return
        else:
            mainRewardIndex = None
            if args is not None:
                mainRewardIndex = args.get('rewardIndex')
                if mainRewardIndex is not None:
                    mainRewardIndex = int(mainRewardIndex)
            self.__replaceMainRewardByIndex(first(result.data), mainRewardIndex)
            return

    def __replaceMainRewardByIndex(self, vehIntCD, index):
        mainRewardsList = self.getViewModel().getMainRewards()
        vehBonus = VehiclesBonus('vehicles', {vehIntCD: {'noCrew': True}})
        vehBonusModel = first(LootBoxVehiclesBonusUIPacker.pack(vehBonus))
        vehBonusTooltipModel = first(LootBoxVehiclesBonusUIPacker.getToolTip(vehBonus))
        if index is not None and vehBonusModel is not None:
            if len(mainRewardsList) > index >= 0:
                vehBonusModel.setIndex(str(index))
                vehBonusModel.setTooltipId(str(index))
                mainRewardsList.setViewModel(index, vehBonusModel)
                self.__tooltipData[str(index)] = vehBonusTooltipModel
        mainRewardsList.invalidate()
        return

    def __replaceMainRewards(self, vehiclesIntCDs):
        for index, vehIntCD in enumerate(vehiclesIntCDs):
            self.__replaceMainRewardByIndex(vehIntCD, index)


class SeniorityRewardAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, completedQuests=None, data=None, viewID=None):
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(viewID, completedQuests=completedQuests, data=data), layer=WindowLayer.TOP_WINDOW)
