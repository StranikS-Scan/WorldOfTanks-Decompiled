# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
import re
from collections import defaultdict
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.game_control.seniority_awards_controller import SACOIN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, getRewardTooltipContent
from gui.impl.backport import TooltipData, BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicle_renderer_model import SeniorityAwardsVehicleRendererModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_award_view_model import SeniorityRewardAwardViewModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_bonus_renderer_model import SeniorityAwardsBonusRendererModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.impl.auxiliary.rewards_helper import getSeniorityAwardsRewardsAndBonuses
from gui.impl.auxiliary.rewards_helper import DEF_MODEL_PRESENTERS
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from gui.impl.auxiliary.rewards_helper import LootRewardDefModelPresenter
from gui.shared.event_dispatcher import showShop
from gui.shared.utils.functions import getAbsoluteUrl, stripHTMLTags
from lunar_ny import ILunarNYController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
_logger = logging.getLogger(__name__)
REG_EXP_QUEST_SUBTYPE = ':([Y, y]\\d*)|:([A,a,B,b][T,t])'
_BONUSES_COUNT = 9
_EXCLUDED_BONUSES = ('slots',)
_SENIORITY_BONUSES_ORDER = (('crystal', 'crystal'),
 ('credits', 'credits'),
 ('crewBooks', 'personalBook'),
 ('crewBooks', 'universalBook'),
 ('customizations', 'projectionDecal'),
 ('premium_plus', 'premium_plus'),
 ('goodies', 'xp'),
 ('goodies', 'credits'),
 ('tokens', 'bonus_battle'),
 ('dossier', 'badge'),
 ('customizations', 'style'),
 ('customizations', 'emblem'),
 ('dossier', 'achievement'))
_SENIORITY_VEHICLES_ORDER = ('ussr:R160_T_50_2', 'usa:A130_Super_Hellcat', 'usa:A134_M24E2_SuperChaffee')

def _getBonusOrder():
    bonusOrder = defaultdict(dict)
    for priority, (bonusType, bonusSubtype) in enumerate(_SENIORITY_BONUSES_ORDER):
        bonusOrder[bonusType].update({bonusSubtype: priority})

    return bonusOrder


def _keySortOrder(bonus, bonusOrder):
    bonusName = bonus.bonusName
    if bonusName in bonusOrder:
        bonusSubtypes = bonusOrder.get(bonusName, {})
        for bonusSubtype, priority in bonusSubtypes.iteritems():
            if any([ bonusSubtype in img for img in bonus.images.values() if img ]):
                return priority

    return len(_SENIORITY_BONUSES_ORDER)


def _vehiclesSortOrder(vehicle):
    return _SENIORITY_VEHICLES_ORDER.index(vehicle.name) if vehicle.name in _SENIORITY_VEHICLES_ORDER else len(_SENIORITY_VEHICLES_ORDER)


class SeniorityRewardAwardView(ViewImpl):
    __slots__ = ('__bonuses', '__vehicles', '__specialCurrencies', '__tooltipData')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __NYController = dependency.descriptor(IFestivityController)
    __lunarNYController = dependency.descriptor(ILunarNYController)

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

    def _onLoading(self, questID, data):
        questYearsType = None
        seniorityLvlSearch = re.search(REG_EXP_QUEST_SUBTYPE, questID) if questID else None
        if seniorityLvlSearch is not None:
            questYearsType = seniorityLvlSearch.groups()[0] or seniorityLvlSearch.groups()[1]
        self.__updateBonuses(data)
        self.__tooltipData = {}
        with self.viewModel.transaction() as vm:
            self.__setRewards(vm)
            self.__setBonuses(vm)
            self.__setSpecialCurrency(vm)
            vm.setIsShopOnOpenLocked(self.__needBlockShopTransition)
            if questYearsType is not None:
                vm.setCategory(questYearsType.upper())
        return

    def _initialize(self, *args, **kwargs):
        super(SeniorityRewardAwardView, self)._initialize(*args, **kwargs)
        self.viewModel.onCloseAction += self.__onWindowClose
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick

    def _finalize(self):
        self.__bonuses = None
        self.__vehicles = None
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        super(SeniorityRewardAwardView, self)._finalize()
        return

    @property
    def __needBlockShopTransition(self):
        newYearBlock = self.__NYController.isEnabled() or self.__NYController.isPostEvent()
        lunarNYBlock = self.__lunarNYController.isActive()
        return not self.__specialCurrencies.get(SACOIN) or newYearBlock or lunarNYBlock

    def __setRewards(self, viewModel):
        vehiclesList = viewModel.getVehicles()
        vehiclesList.clear()
        for vehicle in self.__vehicles:
            rendererModel = SeniorityAwardsVehicleRendererModel()
            rendererModel.setVehicleCD(str(vehicle.vehicleCD))
            rendererModel.setImgSource(self.__getVehImgResource(vehicle.name))
            rendererModel.setVehicleName(vehicle.userName)
            vehiclesList.addViewModel(rendererModel)

        vehiclesList.invalidate()

    def __setBonuses(self, viewModel):
        bonusesList = viewModel.getBonuses()
        bonusesList.clear()
        for index, bonus in enumerate(self.__bonuses):
            if bonus.get('imgSource') is not None:
                bonus['imgSource'] = getAbsoluteUrl(bonus['imgSource'])
            if bonus.get('label') is not None:
                bonus['label'] = stripHTMLTags(bonus['label'])
            presenters = DEF_MODEL_PRESENTERS.copy()
            presenters[BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT] = LootRewardDefModelPresenter()
            modelPresenter = getRewardRendererModelPresenter(bonus, presenters=presenters)
            rendererModel = modelPresenter.getModel(bonus, index)
            tooltipId = str(index)
            bonusModel = SeniorityAwardsBonusRendererModel()
            bonusModel.setLabelStr(rendererModel.getLabelStr())
            bonusModel.setIcon(rendererModel.getIcon())
            bonusModel.setTooltipId(tooltipId)
            bonusModel.setBonusName(rendererModel.getRewardName())
            bonusesList.addViewModel(bonusModel)
            self.__tooltipData[tooltipId] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

        bonusesList.invalidate()
        return

    def __setSpecialCurrency(self, viewModel):
        currencyCount = self.__specialCurrencies.get(SACOIN)
        if currencyCount:
            viewModel.setSpecialCurrencyCount(currencyCount)

    def __onWindowClose(self, _=None):
        self.destroyWindow()

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
             True)) if tooltipId == SeniorityAwardsVehicleRendererModel.TOOLTIP_VEHICLE_REWARD else None

    def __updateBonuses(self, data):
        seniorityAwards = getSeniorityAwardsRewardsAndBonuses(data, maxAwardCount=_BONUSES_COUNT, excluded=_EXCLUDED_BONUSES, sortKey=lambda b: _keySortOrder(b, _getBonusOrder()))
        self.__bonuses = seniorityAwards.bonuses or []
        self.__vehicles = sorted(seniorityAwards.vehicles, key=_vehiclesSortOrder) or []
        self.__specialCurrencies = seniorityAwards.currencies or {}

    @staticmethod
    def __getVehImgResource(vehicleName):
        return getIconResourceName(getNationLessName(vehicleName))

    def __onOpenBtnClick(self):
        if not self.viewModel.getIsShopOnOpenLocked():
            showShop(getPlayerSeniorityAwardsUrl())
        else:
            self.destroyWindow()


class SeniorityRewardAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questID=None, data=None, viewID=None):
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(viewID, questID=questID, data=data))
