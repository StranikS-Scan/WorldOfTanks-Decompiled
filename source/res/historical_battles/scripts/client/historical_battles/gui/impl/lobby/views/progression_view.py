# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/progression_view.py
import typing
from frameworks.wulf import Array
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from historical_battles.gui.gui_constants import HB_DISCOUNT_ENTITLEMENT_PREFIX
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.progress_level_model import ProgressLevelModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.mark_detail_model import MarkDetailModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.progression_view_model import ProgressionViewModel
from historical_battles.gui.bonuses.bonus_packer import getBonusPacker
from historical_battles.gui.shared.event_dispatcher import showShopView, showProgressionVideo
from historical_battles.gui.sounds.sound_hangar_controller import SoundHangarController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.bonuses import SimpleBonus

class ProgressionView(SubModelPresenter):
    __slots__ = ('__tooltipData',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __gameEventController = dependency.descriptor(IGameEventController)
    __progressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self, viewModel, parentView):
        super(ProgressionView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(ProgressionView, self).initialize(args, kwargs)
        self.__updateModel()
        SoundHangarController.onEnterProgressionView()

    def finalize(self):
        self.__progressionController.saveCurPoints()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onPreviewClicked, self.__onPreviewClicked),
         (self.viewModel.onVehicleBuyClicked, self.__onVehicleBuyClicked),
         (self.viewModel.onShowVideoClicked, self.__onShowVideoClicked),
         (self.__progressionController.onProgressPointsUpdated, self.__updateProgressionPoints),
         (self.__progressionController.onSettingsChanged, self.__updateModel),
         (self.__itemsCache.onSyncCompleted, self.__onItemsCacheSyncCompleted))

    @staticmethod
    def __checkDiscountInRewards(rewards):
        for reward in rewards:
            if reward.getName() == 'entitlements':
                entitlementId = reward.getValue().id
                if entitlementId.startswith(HB_DISCOUNT_ENTITLEMENT_PREFIX):
                    discount = entitlementId.split('_')[-1]
                    return discount.isdigit() and int(discount)
                return 0
            continue

    def __onPreviewClicked(self):
        pass

    def __onVehicleBuyClicked(self):
        showShopView()

    def __updateProgressionPoints(self):
        if not self.__progressionController.isEnabled:
            return
        data = self.__progressionController.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            model.setCurProgressPoints(data['curPoints'])
            self.__updateDiscount(data)
            self.__updateProgressionNarratives(model)

    def __updateModel(self):
        if not self.__progressionController.isEnabled:
            return
        with self.viewModel.transaction() as model:
            model.setFrontName(self.__gameEventController.frontController.getSelectedFront().getName())
            model.setHasVehicle(self.__gameEventController.heroTank.hasHeroVehicle())
            self.__updateProgression(model)
            self.__updateProgressionNarratives(model)

    def __updateProgression(self, model):
        data = self.__progressionController.getProgressionData()
        model.setCurProgressPoints(data['curPoints'])
        model.setPrevProgressPoints(data['prevPoints'])
        points = Array()
        for score in data['pointsForLevel']:
            points.addNumber(score)

        model.setPointsForLevel(points)
        progressionLevels = model.getProgressLevels()
        progressionLevels.clear()
        for levelData in data['progressionLevels']:
            level = ProgressLevelModel()
            rewards = level.getRewards()
            bonuses = levelData['rewards']
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getBonusPacker())
            progressionLevels.addViewModel(level)

        self.__updateDiscount(data)
        progressionLevels.invalidate()

    def __updateDiscount(self, data):
        discount = 0
        discountsByLevel = data['discountsByLevel']
        curPoints = data['curPoints']
        for level, levelPoints in enumerate(data['pointsForLevel'], 1):
            if curPoints < levelPoints:
                break
            discount = discountsByLevel.get(level, discount)

        self.viewModel.setVehicleDiscount(discount)

    def __onItemsCacheSyncCompleted(self, *_):
        self.viewModel.setHasVehicle(self.__gameEventController.heroTank.hasHeroVehicle())

    def __updateProgressionNarratives(self, model):
        narratives = model.getMarksDetails()
        narratives.clear()
        narrativesData = self.__gameEventController.narrativesConfig
        frontName = self.__gameEventController.frontController.getSelectedFront().getName()
        finishedStage = self.__progressionController.getCurrentStageData().get('finishedStage')
        sortedNarrativeConfigs = sorted(narrativesData, key=lambda x: x.unlockLevel)
        for narrativeConfig in sortedNarrativeConfigs:
            if narrativeConfig.frontType != frontName:
                continue
            markDetail = MarkDetailModel()
            markDetail.setLocked(narrativeConfig.unlockLevel > finishedStage)
            markDetail.setVideoUrl(narrativeConfig.videoSrc)
            narratives.addViewModel(markDetail)

        narratives.invalidate()

    def __onShowVideoClicked(self, args):
        videoName = args.get('url')
        showProgressionVideo(videoName, parent=self.getParentWindow())
