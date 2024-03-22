# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/pages/progression_page.py
import logging
import typing
import SoundGroups
from adisp import adisp_process
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.clans.clan_cache import g_clanCache
from gui.clans.data_wrapper.clan_supply import PointStatus, DataNames
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.progression_model import ScreenStatus as ProgressionScreenStatus
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.stage_model import StageModel, StageStatus
from gui.impl.gen.view_models.views.lobby.clan_supply.stage_info_model import ScreenStatus as StageScreenStatus, StageInfoStatus
from gui.impl.lobby.clan_supply.bonus_packers import composeBonuses, findVehicle, getClanSupplyBonusPacker, BONUSES_ORDER
from gui.impl.lobby.clan_supply.clan_supply_helpers import showClanSupplyView
from gui.impl.lobby.clan_supply.sound_helper import SOUNDS
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.wgcg.clan_supply.contexts import PurchaseProgressionStageCtx
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.clans.data_wrapper import clan_supply
    from gui.impl.backport import TooltipData
    from gui.impl.gen.view_models.views.lobby.clan_supply.pages.progression_model import ProgressionModel
    from gui.impl.gen.view_models.views.lobby.clan_supply.clan_supply_vehicle_model import ClanSupplyVehicleModel
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)
DEFAULT_STAGE_ID = 1

class ProgressionPage(SubModelPresenter):
    __slots__ = ('__tooltips', '__rewardVehicleIntCD', '__selectedStageID', '__cachedProgressData', '__cachedSettingsData', '__rewardStyleID', '__isFindSelectedStageNeeded')
    __itemsCache = dependency.descriptor(IItemsCache)
    __webController = dependency.descriptor(IWebController)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, viewModel, parentView):
        self.__tooltips = {}
        self.__rewardVehicleIntCD = None
        self.__rewardStyleID = None
        self.__selectedStageID = None
        self.__cachedProgressData = None
        self.__cachedSettingsData = None
        self.__isFindSelectedStageNeeded = True
        super(ProgressionPage, self).__init__(viewModel, parentView)
        return

    @property
    def viewModel(self):
        return super(ProgressionPage, self).getViewModel()

    def initialize(self, *args, **kwargs):
        self.__updateState()
        super(ProgressionPage, self).initialize(*args, **kwargs)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionPage, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _getEvents(self):
        return super(ProgressionPage, self)._getEvents() + ((g_clanCache.clanSupplyProvider.onDataReceived, self.__onDataReceived),
         (g_clanCache.clanSupplyProvider.onDataFailed, self.__onDataFailed),
         (self.viewModel.onSelectStage, self.__onSelectStage),
         (self.viewModel.onPreviewClick, self.__onPreviewClick),
         (self.viewModel.onRefresh, self.__onRefresh),
         (self.viewModel.onBuyStage, self.__onBuyStage),
         (self.viewModel.stageInfo.onRefresh, self.__onStageInfoRefresh))

    def _getCallbacks(self):
        return (('cache.dynamicCurrencies.tourcoin', self.__updateBalance),)

    def __updateState(self):
        progressionSettingsObj = g_clanCache.clanSupplyProvider.getProgressionSettings()
        if progressionSettingsObj.isWaitingResponse:
            self.viewModel.setStatus(ProgressionScreenStatus.PENDING)
            self.viewModel.stageInfo.setStatus(StageScreenStatus.PENDING)
            return
        else:
            self.__cachedSettingsData = progressionSettingsObj.data
            if self.__cachedSettingsData is None:
                self.viewModel.setStatus(ProgressionScreenStatus.ERROR)
                self.viewModel.stageInfo.setStatus(StageScreenStatus.ERROR)
                return
            self.viewModel.setStatus(ProgressionScreenStatus.LOADED)
            progressionProgressObj = g_clanCache.clanSupplyProvider.getProgressionProgress()
            self.__cachedProgressData = progressionProgressObj.data
            if progressionProgressObj.isWaitingResponse:
                self.viewModel.stageInfo.setStatus(StageScreenStatus.PENDING)
            elif progressionProgressObj.data is None:
                self.viewModel.stageInfo.setStatus(StageScreenStatus.ERROR)
            else:
                self.viewModel.stageInfo.setStatus(StageScreenStatus.LOADED)
            self.__updateProgression(self.__cachedSettingsData, self.__cachedProgressData)
            return

    def __updateProgression(self, settingsData, progressData):
        if self.__isFindSelectedStageNeeded or self.__selectedStageID is None:
            self.__selectedStageID = self.__findInitialSelectedStage(progressData)
            if progressData is not None:
                self.__isFindSelectedStageNeeded = False
        with self.viewModel.transaction() as tx:
            if not settingsData.enabled:
                tx.setStatus(ProgressionScreenStatus.ERROR)
                return
            tx.setSelectedStageID(self.__selectedStageID)
            self.__rewardVehicleIntCD = self.__findVehicleRewardIntCD(settingsData)
            self.__rewardStyleID = self.__findStyleRewardID(settingsData)
            if not all((self.__rewardVehicleIntCD, self.__rewardStyleID)):
                tx.setStatus(ProgressionScreenStatus.ERROR)
                _logger.error('Can not find a vehicle or style in rewards.')
                return
            vehicle = self.__itemsCache.items.getItemByCD(self.__rewardVehicleIntCD)
            self.__fillVehicleModel(tx.vehicleInfo, vehicle)
            tx.setIsCompleted(self.__checkProgressionIsCompleted(progressData))
            tx.setIsMainRewardAvailable(self.__isMainRewardAvailable(settingsData, progressData))
            stages = tx.getStages()
            stages.clear()
            for stageID, stageData in sorted(settingsData.points.items()):
                stageProgress = progressData.points.get(stageID) if progressData is not None else None
                stages.addViewModel(self.__fillStageModel(stageID, stageData, stageProgress))

            stages.invalidate()
            self.__updateStageInfo(self.__selectedStageID, settingsData, progressData, model=tx)
        return

    @replaceNoneKwargsModel
    def __updateStageInfo(self, stageID, settingsData, progressData, model=None):
        stageSettings = settingsData.points.get(str(stageID))
        stageProgress = progressData.points.get(str(stageID)) if progressData is not None else None
        model.stageInfo.setId(stageID)
        model.stageInfo.setIsPremium(stageSettings.is_elite)
        model.stageInfo.setPrice(stageSettings.price)
        balance = self.__itemsCache.items.stats.dynamicCurrencies.get(Currency.TOUR_COIN, 0)
        model.stageInfo.setIsEnoughMoney(stageSettings.price <= balance)
        model.stageInfo.setDeficiencyAmount(stageSettings.price - balance)
        if stageProgress is None:
            model.stageInfo.setStageStatus(StageInfoStatus.UNAVAILABLE)
        elif stageProgress.status == PointStatus.PURCHASED:
            model.stageInfo.setStageStatus(StageInfoStatus.PURCHASED)
        elif stageProgress.status == PointStatus.AVAILABLE:
            model.stageInfo.setStageStatus(StageInfoStatus.AVAILABLE)
        rewards = model.stageInfo.getRewards()
        rewards.clear()
        self.__tooltips.clear()
        packBonusModelAndTooltipData(composeBonuses(self.__validateRewards(stageSettings.rewards), bonusesOrder=BONUSES_ORDER), rewards, self.__tooltips, packer=getClanSupplyBonusPacker(isProgression=True))
        rewards.invalidate()
        return

    def __onDataReceived(self, dataName, data):
        if dataName not in (DataNames.PROGRESSION_PROGRESS, DataNames.PROGRESSION_SETTINGS):
            return
        if dataName == DataNames.PROGRESSION_SETTINGS:
            self.viewModel.setStatus(ProgressionScreenStatus.LOADED)
            self.__cachedSettingsData = data
        isSettingsLoaded = self.viewModel.getStatus() is ProgressionScreenStatus.LOADED
        if dataName == DataNames.PROGRESSION_PROGRESS and isSettingsLoaded:
            self.viewModel.stageInfo.setStatus(StageScreenStatus.LOADED)
            self.__cachedProgressData = data
        if all((self.__cachedSettingsData, self.__cachedProgressData)):
            self.__updateProgression(self.__cachedSettingsData, self.__cachedProgressData)
        else:
            self.__updateState()

    def __onDataFailed(self, dataName):
        if dataName == DataNames.PROGRESSION_PROGRESS:
            self.viewModel.stageInfo.setStatus(StageScreenStatus.ERROR)
        elif dataName == DataNames.PROGRESSION_SETTINGS:
            self.viewModel.setStatus(ProgressionScreenStatus.ERROR)

    def __onSelectStage(self, kwargs):
        self.__selectedStageID = int(kwargs.get('id'))
        with self.viewModel.transaction() as tx:
            tx.setSelectedStageID(self.__selectedStageID)
            self.__updateStageInfo(self.__selectedStageID, self.__cachedSettingsData, self.__cachedProgressData, model=tx)

    def __onPreviewClick(self):
        if not all((self.__rewardVehicleIntCD, self.__rewardStyleID)):
            _logger.error('Can not find a reward vehicle or style.')
            return
        else:
            style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, self.__rewardStyleID)
            if style is None:
                _logger.error('Style is invalid, id=%s', self.__rewardStyleID)
                return

            def __onPreviewCallback():
                SoundGroups.g_instance.setState(SOUNDS.STATE_HANGAR_PLACE, SOUNDS.STATE_HANGAR_PLACE_CLANS)
                showClanSupplyView()

            showVehiclePreviewWithoutBottomPanel(self.__rewardVehicleIntCD, style=style, backCallback=__onPreviewCallback, backBtnLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.clanSupply()), previewAlias=VIEW_ALIAS.LOBBY_STRONGHOLD)
            return

    def __onRefresh(self):
        self.__updateState()

    def __onStageInfoRefresh(self):
        self.__updateState()

    @adisp_process
    def __onBuyStage(self, kwargs):
        stageID = int(kwargs.get('id'))
        self.viewModel.stageInfo.setIsBuyLoading(True)
        response = yield self.__webController.sendRequest(ctx=PurchaseProgressionStageCtx(stageID, self.viewModel.stageInfo.getPrice()))
        if self.viewModel is None:
            return
        else:
            self.viewModel.stageInfo.setIsBuyLoading(False)
            if not response.isSuccess():
                _logger.warning('Failed to purchase stage. Code: %s.', response.getCode())
            else:
                self.__selectedStageID = stageID
            self.__updateState()
            return

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        price = model.stageInfo.getPrice()
        balance = self.__itemsCache.items.stats.dynamicCurrencies.get(Currency.TOUR_COIN, 0)
        model.stageInfo.setIsEnoughMoney(price <= balance)
        model.stageInfo.setDeficiencyAmount(price - balance)

    @staticmethod
    def __fillStageModel(stageID, stageSettings, stageProgress):
        model = StageModel()
        model.setId(int(stageID))
        model.setIsPremium(stageSettings.is_elite)
        if stageProgress is None:
            model.setStatus(StageStatus.DISABLED)
        elif stageProgress.status == PointStatus.PURCHASED:
            model.setStatus(StageStatus.OPENED)
        elif stageProgress.status == PointStatus.AVAILABLE:
            model.setStatus(StageStatus.AVAILABLE)
        return model

    @staticmethod
    def __fillVehicleModel(vehicleModel, vehicle):
        fillVehicleModel(vehicleModel, vehicle)
        vehicleModel.setFullName(vehicle.userName)

    @staticmethod
    def __findInitialSelectedStage(progressData):
        return int(progressData.last_purchased) if progressData is not None and progressData.last_purchased is not None else DEFAULT_STAGE_ID

    @staticmethod
    def __checkProgressionIsCompleted(progressData):
        if progressData is None:
            return False
        else:
            _, stageProgress = sorted(progressData.points.items(), key=lambda i: int(i[0]))[-1]
            return stageProgress.status == PointStatus.PURCHASED

    @staticmethod
    def __isMainRewardAvailable(settingsData, progressData):
        if progressData is None:
            return False
        else:
            lastStageID, _ = sorted(settingsData.points.items(), key=lambda i: int(i[0]))[-1]
            stageProgress = progressData.points.get(lastStageID)
            return stageProgress is not None and stageProgress.status == PointStatus.AVAILABLE

    @staticmethod
    def __findVehicleRewardIntCD(pointSettings):
        vehIntCD = None
        for point in pointSettings.points.values():
            vehIntCD = findVehicle(point.rewards)
            if vehIntCD is not None:
                break

        return vehIntCD

    @staticmethod
    def __findStyleRewardID(pointSettings):
        styleID = None
        _, stageSettings = sorted(pointSettings.points.items(), key=lambda i: int(i[0]))[-1]
        customizationReward = findFirst(lambda r: r[0] == 'customizations', stageSettings.rewards.items())
        if customizationReward is None:
            return styleID
        else:
            styleReward = findFirst(lambda item: item['custType'] == 'style', customizationReward[1])
            if styleReward is not None:
                styleID = styleReward['id']
            return styleID

    def __validateRewards(self, rewards):
        result = {}
        for key, value in rewards.items():
            if isinstance(value, dict):
                value = self.__validateRewards(value)
            if isinstance(key, (str, unicode)) and key.isdigit():
                result[int(key)] = value
            result[key] = value

        return result
