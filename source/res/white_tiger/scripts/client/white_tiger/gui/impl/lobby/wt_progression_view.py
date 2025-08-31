# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_progression_view.py
import logging
from account_helpers.AccountSettings import AccountSettings, EVENT_LAST_STAMPS_SEEN, EVENT_LAST_LEVEL_SEEN
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_progression_model import WtProgressionModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_progression_level_model import WtProgressionLevelModel
from white_tiger.gui.impl.lobby import wt_event_sound
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtHiddenCustomizationIconUIPacker
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
_logger = logging.getLogger(__name__)

class WTProgressionView(SubModelPresenter):
    __slots__ = ('__tooltipData',)
    __gameEventController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, viewModel, parentView):
        super(WTProgressionView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(WTProgressionView, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(WTProgressionView, self).initialize(args, kwargs)
        self.__updateModel()
        self.__addListeners()
        if self.__gameEventController.needToShowOutroVideo():
            self.__gameEventController.showOutroVideo()

    def finalize(self):
        self.__removeListeners()
        self.__tooltipData = None
        super(WTProgressionView, self).finalize()
        return

    def getTooltipItems(self):
        return self.__tooltipData

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model)

    def __fillProgression(self, model):
        self.__tooltipData = {}
        previousLevel = AccountSettings.getSettings(EVENT_LAST_LEVEL_SEEN)
        previousStamps = AccountSettings.getSettings(EVENT_LAST_STAMPS_SEEN)
        currentStamps = self.__gameEventController.getCurrentStampsCount()
        stampsPerLevel = self.__gameEventController.getStampsCountPerLevel()
        currentLevel = self.__gameEventController.getCurrentLevel()
        hasMadeProgress = previousLevel < currentLevel
        model.setStampsCurrent(currentStamps)
        model.setStampsPrevious(previousStamps)
        model.setStampsNeededPerStage(stampsPerLevel)
        model.setCurrentStage(currentLevel)
        model.setPreviousStage(previousLevel)
        if hasMadeProgress:
            wt_event_sound.playProgressionLevelChanged()
        AccountSettings.setSettings(EVENT_LAST_LEVEL_SEEN, currentLevel)
        AccountSettings.setSettings(EVENT_LAST_STAMPS_SEEN, currentStamps)
        progression = self.__getItemsProgression()
        stages = model.getStages()
        stages.clear()
        stages.reserve(len(progression))
        for _, rewards in progression:
            item = WtProgressionLevelModel()
            rewardsList = item.getRewards()
            rewardsList.clear()
            rewardsList.reserve(len(rewards))
            packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getWtHiddenCustomizationIconUIPacker())
            rewardsList.invalidate()
            stages.addViewModel(item)

        stages.invalidate()

    def __getItemsProgression(self):
        result = []
        for data in self.__gameEventController.getConfig().progression:
            rewards = self.__gameEventController.getQuestRewards(data.get('quest', ''))
            result.append((data.get('level', 0), rewards))

        return result

    def __addListeners(self):
        self.__gameEventController.onProgressUpdated += self.__updateModel

    def __removeListeners(self):
        self.__gameEventController.onProgressUpdated -= self.__updateModel
