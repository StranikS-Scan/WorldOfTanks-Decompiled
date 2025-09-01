# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/quests_card_presenter.py
import typing
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.event_items import ServerEventAbstract
from helpers import dependency
from last_stand.gui.impl.lobby.ls_helpers import fillProminentBonus, PROMINENT_REWARD_TOOLTIP_ID, getQuestFinishTimeLeft
from last_stand.gui.impl.lobby.tooltips.daily_quests_tooltip import DailyQuestsTooltip
from shared_utils import first, findFirst
from frameworks.wulf import View, ViewEvent
from gui.impl.gen import R
from gui.server_events.cond_formatters import postbattle as postbattleFrmt, bonus as bonusFrmt
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from skeletons.gui.server_events import IEventsCache
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.quests_view_model import QuestsViewModel, WidgetState
from last_stand.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from last_stand_common.last_stand_constants import ArtefactsSettings
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand_common.last_stand_constants import DailyMissionsSettings

class QuestsCardPresenter(ViewComponent[QuestsViewModel]):
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, isBadgeWidget=False):
        super(QuestsCardPresenter, self).__init__(model=QuestsViewModel)
        self.__postBattleCondFormatter = postbattleFrmt.MissionsPostBattleConditionsFormatter()
        self.__bonusCondFormatter = bonusFrmt.MissionsBonusConditionsFormatter()
        self.__isBadgeWidget = isBadgeWidget
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__prominentBonus = None
        self.__quest = None
        self.__initQuest()
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == PROMINENT_REWARD_TOOLTIP_ID and self.__prominentBonus is not None:
                window = BackportTooltipWindow(createTooltipData(tooltip=self.__prominentBonus.tooltip, isSpecial=self.__prominentBonus.isSpecial, specialAlias=self.__prominentBonus.specialAlias, specialArgs=self.__prominentBonus.specialArgs, isWulfTooltip=self.__prominentBonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(QuestsCardPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.key_tooltip():
            return KeyTooltipView(isPostBattle=False)
        if contentID == R.views.last_stand.mono.lobby.tooltips.daily_quests_tooltip():
            progressCurrent = event.getArgument('progressCurrent', 0)
            progressTotal = event.getArgument('progressTotal', 0)
            return DailyQuestsTooltip(self.__quest, self.__isBadgeWidget, progressCurrent, progressTotal)
        return super(QuestsCardPresenter, self).createToolTipContent(event, contentID)

    @property
    def isBadgeWidget(self):
        return self.__isBadgeWidget

    def _onLoading(self, *args, **kwargs):
        super(QuestsCardPresenter, self)._onLoading()
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
        return [(self.eventsCache.onSyncCompleted, self.__onSyncQuestCompleted), (self.lsArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated)]

    def _init(self):
        self.__initQuest()
        if self.__quest is None:
            self.__hideWidget()
            return
        else:
            self.__fillViewModel(self.__quest)
            return

    def __onSyncQuestCompleted(self):
        self._init()

    def __onNotifyStatusChange(self):
        self._init()

    def __getTimeToStatusChange(self):
        return getQuestFinishTimeLeft(self.__quest)

    def __getActiveQuest(self, checker):
        return first(self.eventsCache.getAllQuests(lambda q: checker(q.getID()) and not q.isOutOfDate() and q.isStarted() and ServerEventAbstract.isAvailable(q).isValid).values())

    def __isFinalArtefactOpened(self):
        return self.lsArtifactsCtrl.isArtefactOpened(self.lsArtifactsCtrl.getFinalArtefact().artefactID)

    def __onArtefactStatusUpdated(self, token):
        artefact = self.lsArtifactsCtrl.getArtefact(self.lsArtifactsCtrl.geArtefactIDFromOpenToken(token))
        if artefact and self.lsArtifactsCtrl.isFinalArtefact(artefact):
            self._init()

    def __getFirstConditionIcon(self, quest, questConditions, formatter):
        for orItem in formatter.format(questConditions, quest):
            for andItem in orItem:
                return andItem.iconKey

    def __getFirstBonusConditionCumulativeProgress(self, quest):
        for orItem in self.__bonusCondFormatter.format(quest.bonusCond, quest):
            for andItem in orItem:
                if andItem.progressType == MISSIONS_ALIASES.CUMULATIVE:
                    return (int(andItem.current), int(andItem.total))

    def __fillViewModel(self, quest):
        with self.getViewModel().transaction() as tx:
            tx.setName(quest.getUserName().replace('\\n', '\n'))
            tx.setDescription(quest.getDescription())
            tx.setIsCompleted(quest.isCompleted())
            tx.setResetTime(self.__getTimeToStatusChange())
            if self.__isBadgeWidget:
                tx.setState(WidgetState.BADGE)
                progressCurrent, progressTotal = self.__getFirstBonusConditionCumulativeProgress(quest)
                tx.setMaximumProgress(progressTotal)
                tx.setCurrentProgress(progressCurrent)
                self.__prominentBonus = fillProminentBonus(quest.getID(), self.__quest.getBonuses(), tx.bonus)
                condIcon = self.__getFirstConditionIcon(quest, quest.bonusCond, self.__bonusCondFormatter)
            else:
                tx.setState(WidgetState.DEFAULT)
                tx.setKeyBonus(self.__getBonusDailyKeysCount(quest))
                condIcon = self.__getFirstConditionIcon(quest, quest.postBattleCond, self.__postBattleCondFormatter)
            tx.setConditionName(condIcon)

    def __initQuest(self):
        if self.lsArtifactsCtrl.getArtefactsCount() == 0:
            return
        if self.__isBadgeWidget or self.__isFinalArtefactOpened():
            self.__isBadgeWidget = True
            self.__quest = self.__getActiveQuest(self.__isBadgeQuest)
        else:
            self.__quest = self.__getActiveQuest(self.__isDailyQuest)

    @replaceNoneKwargsModel
    def __hideWidget(self, model=None):
        model.setState(WidgetState.HIDDEN)

    @staticmethod
    def __getBonusDailyKeysCount(quest):
        bonus = findFirst(lambda bonus: bonus.getName() == 'battleToken', quest.getBonuses())
        token = bonus.getTokens().get(ArtefactsSettings.KEY_TOKEN) if bonus else None
        return token.count if token else 0

    @staticmethod
    def __getBonusBadgeID(quest):
        bonus = findFirst(lambda bonus: bonus.getName() == 'dossier', quest.getBonuses())
        badge = first(bonus.getBadges()) if bonus else None
        return badge.badgeID if badge else 0

    @staticmethod
    def __isDailyQuest(questID):
        return questID.startswith(DailyMissionsSettings.DAILY_MISSION_QUEST_PREFIX)

    @staticmethod
    def __isBadgeQuest(questID):
        return questID == DailyMissionsSettings.BADGE_MISSION_QUEST
