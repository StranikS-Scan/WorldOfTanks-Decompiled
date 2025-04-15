# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/messenger/formatters/service_channel.py
import logging
from itertools import chain
import BigWorld
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import getComp7QuestType, isComp7Quest
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from comp7_common_const import Comp7QuestType
from constants import FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA, SCENARIO_RESULT
from dossiers2.custom.records import RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import QuestAchievesFormatter, BattleResultsFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)

class Comp7BattleQuestsFormatter(object):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def format(self, message):
        formattedSysMessages = []
        if message.data:
            for questID in self.__getComp7Quests(message.data.get('completedQuestIDs', set())):
                questType = getComp7QuestType(questID)
                if questType == Comp7QuestType.WEEKLY:
                    formattedMessage = self.__formatWeeklyReward(message, questID)
                elif questType == Comp7QuestType.TOKENS:
                    formattedMessage = self.__formatTokensReward(message, questID)
                else:
                    formattedMessage = None
                if formattedMessage is not None:
                    formattedSysMessages.append(formattedMessage)

        return formattedSysMessages

    def __getComp7Quests(self, questIDs):
        actualSeasonNumber = self.__comp7Ctrl.getActualSeasonNumber()
        return set((qId for qId in questIDs if isComp7Quest(qId, actualSeasonNumber)))

    def __formatTokensReward(self, message, questID):
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        dossierData = rewardsData.get('dossier')
        if dossierData:
            popUps = self.__getDossierPopUps(dossierData, message.data.get('popUpRecords', set()))
            rewardsData.update({'popUpRecords': popUps})
        if rewardsData:
            achievesFormatter = QuestAchievesFormatter()
            return g_settings.msgTemplates.format('comp7RegularRewardMessage', ctx={'title': backport.text(R.strings.comp7_ext.system_messages.tokenWeeklyReward.title()),
             'body': backport.text(R.strings.comp7_ext.system_messages.tokenWeeklyReward.body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False))})
        else:
            return None

    @staticmethod
    def __formatWeeklyReward(message, questID):
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        if rewardsData:
            achievesFormatter = QuestAchievesFormatter()
            return g_settings.msgTemplates.format('comp7RegularRewardMessage', ctx={'title': backport.text(R.strings.comp7_ext.system_messages.weeklyReward.title()),
             'body': backport.text(R.strings.comp7_ext.system_messages.weeklyReward.body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False))})
        else:
            return None

    @staticmethod
    def __getDossierPopUps(dossierData, popUpRecords):
        popUps = set()
        for dossierRecord in chain.from_iterable(dossierData.values()):
            if dossierRecord[0] in ACHIEVEMENT_BLOCK.ALL:
                achievementID = RECORD_DB_IDS.get(dossierRecord, None)
                popUps.update((popUp for popUp in popUpRecords if popUp[0] == achievementID))

        return popUps


class Comp7BattleResultsFormatter(BattleResultsFormatter):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __COMP7SeasonResultsKeys = {SCENARIO_RESULT.LOSE: 'comp7SeasonBattleDefeatResult',
     SCENARIO_RESULT.PARTIAL: 'comp7SeasonBattleDrawGameResult',
     SCENARIO_RESULT.WIN: 'comp7SeasonBattleVictoryResult'}
    __COMP7QualificationResultsKeys = {SCENARIO_RESULT.LOSE: 'comp7QualificationBattleDefeatResult',
     SCENARIO_RESULT.PARTIAL: 'comp7QualificationBattleDrawGameResult',
     SCENARIO_RESULT.WIN: 'comp7QualificationBattleVictoryResult'}

    def _formatMessages(self, message, arenaType, arenaCreateTime):
        result = super(Comp7BattleResultsFormatter, self)._formatMessages(message, arenaType, arenaCreateTime)
        templateName, _ = self._prepareFormatData(message)
        settings = self._getGuiSettings(message, templateName)
        settings.showAt = BigWorld.time()
        comp7QuestsFormatter = Comp7BattleQuestsFormatter()
        for reward in comp7QuestsFormatter.format(message):
            result.append(MessageData(reward, settings))

        return result

    def _getFairplayData(self, message):
        result = super(Comp7BattleResultsFormatter, self)._getFairplayData(message)
        text, params = result
        if params:
            _, __, ___, savedData = params
            restriction = message.data.get('restriction', None)
            extraData = restriction[2] if restriction else {}
            savedData.update({FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.COMP7_PENALTY: extraData.get('penalty', 0),
             FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.COMP7_IS_QUALIFICATION: extraData.get('qualActive', False)})
        return (text, params)

    def _prepareFormatData(self, message):
        result = super(Comp7BattleResultsFormatter, self)._prepareFormatData(message)
        templateName, ctx = result
        guiType = message.data.get('guiType', 0)
        battleResKey = message.data.get('isWinner', 0)
        if guiType == ARENA_GUI_TYPE.COMP7:
            isQualificationBattle = message.data.get('comp7QualActive', False)
            isQualificationActive = self.__comp7Controller.isQualificationActive()
            if isQualificationBattle or isQualificationActive:
                battleResultKeys = self.__COMP7QualificationResultsKeys
            else:
                battleResultKeys = self.__COMP7SeasonResultsKeys
                ctx = self.__makeComp7SeasonMsgCtx(message.data, ctx)
            templateName = battleResultKeys[battleResKey]
        elif guiType == ARENA_GUI_TYPE.TOURNAMENT_COMP7:
            battleResultKeys = self.__COMP7SeasonResultsKeys
            templateName = battleResultKeys[battleResKey]
            ctx = self.__makeTournamentComp7SeasonMsgCtx(message.data, ctx)
        return (templateName, ctx)

    def __makeComp7SeasonMsgCtx(self, battleResults, ctx):
        ctx['ratingPointsStr'] = g_settings.htmlTemplates.format('battleResultRatingPoints', {'ratingPoints': '{:+}'.format(battleResults['comp7RatingDelta'])})
        return ctx

    def __makeTournamentComp7SeasonMsgCtx(self, battleResults, ctx):
        ctx['ratingPointsStr'] = g_settings.htmlTemplates.format('battleResultRatingPoints', {'ratingPoints': str(battleResults['comp7RatingDelta'])})
        return ctx


class Comp7QualificationRewardsFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(Comp7QualificationRewardsFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result
