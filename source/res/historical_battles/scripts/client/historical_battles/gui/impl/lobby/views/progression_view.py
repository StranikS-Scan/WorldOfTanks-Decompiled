# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/progression_view.py
import typing
from frameworks.wulf import Array
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from historical_battles.gui.gui_constants import HB_DISCOUNT_ENTITLEMENT_PREFIX
from historical_battles.gui.impl.gen.view_models.views.lobby.progression.progress_level_model import ProgressLevelModel
from historical_battles.gui.impl.gen.view_models.views.lobby.progression.progression_view_model import ProgressionViewModel
from historical_battles.gui.impl.lobby.views.bonus_packer import getBonusPacker
from historical_battles.gui.shared.event_dispatcher import showHBHangar, showShopView, showInfoPage
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.bonuses import SimpleBonus

class ProgressionView(SubModelPresenter):
    HBProgression = dependency.descriptor(IHBProgressionOnTokensController)
    gameEventController = dependency.descriptor(IGameEventController)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData',)

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

    def finalize(self):
        self.HBProgression.saveCurPoints()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAboutClicked, self.__onAboutClicked),
         (self.viewModel.onPreviewClicked, self.__onPreviewClicked),
         (self.viewModel.onVehicleBuyClicked, self.__onVehicleBuyClicked),
         (self.HBProgression.onProgressPointsUpdated, self.__updateProgressionPoints),
         (self.HBProgression.onSettingsChanged, self.__updateModel),
         (self.itemsCache.onSyncCompleted, self.__onItemsCacheSyncCompleted))

    @staticmethod
    def __onClose():
        showHBHangar()

    @staticmethod
    def __onAboutClicked():
        showInfoPage()

    @staticmethod
    def __checkDiscountInRewards(rewards):
        for reward in rewards:
            if reward.getName() == 'entitlements':
                entitlementId = reward.getValue().id
                if entitlementId.startswith(HB_DISCOUNT_ENTITLEMENT_PREFIX):
                    discount = entitlementId.split('_')[-1]
                    if discount.isdigit():
                        return int(discount)
                    return 0

    def __onPreviewClicked(self):
        pass

    def __onVehicleBuyClicked(self):
        showShopView()

    def __updateProgressionPoints(self):
        if not self.HBProgression.isEnabled:
            return
        data = self.HBProgression.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            model.setCurProgressPoints(data['curPoints'])
            self.__updateDiscount(data)

    def __updateModel(self):
        if not self.HBProgression.isEnabled:
            return
        data = self.HBProgression.getProgressionData()
        with self.viewModel.transaction() as model:
            model.setHasVehicle(self.gameEventController.heroTank.hasHeroVehicle())
            self.__updateProgression(data, model)

    def __updateProgression(self, data, model):
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
        self.viewModel.setHasVehicle(self.gameEventController.heroTank.hasHeroVehicle())
