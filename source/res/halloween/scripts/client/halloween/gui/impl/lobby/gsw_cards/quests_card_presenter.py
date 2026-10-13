# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/gsw_cards/quests_card_presenter.py
from __future__ import absolute_import
import logging
from collections import namedtuple
import typing
from cache import cached_property
from constants import DailyQuestDecorationMap
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.event_items import ServerEventAbstract
from halloween.gui.game_control.halloween_artefacts_controller import getBonusPriority
from halloween.gui.impl.lobby.tooltips.tooltip_positioner import TooltipPositionerMixin
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from helpers import dependency
from halloween.gui.impl.lobby.hw_helpers import getQuestSmallestFinishTimeLeft, fillBaseBonusProperties, getHWMetaAwardFormatter, PROMINENT_REWARD_TOOLTIP_ID, HalloweenBonusesAwardsComposer, INF_DISPLAY_BONUSES
from halloween.gui.impl.lobby.tooltips.daily_quests_tooltip import DailyQuestsTooltip
from gui.impl.gen import R
from gui.server_events.cond_formatters import postbattle as postbattleFrmt, bonus as bonusFrmt
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from halloween.gui.impl.gen.view_models.views.lobby.widgets.quests_card_view_model import QuestsCardViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.quests_list_view_model import QuestsListViewModel
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import View, Window, ViewEvent
    from gui.server_events.awards_formatters import QuestsBonusComposer
    from gui.server_events.event_items import Quest
    from halloween_common.configs.halloween_gsw import CardModel
_logger = logging.getLogger(__name__)
QuestData = namedtuple('QuestData', ['quest', 'bonus'])

class QuestsCardPresenter(TooltipPositionerMixin, ViewComponent[QuestsListViewModel]):
    _hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)
    _halloweenCtrl = dependency.descriptor(IHalloweenController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, isGSW=False):
        super(QuestsCardPresenter, self).__init__(model=QuestsListViewModel)
        self.__postBattleCondFormatter = postbattleFrmt.MissionsPostBattleConditionsFormatter()
        self.__bonusCondFormatter = bonusFrmt.MissionsBonusConditionsFormatter()
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self._fullRefresh)
        self.__quests = {}
        self.__isGSW = isGSW

    @property
    def viewModel(self):
        return super(QuestsCardPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            questId = event.getArgument('questId')
            if tooltipId == PROMINENT_REWARD_TOOLTIP_ID and questId is not None:
                _, bonus = self.__quests.get(questId)
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(QuestsCardPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.daily_quests_tooltip():
            questId = event.getArgument('questId')
            return DailyQuestsTooltip(self.__quests.get(questId))
        return super(QuestsCardPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(QuestsCardPresenter, self)._onLoading()
        self._fullRefresh()
        self.__statusChangeNotifier.startNotification()

    def _finalize(self):
        self.__postBattleCondFormatter = None
        self.__bonusCondFormatter = None
        self.__statusChangeNotifier.stopNotification()
        self.__statusChangeNotifier = None
        super(QuestsCardPresenter, self)._finalize()
        return

    def _getEvents(self):
        return [(self._eventsCache.onSyncCompleted, self._fullRefresh),
         (self._halloweenCtrl.onSettingsUpdate, self._fullRefresh),
         (self._hwAnomaliesCtrl.onChangeSystemAnomaliesUnlock, self._fullRefresh),
         (self._hwAnomaliesCtrl.onRefreshData, self._fullRefresh)]

    def _fullRefresh(self):
        self.__refreshData()
        self.__refreshModel()

    def __getTimeToStatusChange(self):
        return getQuestSmallestFinishTimeLeft([ questData.quest for questData in self.__quests.values() ])

    @staticmethod
    def __validateQuest(quest):
        return ServerEventAbstract.isAvailable(quest).isValid

    def __checkTokenCondition(self, card):
        return not card.visibleByToken or self._itemsCache.items.tokens.getToken(card.visibleByToken)

    def __getActualQuest(self, card):
        questsCache = self._halloweenCtrl.getHWQuestsCache()
        result = None
        for questID in card.quests:
            quest = questsCache.get(questID)
            if quest is None:
                _logger.error('INVALID QUEST %s', questID)
                continue
            if self.__isGSW:
                if not quest.isCompleted() and self.__validateQuest(quest) and self.__checkTokenCondition(card):
                    result = quest
                    break
            result = quest
            if not quest.isCompleted():
                break

        return result

    @cached_property
    def __bonusFormatter(self):
        return HalloweenBonusesAwardsComposer(INF_DISPLAY_BONUSES, getHWMetaAwardFormatter())

    def __getQuestBonus(self, quest):
        questID = quest.getID()
        prominentBonusType = self._halloweenCtrl.getModeSettings().prominentBonus.get(questID, '')
        if prominentBonusType:
            bonusRewards = self.__bonusFormatter.getFormattedBonuses(sorted(quest.getBonuses(), key=getBonusPriority), AWARDS_SIZES.BIG)
            for bonusReward in bonusRewards:
                if prominentBonusType in (bonusReward.bonusName, bonusReward.itemTypeName):
                    return bonusReward

        return None

    def __refreshData(self):
        gswConfigCards = self._halloweenCtrl.getGSWConfig().cards.card
        self.__quests.clear()
        for card in gswConfigCards:
            quest = self.__getActualQuest(card)
            if quest is not None:
                bonus = self.__getQuestBonus(quest)
                self.__quests[quest.getID()] = QuestData(quest, bonus)

        return

    @staticmethod
    def __getFirstConditionIcon(quest, formatter):
        for orItem in formatter.format(quest.postBattleCond, quest):
            for andItem in orItem:
                return andItem.iconKey

    def __getFirstBonusConditionCumulativeProgress(self, quest):
        for orItem in self.__bonusCondFormatter.format(quest.bonusCond, quest):
            for andItem in orItem:
                if andItem.progressType == MISSIONS_ALIASES.CUMULATIVE:
                    return (int(andItem.current), int(andItem.total), int(andItem.earned))

    def __refreshModel(self):
        with self.viewModel.transaction() as tx:
            quests = tx.getQuests()
            quests.clear()
            for questID, questData in self.__quests.items():
                quest, bonus = questData
                curProgress, maxProgress, _ = self.__getFirstBonusConditionCumulativeProgress(quest)
                decorationID = quest.getIconID()
                if decorationID:
                    conIcon = DailyQuestDecorationMap.get(decorationID)
                else:
                    conIcon = self.__getFirstConditionIcon(quest, self.__postBattleCondFormatter)
                questModel = QuestsCardViewModel()
                questModel.setId(questID)
                questModel.setName(quest.getUserName().replace('\\n', '\n'))
                questModel.setDescription(quest.getDescription())
                questModel.setIsCompleted(quest.isCompleted())
                questModel.setCurrentProgress(curProgress)
                questModel.setMaximumProgress(maxProgress)
                questModel.setConditionName(conIcon)
                if bonus is not None:
                    bonusModel = questModel.bonus
                    fillBaseBonusProperties(bonus, bonusModel)
                    bonusModel.setTooltipId(PROMINENT_REWARD_TOOLTIP_ID)
                quests.addViewModel(questModel)

            quests.invalidate()
        return
