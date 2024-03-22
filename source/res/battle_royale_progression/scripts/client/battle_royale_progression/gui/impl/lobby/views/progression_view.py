# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/progression_view.py
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progress_level_model import ProgressLevelModel
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_view_model import ProgressionViewModel
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
from battle_royale_progression.gui.impl.lobby.views.quests_packer import getEventUIDataPacker
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.server_events.events_helpers import EventInfoModel
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.server_events import IEventsCache

class ProgressionView(SubModelPresenter):
    battleRoyale = dependency.descriptor(IBattleRoyaleController)
    brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    eventsCache = dependency.descriptor(IEventsCache)
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
        self.brProgression.saveCurPoints()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAboutClicked, self.__onAboutClicked),
         (self.brProgression.onProgressPointsUpdated, self.__updateProgressionPoints),
         (self.brProgression.onSettingsChanged, self.__updateModel),
         (self.eventsCache.onSyncCompleted, self.__onSyncCompleted))

    def __onClose(self):
        event_dispatcher.showHangar()

    def __onAboutClicked(self):
        self.battleRoyale.openInfoPageWindow()

    def __updateMissionVisitedArray(self, missionVisitedArray, questsIDs):
        missionVisitedArray.clear()
        missionVisitedArray.reserve(len(questsIDs))
        for questID in questsIDs:
            missionCompletedVisited = not self.eventsCache.questsProgress.getQuestCompletionChanged(questID)
            missionVisitedArray.addBool(missionCompletedVisited)

        missionVisitedArray.invalidate()

    def __onSyncCompleted(self, *_):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgressionData()
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['battleQuests'].keys())
            self.__markAsVisited(data)

    def __updateProgressionPoints(self):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            model.setCurProgressPoints(data['curPoints'])

    def __updateModel(self):
        if not self.brProgression.isEnabled:
            return
        data = self.brProgression.getProgressionData()
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateProgression(data, model)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['battleQuests'].keys())
            self.__markAsVisited(data)

    def __updateProgression(self, data, model):
        model.setCurProgressPoints(data['curPoints'])
        model.setPrevProgressPoints(data['prevPoints'])
        model.setPointsForLevel(data['pointsForLevel'])
        progressionLevels = model.getProgressLevels()
        progressionLevels.clear()
        for levelData in data['progressionLevels']:
            level = ProgressLevelModel()
            rewards = level.getRewards()
            bonuses = levelData['rewards']
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getBonusPacker())
            progressionLevels.addViewModel(level)

        progressionLevels.invalidate()

    def __updateBattleQuestsCards(self, battleQuestsModel, data):
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        battleQuestsModel.setCurrentTimerDate(newCountdownVal)
        questsList = battleQuestsModel.getTasksBattle()
        questsList.clear()
        bonusIndexTotal = len(self.__tooltipData)
        for _, quest in data['battleQuests'].items():
            packer = getEventUIDataPacker(quest)
            questModels = packer.pack()
            bonusTooltipList = packer.getTooltipData()
            for bonusIndex, item in enumerate(questModels.getBonuses()):
                tooltipIdx = str(bonusIndexTotal)
                item.setTooltipId(tooltipIdx)
                if bonusTooltipList:
                    self.__tooltipData[tooltipIdx] = bonusTooltipList[str(bonusIndex)]
                bonusIndexTotal += 1

            questsList.addViewModel(questModels)

        questsList.invalidate()

    def __markAsVisited(self, data):
        for seenQuestID in data['battleQuests'].keys():
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
