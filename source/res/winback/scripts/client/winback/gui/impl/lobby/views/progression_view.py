# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/progression_view.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showHangar, showBrowserOverlayView
from gui.server_events.events_helpers import EventInfoModel
from gui.Scaleform.genConsts.WINBACK_ALIASES import WINBACK_ALIASES
from helpers import dependency
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.server_events import IEventsCache
from winback.gui.impl.gen.view_models.views.lobby.views.progress_level_model import ProgressLevelModel
from winback.gui.impl.gen.view_models.views.lobby.views.progression_view_model import ProgressionState, ProgressionViewModel
from winback.gui.impl.lobby.tooltips.compensation_tooltip import CompensationTooltip
from winback.gui.impl.lobby.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from winback.gui.impl.lobby.views.quests_packer import getEventUIDataPacker
from winback.gui.impl.lobby.views.winback_bonus_packer import packWinbackBonusModelAndTooltipData, getWinbackBonusPacker
from winback.gui.selectable_reward.selectable_reward_manager import WinbackSelectableRewardManager
from winback.gui.shared.events import WinbackViewEvent
from winback.gui.shared.event_dispatcher import showWinbackSelectRewardView
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.impl.backport import TooltipData
    from gui.server_events.event_items import Quest
    from winback.gui.impl.gen.view_models.views.lobby.missions.battle_quests_model import BattleQuestsModel

class _DirtyFlags(object):
    NONE = 0
    PROGRESSION = 1
    QUEST = 2
    TO_HANGAR = 4
    FULL_UPDATE = PROGRESSION | QUEST


class ProgressionView(SubModelPresenter):
    __winbackController = dependency.descriptor(IWinbackController)
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__tooltipData', '__dirtyFlags', '__isDeferredUpdate')

    def __init__(self, viewModel, parentView):
        super(ProgressionView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}
        self.__dirtyFlags = _DirtyFlags.FULL_UPDATE
        self.__isDeferredUpdate = False

    def finalize(self):
        self.__unsubscribeFromDeferredUpdateEvent()
        super(ProgressionView, self).finalize()

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.getTooltipData(event)
        if contentID == R.views.winback.lobby.tooltips.SelectableRewardTooltip():
            return SelectableRewardTooltip(**tooltipData.specialArgs)
        else:
            return CompensationTooltip(**tooltipData.specialArgs) if contentID == R.views.winback.lobby.tooltips.CompensationTooltip() else None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def initialize(self, *args, **kwargs):
        super(ProgressionView, self).initialize(args, kwargs)
        self.__updateModel()

    def setDeferredUpdate(self):
        if self.__isDeferredUpdate:
            return
        self.__isDeferredUpdate = True
        self.__subscribeOnDeferredUpdateEvent()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAboutClicked, self.__onAboutClicked),
         (self.__winbackController.winbackProgression.onSettingsChanged, self.__onSettingsChanged),
         (self.__winbackController.winbackProgression.onProgressPointsUpdated, self.__onProgressPointsUpdated),
         (self.__winbackController.winbackProgression.onGiftTokenUpdated, self.__onProgressPointsUpdated),
         (self.eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.viewModel.onShowSelectableRewardView, self.__showSelectableRewardView))

    def __onClose(self):
        showHangar()

    def __onAboutClicked(self):
        url = self.__winbackController.winbackInfoPageURL
        showBrowserOverlayView(url, alias=WINBACK_ALIASES.WINBACK_BROWSER_VIEW)

    def __showSelectableRewardView(self, args):
        stage = int(args.get(ProgressionViewModel.ARG_STAGE_NUMBER))
        selectableBonusTokens = self.__winbackController.winbackProgression.getTokensIdsByRewardFromLevel(stage)
        showWinbackSelectRewardView(selectableBonusTokens)

    def __onSyncCompleted(self, *_):
        self.__dirtyFlags |= _DirtyFlags.QUEST
        self.__updateModel()

    def __onProgressPointsUpdated(self):
        self.__dirtyFlags |= _DirtyFlags.PROGRESSION
        self.__updateModel()

    def __onSettingsChanged(self, isProgressionSwitched):
        if isProgressionSwitched:
            self.__dirtyFlags |= _DirtyFlags.TO_HANGAR
        self.__dirtyFlags |= _DirtyFlags.FULL_UPDATE
        self.__updateModel()

    def __deferredUpdate(self, _):
        self.__isDeferredUpdate = False
        self.__unsubscribeFromDeferredUpdateEvent()
        self.__updateModel()

    def __updateModel(self):
        if self.__isDeferredUpdate or self.__dirtyFlags & _DirtyFlags.NONE:
            return
        if self.__dirtyFlags & _DirtyFlags.TO_HANGAR:
            self.__onClose()
            return
        with self.viewModel.transaction() as model:
            model.setProgressionName(self.__winbackController.progressionName)
            if self.__dirtyFlags & _DirtyFlags.PROGRESSION:
                data = self.__winbackController.winbackProgression.getProgressionData()
                self.__updateProgression(model, data)
            if self.__dirtyFlags & _DirtyFlags.QUEST:
                questsData = self.__winbackController.winbackProgression.getBattleQuestData()
                self.__updateBattleQuestsCards(model.battleQuests, self.__getSortedQuests(questsData))
                self.__updateMissionVisitedArray(model.battleQuests.getMissionsCompletedVisited(), questsData.keys())
                self.__markAsVisited(questsData)
        self.__dirtyFlags = _DirtyFlags.NONE

    def __updateProgression(self, model, data):
        self.__updateProgressionState(model)
        self.__updateProgressionPoints(model, data)
        model.setIsClaimRewardsAvailable(self.__winbackController.hasWinbackOfferGiftToken())
        progressionLevels = model.getProgressLevels()
        progressionLevels.clear()
        for levelData in data['progressionLevels']:
            level = ProgressLevelModel()
            self.__updateProgressionLevelModel(level, levelData)
            progressionLevels.addViewModel(level)

        progressionLevels.invalidate()

    def __updateProgressionState(self, model):
        state = ProgressionState.COMPLETED if self.__winbackController.isFinished() else ProgressionState.INPROGRESS
        model.setState(state)

    def __updateProgressionLevelModel(self, model, data):
        rewards = model.getRewards()
        bonuses = data['rewards']
        packWinbackBonusModelAndTooltipData(bonuses, getWinbackBonusPacker(), rewards, self.__tooltipData)
        model.setIsSelectableReward(self.__hasAvailableSelectableBonuses(bonuses))

    def __updateProgressionPoints(self, model, data):
        previousPoints = data['previousPoints']
        currentPoints = data['currentPoints']
        pointsForLevel = data['pointsForLevel']
        if currentPoints < previousPoints:
            previousPoints = pointsForLevel * len(data['progressionLevels'])
            self.parentView.playResetProgressionSound()
        model.setCurProgressPoints(currentPoints)
        model.setPrevProgressPoints(previousPoints)
        model.setPointsForLevel(pointsForLevel)
        self.__winbackController.winbackProgression.saveCurPoints()

    @staticmethod
    def __hasAvailableSelectableBonuses(bonuses):
        return any((WinbackSelectableRewardManager.isAvailableSelectableBonus(bonus) for bonus in bonuses))

    def __updateBattleQuestsCards(self, battleQuestsModel, quests):
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        battleQuestsModel.setCurrentTimerDate(newCountdownVal)
        questsList = battleQuestsModel.getTasksBattle()
        questsList.clear()
        bonusIndexTotal = len(self.__tooltipData)
        for quest in quests:
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

    @staticmethod
    def __getSortedQuests(questsData):
        return sorted(questsData.itervalues(), key=lambda q: q.getPriority(), reverse=True)

    def __updateMissionVisitedArray(self, missionVisitedArray, questsIDs):
        missionVisitedArray.clear()
        missionVisitedArray.reserve(len(questsIDs))
        for questID in questsIDs:
            missionCompletedVisited = not self.eventsCache.questsProgress.getQuestCompletionChanged(questID)
            missionVisitedArray.addBool(missionCompletedVisited)

        missionVisitedArray.invalidate()

    def __markAsVisited(self, questsData):
        for seenQuestID in questsData.keys():
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)

    def __subscribeOnDeferredUpdateEvent(self):
        g_eventBus.addListener(WinbackViewEvent.WINBACK_REWARD_VIEW_CLOSED, self.__deferredUpdate)

    def __unsubscribeFromDeferredUpdateEvent(self):
        g_eventBus.removeListener(WinbackViewEvent.WINBACK_REWARD_VIEW_CLOSED, self.__deferredUpdate)
