# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/messenger/formatters/service_channel.py
from __future__ import absolute_import
from constants import AUTO_MAINTENANCE_RESULT, AUTO_MAINTENANCE_TYPE
from gui.shared.notifications import NotificationPriorityLevel
from halloween_common.halloween_constants import ArtefactsSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, BattleResultsFormatter, _getRaresAchievementsStrings, AutoMaintenanceFormatter, InvoiceReceivedFormatter
from messenger.formatters.service_channel_helpers import MessageData
from gui.shared.gui_items.Vehicle import getUserName
from items import vehicles as vehicles_core
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.money import Currency
from gui.shared.formatters import getBWFormatter

class HWVehicleRentFormatter(ServiceChannelFormatter):
    _MSG_KEY = 'HWVehicleRentMessage'

    def format(self, message, *args):
        data = message.data
        intCD = data.get('intCD')
        return [MessageData(self._getMessage(intCD), self._getGuiSettings(message, self._MSG_KEY))] if intCD is not None else []

    def _getMessage(self, intCD):
        vehicleName = getUserName(vehicles_core.getVehicleType(intCD))
        ctx = {'description': backport.text(R.strings.halloween_system_messages.serviceChannelMessages.halloweenHangar.vehicleAcquired(), vehicle=vehicleName)}
        return g_settings.msgTemplates.format(self._MSG_KEY, ctx=ctx)


class HWArtefactKeysFormatter(ServiceChannelFormatter):
    _MSG_KEY = 'hwArtefactKeysMessage'

    def format(self, message, *args):
        data = message.data
        delta = data.get('delta')
        isAdded = data.get('isAdded', False)
        priority = NotificationPriorityLevel.MEDIUM if isAdded else None
        return [MessageData(self._getMessage(isAdded, delta), self._getGuiSettings(message, self._MSG_KEY, priority))] if delta is not None else []

    def _getMessage(self, isAdded, delta):
        if isAdded:
            title = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.add.title())
            description = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.add.description(), key=text_styles.stats(delta))
        else:
            title = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.draw.title())
            description = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.draw.description(), key=text_styles.stats(delta))
        ctx = {'title': title,
         'description': description}
        return g_settings.msgTemplates.format(self._MSG_KEY, ctx=ctx)


class HWDifficultyLevelFormatter(ServiceChannelFormatter):
    _MSG_KEY = 'hwDifficultyRewardCongrats'

    def format(self, message, *args):
        data = message.data
        delta = data.get('delta')
        isAdded = data.get('isAdded', False)
        return [MessageData(self._getMessage(isAdded, delta), self._getGuiSettings(message, self._MSG_KEY))] if delta is not None else []

    def _getMessage(self, isAdded, delta):
        if isAdded:
            title = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.add.title())
            description = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.add.description(), key=text_styles.credits(delta))
        else:
            title = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.draw.title())
            description = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.artefactKeys.draw.description(), key=text_styles.credits(delta))
        ctx = {'title': title,
         'description': description}
        return g_settings.msgTemplates.format(self._MSG_KEY, ctx=ctx)


class HalloweenBattleResultsFormatter(BattleResultsFormatter):
    R_SERVICE_CHANNEL_MESSAGES = R.strings.halloween_system_messages.serviceChannelMessages
    _battleResultKeys = {-1: 'HWbattleDefeatResult',
     0: 'HWbattleDefeatResult',
     1: 'HWBattleVictoryResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(HalloweenBattleResultsFormatter, self)._prepareFormatData(message)
        battleResults = message.data
        halloweenPhase = battleResults.get('halloween_phase', 0)
        halloweenPhasesCount = battleResults.get('halloween_phases_count', 0)
        isWinner = battleResults.get('isWinner') == 1
        bonusType = battleResults.get('bonusType')
        ctx['difficultyLevel'] = self._getDifficultyLevel(bonusType)
        ctx['finalResult'] = self.__makeBattleResultString(halloweenPhase, halloweenPhasesCount, isWinner)
        accCredits = battleResults.get(Currency.CREDITS, 0) - battleResults.get('creditsToDraw', 0)
        ctx[Currency.CREDITS] = '<br/>' + backport.text(R.strings.messenger.serviceChannelMessages.battleResults.credits(), text_styles.credits(getBWFormatter(Currency.CREDITS)(accCredits)))
        dailyQuestArtefactKeys = battleResults.get('tokens', {}).get(ArtefactsSettings.KEY_TOKEN, {}).get('count', 0)
        ctx['artefactKeys'] = dailyQuestArtefactKeys + battleResults.get('artefactKeys', 0)
        artefacts = sum((data.get('count', 0) for token, data in battleResults.get('tokens', {}).items() if ArtefactsSettings.QUEST_PREFIX in token and token != ArtefactsSettings.KEY_TOKEN))
        ctx['artefacts'] = self.__makeArtefactString(artefacts)
        ctx['achieves'], ctx['badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
        return (templateName, ctx)

    @staticmethod
    def _getBattleTypeDescr(data):
        bonusType = data.get('bonusType')
        description = backport.text(R.strings.halloween_system_messages.serviceChannelMessages.battleResults.battleTypeName.num(bonusType)())
        return description

    @staticmethod
    def _getDifficultyLevel(bonusType):
        return backport.text(R.strings.halloween_system_messages.serviceChannelMessages.battleResults.difficulty.num(bonusType)())

    def __makeBattleResultString(self, halloweenPhase, halloweenPhasesCount, isWinner):
        return g_settings.htmlTemplates.format('battleResultBossDefeated') if isWinner else g_settings.htmlTemplates.format('battleResultPhases', ctx={'curPhase': text_styles.credits(max(0, halloweenPhase - 1)),
         'maxPhases': text_styles.credits(halloweenPhasesCount)})

    def __makeArtefactString(self, artefacts):
        if not artefacts:
            return ''
        return g_settings.htmlTemplates.format('battleResultQuests', ctx={'artefacts': artefacts}) if artefacts > 1 else g_settings.htmlTemplates.format('battleResultQuest', ctx={'artefacts': artefacts})

    def __makeAchievementsAndBadgesStrings(self, battleResults):
        popUpRecords = []
        badges = []
        for _, vehBattleResults in battleResults.get('playerVehicles', {}).items():
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
        for records in dossierResults.values():
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


class HWAutoMaintenanceFormatter(AutoMaintenanceFormatter):
    _overriddenMessages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.halloween_system_messages.serviceChannelMessages.autoEquipError()},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.halloween_system_messages.serviceChannelMessages.autoEquipSuccess()},
     AUTO_MAINTENANCE_RESULT.DISABLED_OPTION: {AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.halloween_system_messages.serviceChannelMessages.autoEquipDisabledOption()}}


class HWInvoiceReceivedLowPriorityFormatter(InvoiceReceivedFormatter):

    def _getGuiSettings(self, data, key=None, priorityLevel=None, messageType=None, messageSubtype=None, decorator=None):
        if priorityLevel is None:
            priorityLevel = NotificationPriorityLevel.LOW
        return super(HWInvoiceReceivedLowPriorityFormatter, self)._getGuiSettings(data, key, priorityLevel, messageType, messageSubtype, decorator)
