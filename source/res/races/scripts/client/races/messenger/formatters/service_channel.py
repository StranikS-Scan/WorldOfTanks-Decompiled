# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/messenger/formatters/service_channel.py
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import TokensBonus
from gui.shared.formatters import text_styles
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import SyncTokenQuestsSubFormatter
from races_common.races_common import checkIfViolator
from races_constants import EVENT_STATES, RACES_FIRST_WIN_QUEST
from races.skeletons.progression_controller import IRacesProgressionController
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
_NO_FINISHED_PLACE = 0
_FIRST_PLACE = 1
_THIRD_PLACE = 3

class RacesBattleResultsFormatter(BattleResultsFormatter):
    __racesProgression = dependency.descriptor(IRacesProgressionController)

    def _prepareFormatData(self, message):
        _, ctx = super(RacesBattleResultsFormatter, self)._prepareFormatData(message)
        mapDescr = backport.text(R.strings.races_messenger.serviceChannelMessages.racesEventName())
        ctx['gameMode'] = mapDescr
        if checkIfViolator(message.data):
            noResult = u'--'
            ctx['racesTotalScore'] = noResult
            ctx['finishedPlace'] = noResult
            return ('disqualification', ctx)
        ctx['questsMsg'] = self.__makeDailyQuestsString(message)
        ctx['racesTotalScore'] = backport.getIntegralFormat(message.data.get('racesTotalScore', 0))
        finishedPlace = message.data.get('position', 0)
        if _FIRST_PLACE <= finishedPlace <= _THIRD_PLACE:
            temptale = 'racesBattleResult'
        else:
            temptale = 'racesBattleResultDefeat'
        ctx['racesTitle'] = self.__makeTitleString(finishedPlace)
        ctx['finishedPlace'] = self.__makeFinishedPlaceString(finishedPlace)
        ctx['racesFirstWinAchievement'] = self.__makeAchievementString(message)
        return (temptale, ctx)

    def __makeTitleString(self, finishedPlace):
        return backport.text(R.strings.races_messenger.serviceChannelMessages.racesBattleResults.win()) if _FIRST_PLACE <= finishedPlace <= _THIRD_PLACE else backport.text(R.strings.races_messenger.serviceChannelMessages.racesBattleResults.defeat())

    def __makeFinishedPlaceString(self, finishedPlace):
        return backport.text(R.strings.races_messenger.serviceChannelMessages.racesBattleResults.noFinishedPlace()) if finishedPlace == _NO_FINISHED_PLACE else backport.getIntegralFormat(finishedPlace)

    def __makeDailyQuestsString(self, message):
        completedQuestIDs = message.data.get('completedQuestIDs', None)
        if not completedQuestIDs:
            return u''
        else:
            result = u''
            quests = self.__racesProgression.getDailyQuests()
            for questID, quest in quests.iteritems():
                if questID in completedQuestIDs:
                    bonuses = quest.getBonuses()
                    for bonus in bonuses:
                        if isinstance(bonus, TokensBonus):
                            tokens = bonus.getTokens()
                            progressionToken = tokens.get('races:progression_token', None)
                            if not progressionToken:
                                continue
                            header = backport.text(R.strings.races_messenger.serviceChannelMessages.racesBattleResults.dailyQuest.header())
                            result += header
                            poFile = R.strings.races_messenger
                            dailyQuestBody = poFile.serviceChannelMessages.racesBattleResults.dailyQuest.body()
                            resultingText = backport.text(dailyQuestBody, dailyQuestPoints=progressionToken.count)
                            formattedBody = text_styles.stats(resultingText)
                            result += formattedBody + u'\n'
                            break

            return result

    def __makeAchievementString(self, message):
        result = u''
        completedQuestIDs = message.data.get('completedQuestIDs', None)
        if RACES_FIRST_WIN_QUEST in completedQuestIDs:
            result += backport.text(R.strings.races_messenger.serviceChannelMessages.racesBattleResults.firstWinAchievement())
            result += text_styles.stats(backport.text(R.strings.achievements.races24FirstPlace()))
            return result
        else:
            return result


class RacesStateMessageFormatter(ServiceChannelFormatter):
    __TEMPLATES = {EVENT_STATES.START: 'RacesStartedMessage',
     EVENT_STATES.FINISH: 'RacesEndedMessage',
     EVENT_STATES.SUSPEND: 'RacesSuspendedMessage',
     EVENT_STATES.RESUME: 'RacesResumedMessage'}

    def format(self, message, *args):
        state = message.get('state', None)
        if state is None:
            LOG_ERROR('[RacesStateMessageFormatter] message.state is missing')
            return []
        else:
            template = self.__TEMPLATES.get(state, None)
            if template is None:
                LOG_ERROR('[RacesStateMessageFormatter] Missing template for state %s', state)
                return []
            formatted = g_settings.msgTemplates.format(template)
            return [MessageData(formatted, self._getGuiSettings(message, template))]


class RacesLootBoxesAccrual(ServiceChannelFormatter):
    __TEMPLATE = 'RacesLootBoxesAccrual'

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE)
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class RacesProgressionMessageFormatter(SyncTokenQuestsSubFormatter):
    __TEMPLATE = 'RacesProgressionMessage'
    _racesProgression = dependency.descriptor(IRacesProgressionController)

    def format(self, message, *args):
        completedStage = self._racesProgression.getCurrentStage()
        rewards = getRewardsForQuests(message, self._racesProgression.getQuests().keys())
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'racesProgressionStage': completedStage,
         'racesRewards': self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)})
        return [MessageData(formatted, self._getGuiSettings(message.data, self.__TEMPLATE))]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls._racesProgression.isRacesProgressionQuest(questID)
