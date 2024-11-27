# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/award_controller.py
import logging
from constants import EVENT_TYPE
from chat_shared import SYS_MESSAGE_TYPE
from frameworks.wulf import WindowLayer
from gui.server_events.bonuses import mergeBonuses
from gui.impl.lobby.awards import SupportedTokenTypes
from gui.impl.gen import R
from gui.impl import backport
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.game_control.AwardController import ServiceChannelHandler, BattleQuestsAutoWindowHandler
from gui.server_events.bonuses import getAllNonQuestBonuses
from gui.shared.system_factory import registerAwardControllerHandlers
from helpers import dependency
from messenger.formatters.service_channel_helpers import getRewardsForQuests
from messenger.formatters.service_channel import QuestAchievesFormatter
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from new_year.ny_constants import NY_LEVEL_PREFIX, NY_MARKETPLACE_UNLOCK_ENTITLEMENT
from new_year.gui.shared.ny_level_helper import parseNYLevelToken
from new_year_common.items import new_year
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.gui.shared.event_dispatcher import showNYLevelUpWindow, showNYQuestsRewardWindow
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
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


class NewYearQuestHandler(BattleQuestsAutoWindowHandler):

    @staticmethod
    def __showWindow(rewards):
        showNYQuestsRewardWindow(data=rewards)

    @staticmethod
    def _isAppropriate(quest):
        return quest.getType() == EVENT_TYPE.BATTLE_QUEST

    def _showAward(self, ctx):
        config = getNewYearGeneralConfig()
        dailyPrefix = config.getDailyPrefix()
        weeklyPrefix = config.getWeeklyPrefix()
        if dailyPrefix and weeklyPrefix:
            data = ctx[1].data
            detailedRewards = data.get('detailedRewards', {})
            completedQuestIDs = [ questId for questId in data.get('completedQuestIDs', set()) if questId.startswith(dailyPrefix) or questId.startswith(weeklyPrefix) ]
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
                self.__sendRewardNotification(completedQuestIDs, ctx[1])

    def __sendRewardNotification(self, completedQuestIds, data):
        completedQuestRewards = getRewardsForQuests(data, set(completedQuestIds))
        formattedRewards = QuestAchievesFormatter.formatQuestAchieves(completedQuestRewards, asBattleFormatter=False)
        SystemMessages.pushMessage(formattedRewards, type=SM_TYPE.NewYearQuestsReward, messageData={'header': backport.text(R.strings.ny.questGiver.name()),
         'description': '{}\n{}'.format(backport.text(R.strings.ny.questGiver.questCompleted()), backport.text(R.strings.ny.questGiver.rewards()))})


def registerNewYearAwardControllerHandlers():
    registerAwardControllerHandlers((NewYearAtmosphereHandler, NewYearQuestHandler))
