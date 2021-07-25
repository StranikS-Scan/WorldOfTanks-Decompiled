# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_reward_award_view.py
import logging
import re
from collections import defaultdict
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, getRewardTooltipContent
from gui.impl.backport import TooltipData, BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicle_renderer_model import SeniorityAwardsVehicleRendererModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_reward_award_view_model import SeniorityRewardAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.impl.auxiliary.rewards_helper import getSeniorityAwardsRewardsAndBonuses
from gui.impl.auxiliary.rewards_helper import DEF_MODEL_PRESENTERS
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from gui.impl.auxiliary.rewards_helper import LootRewardDefModelPresenter
from gui.shared.event_dispatcher import showSeniorityInfoWindow
from gui.shared.utils.functions import getAbsoluteUrl, stripHTMLTags
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
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
    __slots__ = ('__bonuses', '__vehicles', '__tooltipData')
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, contentResId, *args, **kwargs):
        settings = ViewSettings(contentResId)
        settings.model = SeniorityRewardAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeniorityRewardAwardView, self).__init__(settings)

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

    def _initialize(self, questID, data):
        super(SeniorityRewardAwardView, self)._initialize()
        self.viewModel.onCloseAction += self.__onWindowClose
        self.viewModel.onOpenBtnClick += self.__onOpenBtnClick
        questYearsType = None
        seniorityLvlSearch = re.search(REG_EXP_QUEST_SUBTYPE, questID) if questID else None
        if seniorityLvlSearch is not None:
            questYearsType = seniorityLvlSearch.groups()[0] or seniorityLvlSearch.groups()[1]
        self.__updateBonuses(data)
        self.__tooltipData = {}
        self.__setRewards()
        self.__setBonuses()
        if questYearsType is not None:
            self.viewModel.setCategory(questYearsType.upper())
        config = self.__lobbyContext.getServerSettings().getSeniorityAwardsConfig()
        hasToken = self.__itemsCache.items.tokens.getToken(config.getSecretBoxToken()) is not None
        self.viewModel.setSecretBoxAvailable(hasToken)
        return

    def _finalize(self):
        self.__bonuses = None
        self.__vehicles = None
        self.viewModel.onCloseAction -= self.__onWindowClose
        self.viewModel.onOpenBtnClick -= self.__onOpenBtnClick
        super(SeniorityRewardAwardView, self)._finalize()
        return

    def __setRewards(self):
        with self.viewModel.transaction() as vm:
            vehiclesList = vm.getVehicles()
            vehiclesList.clear()
            for vehicle in self.__vehicles:
                rendererModel = SeniorityAwardsVehicleRendererModel()
                rendererModel.setVehicleCD(str(vehicle.vehicleCD))
                rendererModel.setImgSource(self.__getVehImgResource(vehicle.name))
                vehiclesList.addViewModel(rendererModel)

            vehiclesList.invalidate()

    def __setBonuses(self):
        with self.viewModel.transaction() as vm:
            bonusesList = vm.getBonuses()
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
                bonusesList.addViewModel(rendererModel)
                self.__tooltipData[index] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))

            bonusesList.invalidate()
        return

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
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AWARD_VEHICLE, specialArgs=(vehicleCD,
             None,
             None,
             None,
             None,
             None,
             True)) if tooltipId == SeniorityAwardsVehicleRendererModel.TOOLTIP_VEHICLE_REWARD else None

    def __updateBonuses(self, data):
        bonuses, vehicles = getSeniorityAwardsRewardsAndBonuses(data, maxAwardCount=_BONUSES_COUNT, excluded=_EXCLUDED_BONUSES, sortKey=lambda b: _keySortOrder(b, _getBonusOrder()))
        self.__bonuses = bonuses or []
        self.__vehicles = sorted(vehicles, key=_vehiclesSortOrder) or []

    @staticmethod
    def __getVehImgResource(vehicleName):
        return getIconResourceName(getNationLessName(vehicleName))

    @staticmethod
    def __onOpenBtnClick():
        showSeniorityInfoWindow()


class SeniorityRewardAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questID=None, data=None, viewID=None):
        super(SeniorityRewardAwardWindow, self).__init__(content=SeniorityRewardAwardView(viewID, questID=questID, data=data))
