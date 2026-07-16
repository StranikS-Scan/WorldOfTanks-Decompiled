# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/quests_card_presenter.py
from __future__ import absolute_import
import typing
import constants
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub.view_component import ViewComponent
from gui.server_events import IEventsCache
from gui.server_events.event_items import ServerEventAbstract
from helpers import dependency, time_utils
from ids_generators import SequenceIDGenerator
from last_stand.gui.impl.lobby.ls_helpers import getQuestFinishTimeLeft, fillRewards
from last_stand.gui.impl.lobby.tooltips.daily_quests_tooltip import DailyQuestsTooltip
from last_stand.gui.impl.lobby.tooltips.points_tooltip import PointsTooltipView
from shared_utils import first
from gui.impl.gen import R
from gui.server_events.cond_formatters import postbattle as postbattleFrmt, bonus as bonusFrmt
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.quests_view_model import QuestsViewModel
from last_stand.gui.shared.event_dispatcher import showRewardPathView
from last_stand_common.last_stand_constants import DailyMissionsSettings
from last_stand.skeletons.ls_quests_ui_cache import ILSQuestsUICache
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from last_stand.skeletons.ls_controller import ILSController
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewEvent
    from gui.server_events.parsers import BonusConditions
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class QuestsCardPresenter(ViewComponent[QuestsViewModel]):
    __questsCache = dependency.descriptor(ILSQuestsUICache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lsCtrl = dependency.descriptor(ILSController)
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self):
        super(QuestsCardPresenter, self).__init__(model=QuestsViewModel)
        self.__postBattleCondFormatter = postbattleFrmt.MissionsPostBattleConditionsFormatter()
        self.__bonusCondFormatter = bonusFrmt.MissionsBonusConditionsFormatter()
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__quest = None
        self.__allDailyCompleted = False
        self.__initQuest()
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()
        return

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(QuestsCardPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.daily_quests_tooltip():
            return DailyQuestsTooltip(self.__quest, self.__allDailyCompleted)
        return PointsTooltipView(isPostBattle=False) if contentID == R.views.last_stand.mono.lobby.tooltips.points_tooltip() else super(QuestsCardPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(QuestsCardPresenter, self)._onLoading(*args, **kwargs)
        self._init()
        self.__statusChangeNotifier.startNotification()

    def _finalize(self):
        super(QuestsCardPresenter, self)._finalize()
        self.__postBattleCondFormatter = None
        self.__bonusCondFormatter = None
        self.__statusChangeNotifier.stopNotification()
        self.__statusChangeNotifier = None
        return

    def _getEvents(self):
        return ((self.__questsCache.onSyncCompleted, self.__onSyncQuestCompleted), (self.getViewModel().onClick, self.__onClick), (self.getViewModel().onMarkAsViewed, self.__onMarkAsViewed))

    def _getCallbacks(self):
        return super(QuestsCardPresenter, self)._getCallbacks() + (('tokens', self.__onTokensUpdated),)

    def _init(self):
        self.__initQuest()
        if self.__quest is None:
            self.__setWidgetState(isHidden=True)
            return
        else:
            self.__fillViewModel(self.__quest)
            return

    def __onClick(self):
        showRewardPathView(openFromQuestCard=True)

    def __onMarkAsViewed(self):
        with self.getViewModel().transaction() as tx:
            tx.setEarned(0)
            tx.setAnimateCompletion(False)

    def __onSyncQuestCompleted(self):
        self._init()

    def __onTokensUpdated(self, diff):
        for token in diff:
            if DailyMissionsSettings.DAILY_MISSION_TOKEN_PREFIX in token:
                self._init()
                break

    def __onNotifyStatusChange(self):
        self._init()

    def __getTimeToStatusChange(self):
        return getQuestFinishTimeLeft(self.__quest)

    def __getActiveQuest(self, checker):
        return first(self.__questsCache.getQuests(lambda q: checker(q.getID()) and not q.isOutOfDate() and q.isStarted() and ServerEventAbstract.isAvailable(q).isValid).values())

    def __getFirstConditionIcon(self, quest, questConditions, formatter):
        for orItem in formatter.format(questConditions, quest):
            for andItem in orItem:
                return andItem.iconKey

    def _getFirstConditionKeyName(self, questConditions):
        for cond in questConditions.getConditions().items:
            return cond.getName()

    def __getFirstBonusConditionCumulativeProgress(self, quest):
        for orItem in self.__bonusCondFormatter.format(quest.bonusCond, quest):
            for andItem in orItem:
                if andItem.progressType == MISSIONS_ALIASES.CUMULATIVE:
                    return (int(andItem.current), int(andItem.total))

    def __fillViewModel(self, quest):
        with self.getViewModel().transaction() as tx:
            tx.setId(quest.getID())
            tx.setName(quest.getDescription().replace('\\n', '\n'))
            tx.setDescription(quest.getDescription().replace('\\n', '\n'))
            tx.setIsCompleted(quest.isCompleted())
            tx.setResetTime(self.__getTimeToStatusChange())
            progressCurrent, progressTotal = self.__getFirstBonusConditionCumulativeProgress(quest)
            tx.setMaximumProgress(progressTotal)
            tx.setCurrentProgress(progressCurrent)
            bonusesModel = tx.getBonuses()
            bonusesModel.clear()
            self.__bonusCache = fillRewards(self.__quest.getBonuses(), bonusesModel, self._MAX_BONUSES_IN_VIEW, self.__idGen)
            decorationID = quest.getIconID()
            conditionIcon = None
            if decorationID:
                conditionIcon = constants.DailyQuestDecorationMap.get(decorationID)
            if not conditionIcon:
                bonusCondIcon = self.__getFirstConditionIcon(quest, quest.bonusCond, self.__bonusCondFormatter)
                postBattleCondIcon = self.__getFirstConditionIcon(quest, quest.postBattleCond, self.__postBattleCondFormatter)
                conditionIcon = bonusCondIcon if bonusCondIcon else postBattleCondIcon
            tx.setConditionName(conditionIcon)
            self.__setWidgetState(isHidden=False)
            questsProgress = self.__eventsCache.questsProgress
            condKeyName = self._getFirstConditionKeyName(quest.bonusCond)
            prevProgress = questsProgress.getLastViewedProgress(quest.getID()).get(None, {}).get(condKeyName)
            if prevProgress and prevProgress != progressCurrent:
                tx.setEarned(int(progressCurrent - prevProgress))
            tx.setAnimateCompletion(questsProgress.getQuestCompletionChanged(quest.getID()))
            questsProgress.markQuestProgressAsViewed(quest.getID())
            endDate = self.__lsCtrl.getModeSettings().endDate
            now = time_utils.getCurrentLocalServerTimestamp()
            if endDate - now < constants.SECONDS_IN_DAY:
                self.__allDailyCompleted = True
            tx.setAllDailyCompleted(self.__allDailyCompleted)
        return

    def __initQuest(self):
        self.__quest = self.__getActiveQuest(self.__isDailyQuest)

    @staticmethod
    def __isDailyQuest(questID):
        return questID.startswith(DailyMissionsSettings.DAILY_MISSION_QUEST_PREFIX)

    @replaceNoneKwargsModel
    def __setWidgetState(self, isHidden, model=None):
        model.setIsHidden(isHidden)
