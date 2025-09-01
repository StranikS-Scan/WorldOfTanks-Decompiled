# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/progression_view.py
import typing
import SoundGroups
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from comp7_light.gui.impl.gen.view_models.views.lobby.progression.progress_level_model import ProgressLevelModel
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_packers import getComp7LightBonusPacker, getComp7LightEventUIDataPacker
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7_light.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7_light.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7_light.gui.shared.event_dispatcher import showComp7LightInfoPage
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from comp7_light.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_LIGHT_TOOLTIPS
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.server_events.events_helpers import EventInfoModel
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from comp7_light.gui.impl.gen.view_models.views.lobby.progression.progression_view_model import ProgressionViewModel

class ProgressionView(SubModelPresenter):
    __slots__ = ('__tooltipData', '__bonuses')
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, viewModel, parentView):
        super(ProgressionView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}
        self.__bonuses = {}

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self.getTooltipData(event)
            if tooltipId == COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                if window is None:
                    return
                window.load()
                return window
        return super(ProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            fromIndex = int(event.getArgument('fromIndex'))
            index = int(event.getArgument('index'))
            bonuses = [ bonus for bonus in self.__bonuses[index][fromIndex:] ]
            return AdditionalRewardsTooltip(bonuses)
        return super(ProgressionView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(ProgressionView, self).initialize(args, kwargs)
        self.__updateModel()
        self.__updateSchedule()
        SoundGroups.g_instance.playSound2D('comp_7_progression_enter')

    def finalize(self):
        SoundGroups.g_instance.playSound2D('comp_7_progression_exit')
        self.__comp7LightProgressionController.saveCurPoints()
        self.__bonuses.clear()
        super(ProgressionView, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAboutClicked, self.__onAboutClicked),
         (self.__comp7LightProgressionController.onProgressPointsUpdated, self.__updateProgressionPoints),
         (self.__comp7LightProgressionController.onSettingsChanged, self.__updateModel),
         (self.viewModel.scheduleInfo.season.pollServerTime, self.__updateSchedule),
         (self.__eventsCache.onSyncCompleted, self.__onSyncCompleted))

    def __onClose(self):
        showHangar()

    def __onAboutClicked(self):
        showComp7LightInfoPage()

    def __updateMissionVisitedArray(self, missionVisitedArray, questsIDs):
        missionVisitedArray.clear()
        missionVisitedArray.reserve(len(questsIDs))
        for questID in questsIDs:
            missionCompletedVisited = not self.__eventsCache.questsProgress.getQuestCompletionChanged(questID)
            missionVisitedArray.addBool(missionCompletedVisited)

        missionVisitedArray.invalidate()

    def __onSyncCompleted(self, *_):
        if not self.__comp7LightProgressionController.isEnabled:
            return
        data = self.__comp7LightProgressionController.getProgressionData()
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['battleQuests'].keys())
            self.__markAsVisited(data)
            self.__updateSchedule()

    def __updateProgressionPoints(self):
        if not self.__comp7LightProgressionController.isEnabled:
            return
        data = self.__comp7LightProgressionController.getProgessionPointsData()
        with self.viewModel.transaction() as model:
            model.setCurProgressPoints(data['curPoints'])

    def __updateModel(self):
        if not self.__comp7LightProgressionController.isEnabled:
            return
        data = self.__comp7LightProgressionController.getProgressionData()
        with self.viewModel.transaction() as model:
            self.__updateBattleQuestsCards(model.battleQuests, data)
            self.__updateProgression(data, model)
            self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), data['questsOrder'])
            self.__markAsVisited(data)

    def __updateSchedule(self):
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        self.viewModel.battleQuests.setCurrentTimerDate(newCountdownVal)
        comp7_core_model_helpers.setScheduleInfo(self.viewModel.scheduleInfo, self.__comp7LightController, COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)

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
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipData, getComp7LightBonusPacker())
            progressionLevels.addViewModel(level)

        progressionLevels.invalidate()

    def __updateBattleQuestsCards(self, battleQuestsModel, data):
        questsList = battleQuestsModel.getTasksBattle()
        questsList.clear()
        bonusIndexTotal = len(self.__tooltipData)
        for index, questId in enumerate(data['questsOrder']):
            quest = data['battleQuests'][questId]
            packer = getComp7LightEventUIDataPacker(quest)
            questModels = packer.pack()
            bonusTooltipList = packer.getTooltipData()
            self.__bonuses[index] = questModels.getBonuses()
            for bonusIndex, item in enumerate(questModels.getBonuses()):
                tooltipIdx = str(bonusIndexTotal)
                item.setTooltipId(tooltipIdx)
                if bonusTooltipList:
                    self.__tooltipData[tooltipIdx] = bonusTooltipList[str(bonusIndex)]
                bonusIndexTotal += 1

            questsList.addViewModel(questModels)

        questsList.invalidate()

    def __markAsVisited(self, data):
        for seenQuestID in data['questsOrder']:
            self.__eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
