# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/award_controller.py
import logging
from constants import EVENT_TYPE, INVOICE_ASSET
from chat_shared import SYS_MESSAGE_TYPE
from frameworks.wulf import WindowLayer
from gui.server_events.bonuses import mergeBonuses, getMergedBonusesFromDicts
from gui.impl.lobby.awards import SupportedTokenTypes
from gui.impl.gen import R
from gui.impl import backport
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.game_control.AwardController import ServiceChannelHandler, MultiTypeServiceChannelHandler
from gui.server_events.bonuses import getAllNonQuestBonuses
from gui.shared.system_factory import registerAwardControllerHandlers
from helpers import dependency
from messenger.formatters.service_channel_helpers import getRewardsForQuests
from messenger.formatters.service_channel import QuestAchievesFormatter
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import findFirst
from new_year.ny_constants import NY_LEVEL_PREFIX, NY_MARKETPLACE_UNLOCK_ENTITLEMENT, NY_INVOICE_LEADERBOARD_REWARD_PREFIX
from new_year.gui.shared.ny_level_helper import parseNYLevelToken
from new_year_common.items import new_year
from new_year.gui.shared.event_dispatcher import showNYLevelUpWindow, showNYQuestsRewardWindow, showNYLeaderboardRewardWindow
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
from new_year_common.items.components.ny_constants import CurrentNYConstants
from new_year.tamagotchi.sys_msg.sys_msg_handler import TamagotchiSysMsgHandler
_logger = logging.getLogger(__name__)

class NewYearAtmosphereHandler(ServiceChannelHandler):
    _bootcampController = dependency.descriptor(IBootcampController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _FIRST_LEVEL = 1

    def __init__(self, awardCtrl):
        super(NewYearAtmosphereHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self.__alreadyGotForBootcamp = []

    def _needToShowAward(self, ctx):
        if not super(NewYearAtmosphereHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isNewYearToken = False
        isNew = True
        for token in message.data.get('completedQuestIDs', ''):
            level = parseNYLevelToken(token)
            if level == self._FIRST_LEVEL:
                continue
            if level or token in new_year.g_cache.collectionIDByCollectionRewards:
                isNewYearToken = True
                if self._bootcampController.isInBootcampAccount():
                    self.__alreadyGotForBootcamp.append(token)
                elif token in self.__alreadyGotForBootcamp:
                    isNew = False
                break

        return isNewYearToken and isNew

    def _showAward(self, ctx):
        data = ctx[1].data
        completedQuestIDs = data.get('completedQuestIDs', set())
        levelRewards = {}
        collectionRewards = {}
        detailedRewards = data.get('detailedRewards', {})
        for questID in completedQuestIDs:
            rewards = detailedRewards.get(questID, {})
            if questID.startswith(NY_LEVEL_PREFIX) and parseNYLevelToken(questID) != self._FIRST_LEVEL:
                level = parseNYLevelToken(questID)
                levelRewards[level] = getAllNonQuestBonuses(rewards)
            elif questID in new_year.g_cache.collectionIDByCollectionRewards:
                collectionStrId = new_year.g_cache.collectionIDByCollectionRewards[questID]
                collectionRewards[collectionStrId] = getAllNonQuestBonuses(rewards)
            if NY_MARKETPLACE_UNLOCK_ENTITLEMENT in rewards.get('entitlements', {}):
                self.__pushMessage()

        if levelRewards:
            self.__showWindow({'levelRewards': levelRewards})
        if collectionRewards:
            self.__showWindow({'collectionRewards': collectionRewards})

    @classmethod
    def __showWindow(cls, ctx):
        showNYLevelUpWindow(layer=WindowLayer.TOP_WINDOW, **ctx)

    def __pushMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.ny.notification.previousStyles.text()), type=SM_TYPE.NewYearPreviousStyleShop, messageData={'header': backport.text(R.strings.ny.notification.header())})


class NewYearQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(NewYearQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.versusAIBattleResults.index()), awardCtrl)

    @staticmethod
    def __showWindow(rewards):
        showNYQuestsRewardWindow(data=rewards)

    @staticmethod
    def _isAppropriate(quest):
        return quest.getType() == EVENT_TYPE.BATTLE_QUEST

    def _showAward(self, ctx):
        data = ctx[1].data
        if data is None:
            return
        else:
            detailedRewards = data.get('detailedRewards', {})
            completedQuestIDs = [ questId for questId in data.get('completedQuestIDs', set()) if questId.startswith(CurrentNYConstants.NY_DAILY_QUESTS_PREFIX) or questId.startswith(CurrentNYConstants.NY_WEEKLY_QUESTS_PREFIX) ]
            questRewards = []
            machineRewards = []
            for questId in completedQuestIDs:
                for reward in getAllNonQuestBonuses(detailedRewards.get(questId, {})):
                    if reward.getName() == SupportedTokenTypes.LOOTBOX_TOKEN and reward.getTokens().keys()[0] == getMachineLootboxToken():
                        machineRewards.append(reward)
                        continue
                    questRewards.append(reward)

            if questRewards or machineRewards:
                self.__showWindow(mergeBonuses(questRewards) + mergeBonuses(machineRewards))
            return

    def __sendRewardNotification(self, completedQuestIds, data):
        completedQuestRewards = getRewardsForQuests(data, set(completedQuestIds))
        formattedRewards = QuestAchievesFormatter.formatQuestAchieves(completedQuestRewards, asBattleFormatter=False)
        SystemMessages.pushMessage(formattedRewards, type=SM_TYPE.NewYearQuestsReward, messageData={'header': backport.text(R.strings.ny.questGiver.name()),
         'description': '{}\n{}'.format(backport.text(R.strings.ny.questGiver.questCompleted()), backport.text(R.strings.ny.questGiver.rewards()))})


class NewYearWeeklyRewardHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(NewYearWeeklyRewardHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)
        self.__leaderboardSeasonToRewards = {}

    def _needToShowAward(self, ctx):
        isNeedToShow = super(NewYearWeeklyRewardHandler, self)._needToShowAward(ctx)
        seasonId = self.__getRewardsSeasonID(ctx)
        if seasonId is None:
            return True
        elif isNeedToShow:
            self.__appendRewards(ctx, seasonId)
            return self.__canShow(seasonId)
        else:
            return False

    def __appendRewards(self, ctx, seasonId):
        invoiceData = self.__getProductInvoiceData(ctx)
        if invoiceData is None:
            return
        else:
            rewardsDict = invoiceData.get('data', {})
            for key, value in rewardsDict.iteritems():
                self.__leaderboardSeasonToRewards.setdefault(seasonId, []).append({key: value})

            return

    def _showAward(self, ctx):
        seasonId = self.__getRewardsSeasonID(ctx)
        if seasonId is not None:
            self.__processLeaderboardRewards(seasonId)
        return

    def __processLeaderboardRewards(self, seasonId):
        seasonRewards = self.__leaderboardSeasonToRewards.get(seasonId, [])
        rewards = getMergedBonusesFromDicts(seasonRewards)
        if rewards:
            showNYLeaderboardRewardWindow(rewards, seasonId)
            TamagotchiSysMsgHandler.sendRewardNotification(rewards, seasonId)
            self.__leaderboardSeasonToRewards.pop(seasonId, None)
        else:
            TamagotchiSysMsgHandler.sendNotifWithoutReward(seasonId)
        return

    def __canShow(self, seasonID):
        seasonRewards = self.__leaderboardSeasonToRewards.get(seasonID)
        if not seasonRewards:
            return True
        dogTagComponents = [ item for item in seasonRewards if 'dogTagComponents' in item ]
        if not dogTagComponents:
            return True
        return False if len(dogTagComponents) < 2 else True

    def __getRewardsSeasonID(self, ctx):
        invoiceData = self.__getProductInvoiceData(ctx)
        if invoiceData is None:
            return
        else:
            nyLeaderboardTag = self.__extractLeaderboardTag(invoiceData)
            return None if nyLeaderboardTag is None else self.__parseLeaderboardTag(nyLeaderboardTag)

    def __getProductInvoiceData(self, ctx):
        invoiceData = ctx[1].data
        return invoiceData if invoiceData and isinstance(invoiceData, dict) and invoiceData.get('assetType') == INVOICE_ASSET.PURCHASE else None

    def __extractLeaderboardTag(self, invoiceData):
        tags = invoiceData.get('tags', [])
        return findFirst(lambda tag: tag.startswith(NY_INVOICE_LEADERBOARD_REWARD_PREFIX), tags)

    def __parseLeaderboardTag(self, tag):
        result = tag.split('_')
        if len(result) < 3 or not result[2].isdigit():
            _logger.error('[NewYearWeeklyRewardHandler]: incorrect leaderboard tag format')
            return None
        else:
            return int(result[2])


def registerNewYearAwardControllerHandlers():
    registerAwardControllerHandlers((NewYearAtmosphereHandler, NewYearQuestHandler, NewYearWeeklyRewardHandler))
