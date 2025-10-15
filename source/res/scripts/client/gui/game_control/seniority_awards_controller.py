# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seniority_awards_controller.py
import copy
import typing
import BigWorld
import Event
from constants import SENIORITY_AWARDS_COMP_TOKEN_PREFIX, SENIORITY_AWARDS_COMPENSATION_BONUS, SENIORITY_AWARDS_COMP_QUEST_PREFIX, SENIORITY_AWARDS_VEHICLE_OFFER
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.server_events.finders import getFinalTokensQuestIdBySeasonId
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, time_utils
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from helpers.server_settings import SeniorityAwardsConfig
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
SACOIN = 'sacoin'
CLAIM_REWARD_TIMEOUT = 10
_OFFER_COMPENSATION_TOKEN_NAME = SENIORITY_AWARDS_COMPENSATION_BONUS + ':offer'
_BLANK_COMPENSATION_TOKEN_NAME = SENIORITY_AWARDS_COMPENSATION_BONUS + ':blank'

class SeniorityAwardsController(ISeniorityAwardsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __eventsCache = dependency.descriptor(IEventsCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        super(SeniorityAwardsController, self).__init__()
        self.onUpdated = Event.Event()
        self.__claimTimeoutId = None
        return

    @property
    def isEnabled(self):
        return self._config.enabled

    @property
    def timeLeft(self):
        return self._config.endTime - time_utils.getServerUTCTime() if self.isEnabled else -1

    @property
    def isRewardReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self._config.receivedRewardsToken)

    @property
    def seniorityQuestPrefix(self):
        return self._config.rewardQuestsPrefix

    @property
    def isEligibleToReward(self):
        return self.isEnabled and self.__itemsCache.items.tokens.isTokenAvailable(self._config.rewardEligibilityToken)

    @property
    def isNeedToShowRewardNotification(self):
        return self.isEnabled and self.__hangarSpace.spaceInited and self._config.showRewardNotification and self.isEligibleToReward and not self.isRewardReceived

    @property
    def isNeedToShowOfferNotification(self):
        if not (self.isEnabled and self.__hangarSpace.spaceInited and self.__itemsCache.items.tokens.isTokenAvailable(SENIORITY_AWARDS_VEHICLE_OFFER)):
            return False
        else:
            offer = self.__offersProvider.getOfferByGiftToken(SENIORITY_AWARDS_VEHICLE_OFFER)
            return offer is not None and offer.isOfferAvailable

    @property
    def clockOnNotification(self):
        return self._config.clockOnNotification

    def getSACoin(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(SACOIN, 0)

    def replaceCompTokens(self, rewards):
        result = {}
        rewards.setdefault('tokens', {})
        for key, section in rewards.iteritems():
            if key != 'tokens':
                result[key] = section

        result['tokens'] = newTokens = {}
        oldTokens = rewards['tokens']
        for tokenId, value in oldTokens.iteritems():
            if tokenId == 'offer:seniority:vehicle_10:1':
                continue
            if not tokenId.startswith(SENIORITY_AWARDS_COMP_TOKEN_PREFIX):
                newTokens[tokenId] = value
                continue
            self.__replaceCompensationToken(tokenId, value, result)

        return result

    def __replaceCompensationToken(self, tokenId, value, result):
        if tokenId.startswith('wdr25_check_comp_quests:pm'):
            self.__checkAndReplaceFreeList(tokenId, value, result)
        elif tokenId == 'wdr25_check_comp_quests:vehicle_offer':
            self.__checkAndReplaceVehicleOffer(value, result)

    def __checkAndReplaceFreeList(self, tokenId, value, result):
        seasonId = int(tokenId[-1])
        finalPmTokens = getFinalTokensQuestIdBySeasonId(seasonId)
        pmCompleteTokens = []
        for pmToken in finalPmTokens:
            pmCompleteTokens.append(self.__itemsCache.items.tokens.getTokenCount(pmToken))

        if all(pmCompleteTokens):
            questID = '%spm_%d:1' % (SENIORITY_AWARDS_COMP_QUEST_PREFIX, seasonId)
            quest = self.__eventsCache.getQuestByID(questID)
            bonuses = quest.getBonuses()
            compensationCount = bonuses[0].getValue()
            valueCopy = copy.copy(value)
            valueCopy['count'] = compensationCount
            valueCopy['bonus'] = {'currency': SACOIN,
             'amount': compensationCount,
             'campaignID': seasonId}
            result.setdefault('meta', {})
            result['meta']['%s_%d' % (_BLANK_COMPENSATION_TOKEN_NAME, seasonId)] = valueCopy
        else:
            questID = '%spm_%d:2' % (SENIORITY_AWARDS_COMP_QUEST_PREFIX, seasonId)
            quest = self.__eventsCache.getQuestByID(questID)
            bonus = quest.getBonuses()[0]
            result['tokens'].update(bonus.getValue())

    def __checkAndReplaceVehicleOffer(self, value, result):
        criteria = REQ_CRITERIA.VEHICLE.LEVEL(10) | ~REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN
        criteria |= ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.COLLECTIBLE
        criteria |= ~REQ_CRITERIA.VEHICLE.HIDDEN_IN_HANGAR | ~REQ_CRITERIA.VEHICLE.ROLES(['role_SPG_assault'])
        vUnlocked = self.__itemsCache.items.getVehicles(criteria)
        selectableCount = len(vUnlocked)
        tokenCount = value.get('count', 1)
        offerCount = min(tokenCount, selectableCount)
        compensationCount = tokenCount - offerCount
        offerCreditsCompensation = self._config.offerCreditsCompensation
        if offerCount:
            valueCopy = copy.deepcopy(value)
            valueCopy['count'] = offerCount
            result['tokens'][SENIORITY_AWARDS_VEHICLE_OFFER] = valueCopy
        if compensationCount and offerCreditsCompensation:
            valueCopy = copy.deepcopy(value)
            valueCopy['count'] = compensationCount
            valueCopy.update({'extItems': [{'bonus': {'amount': offerCreditsCompensation}}]})
            result['tokens'][_OFFER_COMPENSATION_TOKEN_NAME] = valueCopy

    @property
    def pendingReminderTimestamp(self):
        if not self.isEnabled:
            return None
        else:
            timestamp = time_utils.getServerUTCTime()
            reminders = self._config.reminders
            pendingNotifications = [ reminderTS for reminderTS in reminders if reminderTS < timestamp ]
            return max(pendingNotifications) if pendingNotifications else None

    def claimReward(self):
        self.__showWaiting()
        self.__scheduleClaimTimeout()
        BigWorld.player().requestSingleToken(self._config.claimRewardToken)

    def markRewardReceived(self):
        self.__hideWaiting()
        self.__cancelClaimTimeout()

    def onLobbyInited(self, event):
        super(SeniorityAwardsController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        if self.__hangarSpace.spaceInited:
            self.__update()
        else:
            self.__hangarSpace.onSpaceCreate += self.__onHangarLoaded

    def onAccountBecomeNonPlayer(self):
        super(SeniorityAwardsController, self).onAccountBecomeNonPlayer()
        self.__clear()

    def fini(self):
        self.onUpdated.clear()
        self.__clear()
        super(SeniorityAwardsController, self).fini()

    def onDisconnected(self):
        self.__clear()
        super(SeniorityAwardsController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()
        super(SeniorityAwardsController, self).onAvatarBecomePlayer()

    @property
    def _config(self):
        return self.__lobbyContext.getServerSettings().getSeniorityAwardsConfig() if self.__lobbyContext else SeniorityAwardsConfig()

    def __onHangarLoaded(self):
        self.__update()

    def __clear(self):
        self.__removeListeners()
        self.__cancelClaimTimeout()
        self.__endTimestamp = None
        self.__clockOnNotification = None
        return

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__hangarSpace.onSpaceCreate -= self.__onHangarLoaded
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onTokensUpdate(self, diff):
        eligibilityToken = self._config.rewardEligibilityToken
        if eligibilityToken and eligibilityToken in diff:
            self.__update()

    def __onSettingsChanged(self, diff):
        if 'seniority_awards_config' in diff:
            self.__update()

    def __scheduleClaimTimeout(self):
        self.__cancelClaimTimeout()
        self.__claimTimeoutId = BigWorld.callback(CLAIM_REWARD_TIMEOUT, self.__onClaimRewardFailed)

    def __cancelClaimTimeout(self):
        if self.__claimTimeoutId:
            BigWorld.cancelCallback(self.__claimTimeoutId)
            self.__claimTimeoutId = None
        return

    def __onClaimRewardFailed(self):
        self.__cancelClaimTimeout()
        self.__hideWaiting()
        SystemMessages.pushI18nMessage('#system_messages:seniority_awards/claim_reward_failed', type=SystemMessages.SM_TYPE.Error, priority='high')

    @staticmethod
    def __showWaiting():
        Waiting.show('claimSeniorityAwards')

    @staticmethod
    def __hideWaiting():
        Waiting.hide('claimSeniorityAwards')

    def __update(self):
        self.onUpdated()
