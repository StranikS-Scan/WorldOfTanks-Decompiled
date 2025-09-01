# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/game_control/award_controller.py
import logging
import typing
import ArenaType
from chat_shared import SYS_MESSAGE_TYPE
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isComp7VisibleQuest, getComp7QuestType, parseComp7RanksQuestID, getRequiredTokensCountToComplete
from comp7.gui.shared import event_dispatcher as comp7_events
from comp7.gui.shared.event_dispatcher import showComp7BanWindow
from comp7.skeletons.gui.game_control import IComp7ShopController
from comp7_common_const import Comp7QuestType, qualificationQuestIDBySeasonNumber, COMP7_YEARLY_REWARD_TOKEN
from constants import INVOICE_ASSET, ARENA_BONUS_TYPE, PENALTY_TYPES
from fairplay_violation_types import getFairplayViolationLocale, getPenaltyTypeAndViolationName, FAIRPLAY_EXCLUDED_ARENA_BONUS_TYPES
from gui.game_control.AwardController import MultiTypeServiceChannelHandler, ServiceChannelHandler, PunishWindowHandler
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters.time_formatters import getTillTimeByResource
from helpers import dependency
from messenger.formatters import TimeFormatter
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.server_events.event_items import TokenQuest
_logger = logging.getLogger(__name__)

class Comp7QuestRewardHandler(MultiTypeServiceChannelHandler):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)
    __comp7ShopCtrl = dependency.descriptor(IComp7ShopController)

    def __init__(self, awardCtrl):
        handledTypes = (SYS_MESSAGE_TYPE.comp7BattleResults.index(), SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index())
        super(Comp7QuestRewardHandler, self).__init__(handledTypes, awardCtrl)
        self.__completedQuestIDs = set()

    def fini(self):
        self.__completedQuestIDs.clear()
        self.eventsCache.onSyncCompleted -= self.__showAward
        super(Comp7QuestRewardHandler, self).fini()

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data
        self.__completedQuestIDs.update((qID for qID in data.get('completedQuestIDs', set()) if isComp7VisibleQuest(qID)))
        if not self.__completedQuestIDs:
            return
        if self.eventsCache.waitForSync:
            self.eventsCache.onSyncCompleted += self.__onEventCacheSyncCompleted
        else:
            self.__showAward()

    def __showAward(self):
        ranksQuests, tokensQuests, _, isQualification = self.__getComp7CompletedQuests()
        self.__completedQuestIDs.clear()
        if ranksQuests:
            self.__comp7ShopCtrl.validateCachedProducts()
        if isQualification:
            comp7_events.showComp7QualificationRewardsScreen(quests=ranksQuests)
        else:
            for quest in ranksQuests:
                comp7_events.showComp7RanksRewardsScreen(quest=quest)

        for quest in tokensQuests:
            comp7_events.showComp7TokensRewardsScreen(quest=quest)

    def __getComp7CompletedQuests(self):
        ranksQuests = []
        tokensQuests = []
        periodicQuests = []
        isQualification = False
        if not self.__completedQuestIDs:
            return (ranksQuests, tokensQuests, periodicQuests)
        else:
            allQuests = self.eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID()))
            actualSeasonNumber = self.__comp7Ctrl.getActualSeasonNumber()
            qualificationQuestID = qualificationQuestIDBySeasonNumber(actualSeasonNumber) if actualSeasonNumber else None
            for qID in self.__completedQuestIDs:
                quest = allQuests.get(qID)
                if quest is None:
                    _logger.error('Missing Comp7 Quest qID=%s', qID)
                    continue
                qType = getComp7QuestType(qID)
                if qType == Comp7QuestType.RANKS:
                    ranksQuests.append(quest)
                elif qType == Comp7QuestType.TOKENS:
                    tokensQuests.append(quest)
                elif qType == Comp7QuestType.PERIODIC:
                    periodicQuests.append(quest)
                if qID == qualificationQuestID:
                    isQualification = True

            ranksQuests.sort(key=self.__getRanksQuestSortKey, reverse=True)
            tokensQuests.sort(key=self.__getTokensQuestSortKey)
            return (ranksQuests,
             tokensQuests,
             periodicQuests,
             isQualification)

    def __onEventCacheSyncCompleted(self, *_):
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        self.__showAward()

    @staticmethod
    def __getRanksQuestSortKey(quest):
        division = parseComp7RanksQuestID(quest.getID())
        return (division.rank, division.index)

    @staticmethod
    def __getTokensQuestSortKey(quest):
        return getRequiredTokensCountToComplete(quest.getID())


class Comp7InvoiceRewardHandler(ServiceChannelHandler):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)
    __RETRY_TIMES = [2, 3, 5]

    def __init__(self, awardCtrl):
        super(Comp7InvoiceRewardHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)
        self.__bonuses = None
        return

    def _showAward(self, ctx):
        _, message = ctx
        invoiceData = message.data
        if invoiceData.get('assetType', 0) == INVOICE_ASSET.PURCHASE:
            bonuses = invoiceData.get('data', {})
            if COMP7_YEARLY_REWARD_TOKEN in bonuses.get('tokens', ()):
                self.__bonuses = bonuses
                self.__comp7Ctrl.onEntitlementsUpdated += self.__onEntitlementsUpdated
                self.__comp7Ctrl.onEntitlementsUpdateFailed += self.__onEntitlementsUpdateFailed
                self.__comp7Ctrl.updateEntitlementsCache(True, self.__RETRY_TIMES)

    def __onEntitlementsUpdated(self):
        self.__comp7Ctrl.onEntitlementsUpdated -= self.__onEntitlementsUpdated
        self.__comp7Ctrl.onEntitlementsUpdateFailed -= self.__onEntitlementsUpdateFailed
        comp7_events.showComp7YearlyRewardsScreen(self.__bonuses)

    def __onEntitlementsUpdateFailed(self):
        self.__comp7Ctrl.onEntitlementsUpdated -= self.__onEntitlementsUpdated
        self.__comp7Ctrl.onEntitlementsUpdateFailed -= self.__onEntitlementsUpdateFailed
        _logger.warning('Could not show season results due to unsuccessful entitlements request')
        comp7_events.showComp7YearlyRewardsScreen(self.__bonuses, showSeasonResults=False)


class Comp7PunishWindowHandler(PunishWindowHandler):

    def _showAward(self, ctx):
        _, message = ctx
        arenaTypeID = message.data.get('arenaTypeID', 0)
        if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
            arenaType = ArenaType.g_cache[arenaTypeID]
        else:
            arenaType = None
        arenaCreateTime = message.data.get('arenaCreateTime', None)
        fairplayViolations = message.data.get('fairplayViolations', None)
        bonusType = message.data.get('bonusType')
        if bonusType != ARENA_BONUS_TYPE.COMP7:
            return
        else:
            if arenaCreateTime and arenaType and bonusType not in FAIRPLAY_EXCLUDED_ARENA_BONUS_TYPES and fairplayViolations is not None and fairplayViolations[:2] != (0, 0):
                restriction = message.data.get('restriction', None)
                banDuration = restriction[1] if restriction else 0
                extraData = restriction[2] if restriction else {}
                arenaTimeStr = TimeFormatter.getActualMsgTimeStr(arenaCreateTime)
                penaltyType, violationName, isAFKPenalty = getPenaltyTypeAndViolationName(fairplayViolations, banDuration)
                punishmentReason = backport.text(getFairplayViolationLocale(violationName))
                if penaltyType == PENALTY_TYPES.BAN:
                    showComp7BanWindow(arenaTypeID, arenaTimeStr, getTillTimeByResource(banDuration, R.strings.dialogs.punishmentWindow.time, removeLeadingZeros=True), extraData.get('penalty', 0), extraData.get('qualActive', False))
                elif penaltyType == PENALTY_TYPES.PENALTY:
                    self._showPenaltyWindow(arenaTypeID, arenaTimeStr, punishmentReason, isAFKPenalty)
                else:
                    self._showWarningWindow(arenaTypeID, arenaTimeStr, punishmentReason, isAFKPenalty)
            return

    @property
    def channelType(self):
        return SYS_MESSAGE_TYPE.comp7BattleResults.index()
