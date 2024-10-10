# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/messenger/formatters/service_channel.py
import logging
import typing
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import ZERO_MONEY, Money, Currency
from gui.shared.notifications import NotificationPriorityLevel
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from messenger import g_settings
from gui.shared.formatters import text_styles
from constants import LOOTBOX_TOKEN_PREFIX
from helpers import dependency
from messenger.formatters.service_channel import WaitItemsSyncFormatter, BattleResultsFormatter, ServiceChannelFormatter, QuestAchievesFormatter, InvoiceReceivedFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.game_control import IWhiteTigerController
from client_constants import EVENT_STATES
from white_tiger_common import wt_constants
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

class WTBattleResultsFormatter(BattleResultsFormatter):
    __gameEventController = dependency.descriptor(IWhiteTigerController)
    __WT_BATTLE_QUEST_PREFIX = 'wtevent:battle_quest:event'
    _battleResultKeys = {-1: 'WTEventBattleDefeatResult',
     0: 'WTEventBattleDefeatResult',
     1: 'WTEventBattleVictoryResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(WTBattleResultsFormatter, self)._prepareFormatData(message)
        battleResults = message.data
        self.__fillWTEventMsgCtx(battleResults, ctx)
        return (templateName, ctx)

    def _getBackgroundIconSource(self, battleResults):
        return 'bgVictory' if battleResults.get('isWinner', 0) else 'bgDefeat'

    def __fillWTEventMsgCtx(self, battleResults, ctx):
        strRes = R.strings.white_tiger.notifications.battleResults
        mainResultName = 'victory' if battleResults.get('isWinner', -1) == 1 else 'defeat'
        ctx['mainResultName'] = backport.text(strRes.dyn(mainResultName).header())
        ctx['eventName'] = backport.text(strRes.eventName())
        team = battleResults.get('team', -1)
        if team == wt_constants.WT_TEAMS.BOSS_TEAM:
            teamName = backport.text(strRes.team.boss())
        elif team == wt_constants.WT_TEAMS.HUNTERS_TEAM:
            teamName = backport.text(strRes.team.hunters())
        else:
            teamName = ''
            _logger.warning('Unexpected team type: %r', team)
        ctx['teamName'] = teamName
        ctx['quests'] = ''
        completedQuestIDs = battleResults.get('completedQuestIDs', ())
        if self.__containsWTBattleQuest(completedQuestIDs):
            ctx['quests'] = '<br>%s' % text_styles.main(backport.text(strRes.questCompleted()))
        ctx['stamps'] = ''
        tokens = battleResults.get('tokens', {})
        stampToken = self.__gameEventController.getConfig().stamp
        if stampToken in tokens:
            earnedCount = tokens[stampToken].get('count', 0)
            if earnedCount > 0:
                ctx['stamps'] = '<br>%s' % text_styles.main(backport.text(strRes.stamp(), count=text_styles.expText(earnedCount)))
        ctx['tickets'] = ''
        ticketToken = self.__gameEventController.getConfig().ticketToken
        if ticketToken in tokens:
            earnedCount = tokens[ticketToken].get('count', 0)
            if earnedCount > 0:
                ctx['tickets'] = '<br>%s' % text_styles.main(backport.text(strRes.ticket(), count=text_styles.expText(earnedCount)))
                self.__pushTicketsEarnedMessage()
        ctx['lootboxes'] = ''
        lootboxesStrs = []
        for tID, tVal in tokens.items():
            if tID.startswith(LOOTBOX_TOKEN_PREFIX):
                lootBox = self._itemsCache.items.tokens.getLootBoxByTokenID(tID)
                if lootBox is not None:
                    lootboxesStrs.append(backport.text(strRes.lootboxes.dyn(lootBox.getType())(), count=text_styles.expText(tVal.get('count', 0))))

        if lootboxesStrs:
            ctx['lootboxes'] = '<br>%s' % text_styles.main('<br>'.join(lootboxesStrs))
        return

    def __pushTicketsEarnedMessage(self):
        strRes = R.strings.white_tiger.notifications.ticketToken.received
        SystemMessages.pushMessage(text=backport.text(strRes.body(), ticketsCount=str(self.__gameEventController.getTicketCount())), messageData={'header': backport.text(strRes.header())}, type=SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)

    def __containsWTBattleQuest(self, questIDs):
        for questID in questIDs:
            if questID.startswith(self.__WT_BATTLE_QUEST_PREFIX):
                return True

        return False


class WTEventTicketTokenWithdrawnFormatter(WaitItemsSyncFormatter):
    __wtController = dependency.descriptor(IWhiteTigerController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        data = message.data
        isSynced = yield self._waitForSyncItems()
        if isSynced and data:
            token = data['token']
            amountDelta = data['amount_delta']
            if amountDelta >= 0:
                raise SoftException('Unexpected ticket amount to withdraw')
            strRes = R.strings.event.notifications
            config = self.__wtController.getConfig()
            if token == config.ticketToken:
                text = backport.text(strRes.ticketToken.withdrawn.body(), ticketsCount=str(self.__wtController.getTicketCount()))
            elif token == config.quickBossTicketToken:
                text = backport.text(strRes.quickBossTicketToken.withdrawn.body())
            else:
                raise SoftException('Unexpected ticket token')
            xmlKey = 'WTEventTicketTokenWithdrawn'
            formatted = g_settings.msgTemplates.format(xmlKey, ctx={'text': text})
            callback([MessageData(formatted, self._getGuiSettings(message, xmlKey))])
        else:
            callback([MessageData(None, None)])
        return


class WTEventStateMessageFormatter(ServiceChannelFormatter):
    __TEMPLATES = {EVENT_STATES.START: 'WTEventStartedMessage',
     EVENT_STATES.FINISH: 'WTEventEndedMessage'}

    def format(self, message, *args):
        state = message.get('state', None)
        if state is None:
            _logger.error('[WTEventStateMessageFormatter] message.state is missing')
            return []
        else:
            template = self.__TEMPLATES.get(state, None)
            if template is None:
                _logger.error('[WTEventStateMessageFormatter] Missing template for state %s', state)
                return []
            formatted = g_settings.msgTemplates.format(template)
            return [MessageData(formatted, self._getGuiSettings(message, template))]


class WTEventLootBoxMessageFormatter(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __strRes = R.strings.white_tiger.notifications.lootBoxes

    @classmethod
    def formatLootBoxRewards(cls, rewards):
        rewardsReceived = text_styles.titleFont(backport.text(cls.__strRes.rewardsReceived()))
        compensation, compensatedVehicles = cls.__formatCompensation(rewards)
        lootBoxesStr = cls.__formatLootBoxesTokens(rewards.get('tokens', {}))
        rewardsStr = QuestAchievesFormatter.formatQuestAchieves(rewards, False)
        rewards.get('vehicles', []).extend(compensatedVehicles)
        return '{0}<br/>{1}<br/>{2}{3}'.format(lootBoxesStr, rewardsReceived, rewardsStr, compensation)

    @classmethod
    def formatTankPortalRewards(cls, ctx):
        compensation, compensatedVehicles = cls.__formatCompensation(ctx)
        lootBoxesStr = cls.__formatLootBoxesTokens(ctx.get('tokens', {}))
        vehiclesList = ctx.get('vehicles', [])
        vehMsg = InvoiceReceivedFormatter.getVehiclesString(vehiclesList, htmlTplPostfix='QuestsReceived')
        ctx.get('vehicles', []).extend(compensatedVehicles)
        return '{0}<br/>{1}<br/>{2}'.format(lootBoxesStr, vehMsg, compensation)

    @classmethod
    def __formatCompensation(cls, rewards):
        compensationHeader = text_styles.titleFont(backport.text(cls.__strRes.compensation.header()))
        cls.__preformatCompensationValue(rewards)
        compensation = cls.__formatVehiclesCompensation(rewards)
        compensatedVehicles = []
        if compensation:
            compensation = '<br/><br/>{0}<br/>{1}'.format(compensationHeader, compensation)
            compensatedVehicles = cls.__filterRewardsByVehicleCompensation(rewards)
        return (compensation, compensatedVehicles)

    @classmethod
    def __formatLootBoxesTokens(cls, tokens):
        for tokenID, tokenValue in tokens.items():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                lootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
                if lootBox is not None:
                    return backport.text(cls.__strRes.dyn(lootBox.getType())(), count=abs(tokenValue.get('count', 0)))

        return ''

    @classmethod
    def __formatVehiclesCompensation(cls, rewards):
        vehiclesList = rewards.get('vehicles', {})
        compensation = InvoiceReceivedFormatter.getVehiclesCompensationString(vehiclesList, htmlTplPostfix='QuestsReceived')
        return compensation

    @classmethod
    def __filterRewardsByVehicleCompensation(cls, rewards):
        compensatedVehicles = []
        vehiclesList = rewards.get('vehicles', {})
        for ind, vehicleDict in enumerate(vehiclesList):
            for vehicleData in vehicleDict.values():
                if 'customCompensation' in vehicleData:
                    compensatedVehicles.append(vehicleDict)
                    vehiclesList.pop(ind)

        return compensatedVehicles

    @classmethod
    def __preformatCompensationValue(cls, rewards):
        vehiclesList = rewards.get('vehicles', [])
        compValue = cls.__getCompensationValue(vehiclesList)
        for currency in Currency.ALL:
            if compValue.get(currency, 0) > 0:
                currencyValue = rewards.pop(currency, None)
                if currencyValue is not None:
                    newCurrencyValue = currencyValue - compValue.get(currency, 0)
                    if newCurrencyValue:
                        rewards[currency] = newCurrencyValue

        return

    @classmethod
    def __getCompensationValue(cls, vehicles):
        comp = ZERO_MONEY
        for vehicleDict in vehicles:
            for vehData in vehicleDict.values():
                if 'customCompensation' in vehData:
                    comp += Money.makeFromMoneyTuple(vehData['customCompensation'])

        return comp
