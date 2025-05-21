# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/messenger/formatters/service_channel.py
from constants import AUTO_MAINTENANCE_RESULT, AUTO_MAINTENANCE_TYPE
from last_stand_common.last_stand_constants import ArtefactsSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, BattleResultsFormatter, _getRaresAchievementsStrings, AutoMaintenanceFormatter
from messenger.formatters.service_channel_helpers import MessageData
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.money import Currency
from gui.shared.formatters import getBWFormatter

class LSArtefactKeysFormatter(ServiceChannelFormatter):
    _MSG_KEY = 'lsArtefactKeysMessage'

    def format(self, message, *args):
        data = message.data
        delta = data.get('delta')
        isAdded = data.get('isAdded', False)
        return [MessageData(self._getMessage(isAdded, delta), self._getGuiSettings(message, self._MSG_KEY))] if delta is not None else []

    def _getMessage(self, isAdded, delta):
        if isAdded:
            title = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.add.title())
            description = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.add.description(), key=text_styles.stats(delta))
        else:
            title = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.draw.title())
            description = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.draw.description(), key=text_styles.stats(delta))
        ctx = {'title': title,
         'description': description}
        return g_settings.msgTemplates.format(self._MSG_KEY, ctx=ctx)


class LSDifficultyLevelFormatter(ServiceChannelFormatter):
    _MSG_KEY = 'lsDifficultyRewardCongrats'

    def format(self, message, *args):
        data = message.data
        delta = data.get('delta')
        isAdded = data.get('isAdded', False)
        return [MessageData(self._getMessage(isAdded, delta), self._getGuiSettings(message, self._MSG_KEY))] if delta is not None else []

    def _getMessage(self, isAdded, delta):
        if isAdded:
            title = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.add.title())
            description = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.add.description(), key=text_styles.credits(delta))
        else:
            title = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.draw.title())
            description = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.artefactKeys.draw.description(), key=text_styles.credits(delta))
        ctx = {'title': title,
         'description': description}
        return g_settings.msgTemplates.format(self._MSG_KEY, ctx=ctx)


class LSBattleResultsFormatter(BattleResultsFormatter):
    R_SERVICE_CHANNEL_MESSAGES = R.strings.last_stand_system_messages.serviceChannelMessages
    _battleResultKeys = {-1: 'LSBattleDefeatResult',
     0: 'LSBattleDefeatResult',
     1: 'LSBattleVictoryResult'}

    def _prepareFormatData(self, message):
        _, ctx = super(LSBattleResultsFormatter, self)._prepareFormatData(message)
        battleResults = message.data
        templateName = self._getTemplateName(battleResults)
        lsPhase = battleResults.get('phase', 0)
        lsPhasesCount = battleResults.get('phasesCount', 0)
        isWinner = battleResults.get('isWinner') == 1
        bonusType = battleResults.get('bonusType')
        ctx['difficultyLevel'] = self._getDifficultyLevel(bonusType)
        ctx['finalResult'] = self.__makeBattleResultString(lsPhase, lsPhasesCount, isWinner, bonusType)
        accCredits = battleResults.get(Currency.CREDITS, 0) - battleResults.get('creditsToDraw', 0)
        ctx[Currency.CREDITS] = '<br/>' + backport.text(R.strings.messenger.serviceChannelMessages.battleResults.credits(), text_styles.credits(getBWFormatter(Currency.CREDITS)(accCredits)))
        dailyQuestArtefactKeys = battleResults.get('tokens', {}).get(ArtefactsSettings.KEY_TOKEN, {}).get('count', 0)
        ctx['artefactKeys'] = dailyQuestArtefactKeys + battleResults.get('artefactKeys', 0)
        artefacts = sum((data.get('count', 0) for token, data in battleResults.get('tokens', {}).iteritems() if ArtefactsSettings.QUEST_PREFIX in token and token != ArtefactsSettings.KEY_TOKEN))
        ctx['artefacts'] = self.__makeArtefactString(artefacts)
        ctx['achieves'], ctx['badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
        return (templateName, ctx)

    @staticmethod
    def _getBattleTypeDescr(data):
        bonusType = data.get('bonusType')
        description = backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.battleResults.battleTypeName.num(bonusType)())
        return description

    @staticmethod
    def _getDifficultyLevel(bonusType):
        return backport.text(R.strings.last_stand_system_messages.serviceChannelMessages.battleResults.difficulty.num(bonusType)())

    def _getTemplateName(self, data):
        battleResKey = data.get('isWinner', 0)
        return self._battleResultKeys[battleResKey]

    def __makeBattleResultString(self, lsPhase, lsPhasesCount, isWinner, bonusType):
        lsPhase = lsPhasesCount if isWinner else max(0, lsPhase - 1)
        return g_settings.htmlTemplates.format('LSBattleResultWaves', ctx={'curPhase': text_styles.credits(lsPhase),
         'maxPhases': text_styles.credits(lsPhasesCount)})

    def __makeArtefactString(self, artefacts):
        if not artefacts:
            return ''
        return g_settings.htmlTemplates.format('LSBattleResultQuests', ctx={'artefacts': artefacts}) if artefacts > 1 else g_settings.htmlTemplates.format('LSBattleResultQuest', ctx={'artefacts': artefacts})

    def __makeAchievementsAndBadgesStrings(self, battleResults):
        popUpRecords = []
        badges = []
        for _, vehBattleResults in battleResults.get('playerVehicles', {}).iteritems():
            for recordIdx, value in vehBattleResults.get('popUpRecords', []):
                recordName = DB_ID_TO_RECORD[recordIdx]
                if recordName in IGNORED_BY_BATTLE_RESULTS:
                    continue
                block, name = recordName
                if block == BADGES_BLOCK:
                    badges.append(name)
                achieve = getAchievementFactory(recordName).create(value=value)
                if achieve is not None and achieve not in popUpRecords:
                    popUpRecords.append(achieve)

            if 'markOfMastery' in vehBattleResults and vehBattleResults['markOfMastery'] > 0:
                popUpRecords.append(getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, 'markOfMastery')).create(value=vehBattleResults['markOfMastery']))

        dossierResults = battleResults.get('dossier', {})
        for records in dossierResults.itervalues():
            for recordName in records:
                block, id_ = recordName
                if block == BADGES_BLOCK:
                    badges.append(id_)

        achievementsStrings = [ a.getUserName() for a in sorted(popUpRecords) ]
        raresStrings = _getRaresAchievementsStrings(battleResults)
        if raresStrings:
            achievementsStrings.extend(raresStrings)
        achievementsBlock = ''
        if achievementsStrings:
            achievementsBlock = g_settings.htmlTemplates.format('battleResultAchieves', {'achieves': ', '.join(achievementsStrings)})
        badgesBlock = ''
        if badges:
            badgesStr = ', '.join([ backport.text(R.strings.badge.dyn('badge_{}'.format(badgeID))()) for badgeID in badges ])
            badgesBlock = '<br/>' + g_settings.htmlTemplates.format('badgeAchievement', {'badges': badgesStr})
        return (achievementsBlock, badgesBlock)


class LSAutoMaintenanceFormatter(AutoMaintenanceFormatter):
    _overriddenMessages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.last_stand_system_messages.serviceChannelMessages.autoEquipError()},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.last_stand_system_messages.serviceChannelMessages.autoEquipSuccess()},
     AUTO_MAINTENANCE_RESULT.DISABLED_OPTION: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.last_stand_system_messages.serviceChannelMessages.autoEquipDisabledOption()}}
