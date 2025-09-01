# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/weekly_quests_widget_presenter.py
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from comp7.gui.impl.gen.view_models.views.lobby.weekly_quests_widget_model import WeeklyQuestsWidgetModel, State
from comp7.gui.impl.lobby.comp7_helpers.account_settings import setLastSeenQuestData, getLastSeenQuestData
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import getComp7BonusPacker, packQuestBonuses
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isWeeklyRewardClaimed
from comp7.gui.impl.lobby.tooltips.weekly_quest_widget_tooltip import WeeklyQuestWidgetTooltip
from comp7.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7OverlapCtrlMixin
from comp7.gui.shared.event_dispatcher import showComp7MetaRootTab, showComp7WeeklyQuestsRewardsSelectionWindow
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestWidgetPacker
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from frameworks.wulf import Array
from helpers.time_utils import getServerUTCTime
from skeletons.gui.server_events import IEventsCache
from frameworks.wulf.view.array import fillViewModelsArray
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest

class WeeklyQuestsWidgetPresenter(TooltipPositionerMixin, Comp7OverlapCtrlMixin, ViewComponent[WeeklyQuestsWidgetModel], IGlobalListener):
    __eventsCache = dependency.descriptor(IEventsCache)
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def __init__(self):
        super(WeeklyQuestsWidgetPresenter, self).__init__(model=WeeklyQuestsWidgetModel)

    @property
    def viewModel(self):
        return super(WeeklyQuestsWidgetPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        self.startGlobalListening()
        super(WeeklyQuestsWidgetPresenter, self)._onLoading(*args, **kwargs)
        self._updateViewModel()

    def _updateViewModel(self):
        self.queueUpdate()

    def _getEvents(self):
        return super(WeeklyQuestsWidgetPresenter, self)._getEvents() + ((self.viewModel.onMarkAsViewed, self.__onMarkAsViewed),
         (self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated, self.__onWeeklyQuestsUpdated),
         (self.viewModel.onGoToWeeklyQuests, self.__onGoToWeeklyQuests),
         (self.viewModel.onGoToRewardsSelection, self.__onGoToRewardsSelection),
         (self.viewModel.onPollServerTime, self.__onPollServerTime))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.weekly_quest_widget_tooltip():
            return WeeklyQuestWidgetTooltip()
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(WeeklyQuestsWidgetPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        super(WeeklyQuestsWidgetPresenter, self)._finalize()
        self.stopGlobalListening()

    def __onWeeklyQuestsUpdated(self, _):
        self._updateViewModel()

    def _rawUpdate(self):
        super(WeeklyQuestsWidgetPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as tx:
            quests = self.__comp7WeeklyQuestsCtrl.getQuests()
            tx.setQuestsCompleted(quests.numCompletedBattleQuests)
            tx.setTotalQuestsCount(quests.numBattleQuests)
            tx.setState(self.__getQuestsState())
            tx.setLeftToNewQuestsTimestamp(quests.timeOfNewQuests or -1)
            tx.setServerTimestamp(int(getServerUTCTime()))
            modelQuests = tx.getQuests()
            modelQuests.clear()
            if quests.oldQuest:
                questCardModel = self.__updateQuestData(quests.oldQuest, quests.numCompletedBattleQuests)
                modelQuests.addViewModel(questCardModel)
                questCardModel.unbind()
            if quests.newQuest and self.__getQuestsState() == State.ACTIVE:
                questCardModel = self.__updateQuestData(quests.newQuest, quests.numCompletedBattleQuests + 1)
                modelQuests.addViewModel(questCardModel)
                questCardModel.unbind()
            modelQuests.invalidate()

    def __updateQuestData(self, quest, questNumber):
        bonusPacker = getComp7BonusPacker()
        questPacker = Comp7WeeklyQuestWidgetPacker()
        packedBonuses, _ = packQuestBonuses(quest.getBonuses(), bonusPacker)
        questCardModel = questPacker.pack(quest)
        fillViewModelsArray(packedBonuses, questCardModel.getBonuses())
        questCardModel.setQuestNumber(questNumber)
        return questCardModel

    def __getQuestsState(self):
        weeklyQuests = self.__comp7WeeklyQuestsCtrl.getQuests()
        if weeklyQuests.numBattleQuests == weeklyQuests.numCompletedBattleQuests:
            if isWeeklyRewardClaimed():
                return State.HIDE
            return State.REWARD
        return State.ACTIVE if weeklyQuests.newQuest.isStarted() else State.WAITING

    def __onMarkAsViewed(self):
        weeklyQuest = self.__comp7WeeklyQuestsCtrl.getQuests()
        if weeklyQuest.oldQuest:
            self.__setPrevQuestData(weeklyQuest.oldQuest)
        if weeklyQuest.newQuest:
            self.__setPrevQuestData(weeklyQuest.newQuest)

    @staticmethod
    def __setPrevQuestData(quest):
        packedQuest = Comp7WeeklyQuestWidgetPacker().pack(quest)
        setLastSeenQuestData(quest.getID(), (packedQuest.getCurrentProgress(), True))
        _, showCompletedAnimation = getLastSeenQuestData(quest.getID())
        if showCompletedAnimation and not packedQuest.getIsCompleted():
            setLastSeenQuestData(quest.getID(), (packedQuest.getCurrentProgress(), False))
        packedQuest.unbind()

    @staticmethod
    def __onGoToWeeklyQuests():
        showComp7MetaRootTab(tabId=MetaRootViews.WEEKLYQUESTS)

    @staticmethod
    def __onGoToRewardsSelection():
        showComp7WeeklyQuestsRewardsSelectionWindow()

    def __onPollServerTime(self):
        with self.viewModel.transaction() as tx:
            tx.setServerTimestamp(int(getServerUTCTime()))
