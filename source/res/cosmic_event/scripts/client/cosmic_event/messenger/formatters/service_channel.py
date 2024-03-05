# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/messenger/formatters/service_channel.py
import logging
from typing import TYPE_CHECKING
from gui.shared.formatters import text_styles
from cosmic_constants import EVENT_STATES
from cosmic_event.cosmic_constants import PROGRESSION_TOKEN
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from cosmic_event_common.cosmic_event_common import checkIfViolator
from gui.impl import backport
from gui.impl.gen import R
from helpers import int2roman, dependency
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import SyncTokenQuestsSubFormatter
from cosmic_event.gui.gui_constants import ACHIEVEMENTS_IDS
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Dict, Any, List

class CosmicBattleResultsFormatter(BattleResultsFormatter):

    def _prepareFormatData(self, message):
        _, ctx = super(CosmicBattleResultsFormatter, self)._prepareFormatData(message)
        ctx['totalScore'] = self.__makeTotalScoreString(message)
        return ('cosmicBattleResult', ctx)

    @staticmethod
    def __makeTotalScoreString(message):
        value = message.data.get('cosmicTotalScore', 0) if not checkIfViolator(message.data) else 0
        return backport.getIntegralFormat(value)


def formatCosmicQuestBonuses(rewards):
    results = []
    progressionTokens = rewards.get('tokens', {}).get(PROGRESSION_TOKEN, {}).get('count', 0)
    if progressionTokens:
        results.append(g_settings.htmlTemplates.format('cosmicEventProgressionToken', ctx={'progressionTokens': backport.getIntegralFormat(progressionTokens)}))
    formattedResults = QuestAchievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
    if formattedResults:
        results.append(formattedResults)
    return '<br/>'.join(results)


class CosmicDailyMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'CosmicDailyMessage'
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    def format(self, message, *args):
        rewards = message.get('rewards', {})
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'rewards': formatCosmicQuestBonuses(rewards)})
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls._isQuestOfThisGroup(questID)


class CosmicProgressionMessageFormatter(SyncTokenQuestsSubFormatter):
    __TEMPLATE = 'CosmicProgressionMessage'
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    def format(self, message, *args):
        stage = self._cosmicProgression.getCurrentStage()
        rewards = getRewardsForQuests(message, self._cosmicProgression.getQuests().keys())
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'stage': int2roman(stage),
         'rewards': self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)})
        return [MessageData(formatted, self._getGuiSettings(message.data, self.__TEMPLATE))]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        isNotAchievement = questID not in ACHIEVEMENTS_IDS
        return isNotAchievement and cls._cosmicProgression.isCosmicProgressionQuest(questID)


class CosmicAchievementsMessageFormatter(SyncTokenQuestsSubFormatter):
    __TEMPLATE = 'CosmicAchievementsMessage'
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    def format(self, message, *args):
        completedQuestIDs = set(message.data.get('completedQuestIDs', {}))
        if not completedQuestIDs:
            return []
        achievementsQuests = self._cosmicProgression.getAchievementsQuests()
        resQuest = [ quest for key, quest in achievementsQuests.iteritems() if key in completedQuestIDs ]
        achievementStrList = []
        for quest in resQuest:
            for bonus in quest.getBonuses():
                for achievement in bonus.getAchievements():
                    text = backport.text(R.strings.cosmic_messenger.serviceChannelMessages.cosmicAchievement(), achievement=achievement.getUserName())
                    achievementStrList.append('{0}\n'.format(text_styles.titleFont(text)))

        if not achievementStrList:
            return []
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'achievements': ''.join(achievementStrList)})
        return [MessageData(formatted, self._getGuiSettings(message.data, self.__TEMPLATE))]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID in ACHIEVEMENTS_IDS


class CosmicVehicleRentMessageFormatter(SyncTokenQuestsSubFormatter):

    def format(self, message, *args):
        return None

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return dependency.instance(ICosmicEventBattleController).isVehicleRentQuest(questID)


class CosmicEventStateMessageFormatter(ServiceChannelFormatter):
    __TEMPLATES = {EVENT_STATES.START: 'CosmicEventStartedMessage',
     EVENT_STATES.FINISH: 'CosmicEventEndedMessage',
     EVENT_STATES.SUSPEND: 'CosmicEventSuspendedMessage',
     EVENT_STATES.RESUME: 'CosmicEventResumedMessage'}

    def format(self, message, *args):
        state = message.get('state', None)
        if state is None:
            _logger.error('[CosmicEventStateMessageFormatter] message.state is missing')
            return []
        else:
            template = self.__TEMPLATES.get(state, None)
            if template is None:
                _logger.error('[CosmicEventStateMessageFormatter] Missing template for state %s', state)
                return []
            formatted = g_settings.msgTemplates.format(template)
            return [MessageData(formatted, self._getGuiSettings(message, template))]
