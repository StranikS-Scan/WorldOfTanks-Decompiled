# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel.py
import operator
import re
import time
import types
from Queue import Queue
from collections import namedtuple
import ArenaType
import BigWorld
import constants
import personal_missions
from adisp import async, process
from chat_shared import decompressSysMessage
from constants import INVOICE_ASSET, AUTO_MAINTENANCE_TYPE, AUTO_MAINTENANCE_RESULT, PREBATTLE_TYPE, FINISH_REASON, KICK_REASON_NAMES, KICK_REASON, NC_MESSAGE_TYPE, NC_MESSAGE_PRIORITY, SYS_MESSAGE_CLAN_EVENT, SYS_MESSAGE_CLAN_EVENT_NAMES, ARENA_GUI_TYPE, SYS_MESSAGE_FORT_EVENT_NAMES, EVENT_TYPE
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from gui import GUI_SETTINGS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.BADGE import BADGE
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE
from gui.clans.formatters import getClanFullName
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.ranked_models import PostBattleRankInfo
from gui.server_events.awards_formatters import CompletionTokensBonusFormatter
from gui.server_events.bonuses import VehiclesBonus, DEFAULT_CREW_LVL
from gui.server_events.recruit_helper import getSourceIdFromQuest
from gui.server_events.finders import PERSONAL_MISSION_TOKEN
from gui.shared import formatters as shared_fmts
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import getBWFormatter, getStyle
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import getUserName, getShortUserName
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings, NotificationGroup
from gui.shared.utils.transport import z_loads
from helpers import dependency
from helpers import i18n, html, getLocalizedData
from helpers import time_utils
from items import getTypeInfoByIndex, getTypeInfoByName, vehicles as vehicles_core, tankmen
from messenger import g_settings
from messenger.ext import passCensor
from messenger.formatters import TimeFormatter, NCContextItemFormatter
from messenger.m_constants import MESSENGER_I18N_FILE
from shared_utils import BoundMethodWeakref, findFirst, first
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from items import makeIntCompactDescrByID
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items.components.c11n_constants import CustomizationType, DecalType
from gui.impl.lobby.loot_box.loot_box_helper import getMergedLootBoxBonuses
_EOL = '\n'
_DEFAULT_MESSAGE = 'defaultMessage'
_RENT_TYPES = {'time': 'rentDays',
 'battles': 'rentBattles',
 'wins': 'rentWins'}

def _getTimeStamp(message):
    if message.createdAt is not None:
        result = time_utils.getTimestampFromUTC(message.createdAt.timetuple())
    else:
        result = time_utils.getCurrentTimestamp()
    return result


_CustomizationItemData = namedtuple('_CustomizationItemData', ('guiItemType', 'userName'))

def _getCustomizationItemData(itemId, custType):
    itemsCache = dependency.instance(IItemsCache)
    customizationType = None
    if custType == 'paint':
        customizationType = CustomizationType.PAINT
    elif custType == 'camouflage':
        customizationType = CustomizationType.CAMOUFLAGE
    elif custType == 'modification':
        customizationType = CustomizationType.MODIFICATION
    elif custType == 'style':
        customizationType = CustomizationType.STYLE
    elif custType == 'decal':
        customizationType = CustomizationType.DECAL
    elif custType == 'projection_decal':
        customizationType = CustomizationType.PROJECTION_DECAL
    elif custType == 'personal_number':
        customizationType = CustomizationType.PERSONAL_NUMBER
    compactDescr = makeIntCompactDescrByID('customizationItem', customizationType, itemId)
    item = itemsCache.items.getItemByCD(compactDescr)
    if custType == 'decal':
        descriptor = item.descriptor
        if descriptor.type == DecalType.EMBLEM:
            custType = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EMBLEM]
        elif descriptor.type == DecalType.INSCRIPTION:
            custType = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.INSCRIPTION]
    itemName = item.userName
    return _CustomizationItemData(custType, itemName)


def _extendCustomizationData(newData, extendable, htmlTplPostfix):
    if extendable is None:
        return
    else:
        customizations = newData.get('customizations', [])
        for customizationItem in customizations:
            custType = customizationItem['custType']
            custValue = customizationItem['value']
            if custValue > 0:
                operation = 'added'
            elif custValue < 0:
                operation = 'removed'
            else:
                operation = None
            if operation is not None:
                guiItemType, _ = _getCustomizationItemData(customizationItem['id'], custType)
                custValue = abs(custValue)
                if custValue > 1:
                    extendable.append(i18n.makeString('#system_messages:customization/{}/{}Value'.format(operation, guiItemType), custValue))
                else:
                    extendable.append(i18n.makeString('#system_messages:customization/{}/{}'.format(operation, guiItemType)))
            if 'compensatedNumber' in customizationItem:
                compStr = InvoiceReceivedFormatter.getCustomizationCompensationString(customizationItem, htmlTplPostfix=htmlTplPostfix)
                extendable.append(compStr)

        return


def _processRareAchievements(rares):
    unknownAchieves = 0
    achievements = []
    for rareID in rares:
        achieve = getAchievementFactory((ACHIEVEMENT_BLOCK.RARE, rareID)).create()
        if achieve is None:
            unknownAchieves += 1
        achievements.append(achieve.getUserName())

    if unknownAchieves:
        achievements.append(i18n.makeString('#system_messages:%s/title' % ('actionAchievements' if unknownAchieves > 1 else 'actionAchievement')))
    return achievements


def _getRaresAchievementsStirngs(battleResults):
    dossiers = battleResults.get('dossier', {})
    rares = []
    for d in dossiers.itervalues():
        for (blck, _), rec in d.iteritems():
            if blck == ACHIEVEMENT_BLOCK.RARE:
                value = rec['value']
                if value > 0:
                    rares.append(value)

    return _processRareAchievements(rares) if rares else None


def _getDefaultMessage(normal='', bold=''):
    return g_settings.msgTemplates.format(_DEFAULT_MESSAGE, {'normal': normal,
     'bold': bold})


_MessageData = namedtuple('MessageData', 'data, settings')

class ServiceChannelFormatter(object):

    def format(self, data, *args):
        return []

    def isNotify(self):
        return True

    def isAsync(self):
        return False

    def _getGuiSettings(self, data, key=None, priorityLevel=None, messageType=None):
        try:
            isAlert = data.isHighImportance and data.active
        except AttributeError:
            isAlert = False

        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel, isAlert, messageType=messageType)

    def canBeEmpty(self):
        return False


class WaitItemsSyncFormatter(ServiceChannelFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__callbackQueue = None
        return

    def isAsync(self):
        return True

    @async
    def _waitForSyncItems(self, callback):
        if self.itemsCache.isSynced():
            callback(True)
        else:
            self.__registerHandler(callback)

    def __registerHandler(self, callback):
        if not self.__callbackQueue:
            self.__callbackQueue = Queue()
        self.__callbackQueue.put(callback)
        self.itemsCache.onSyncCompleted += self.__onSyncCompleted

    def __unregisterHandler(self):
        self.__callbackQueue = None
        self.itemsCache.onSyncCompleted -= self.__onSyncCompleted
        return

    def __onSyncCompleted(self, *_):
        while not self.__callbackQueue.empty():
            self.__callbackQueue.get_nowait()(self.itemsCache.isSynced())

        self.__unregisterHandler()


class ServerRebootFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverReboot', ctx={'date': local_dt.strftime('%c')})
            return [_MessageData(formatted, self._getGuiSettings(message, 'serverReboot'))]
        else:
            return [_MessageData(None, None)]


class ServerRebootCancelledFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverRebootCancelled', ctx={'date': local_dt.strftime('%c')})
            return [_MessageData(formatted, self._getGuiSettings(message, 'serverRebootCancelled'))]
        else:
            return [_MessageData(None, None)]


class BattleResultsFormatter(WaitItemsSyncFormatter):
    __battleResultKeys = {-1: 'battleDefeatResult',
     0: 'battleDrawGameResult',
     1: 'battleVictoryResult'}
    __goldTemplateKey = 'battleResultGold'
    __questsTemplateKey = 'battleQuests'
    __i18n_penalty = '#%s:serviceChannelMessages/battleResults/penaltyForDamageAllies' % MESSENGER_I18N_FILE
    __i18n_contribution = '#%s:serviceChannelMessages/battleResults/contributionForDamageAllies' % MESSENGER_I18N_FILE
    __RANKED_STATES_WITH_NUMBER = ('rankEarned', 'rankLost')

    def isNotify(self):
        return True

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            battleResults = message.data
            arenaTypeID = battleResults.get('arenaTypeID', 0)
            if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
                arenaType = ArenaType.g_cache[arenaTypeID]
            else:
                arenaType = None
            arenaCreateTime = battleResults.get('arenaCreateTime', None)
            if arenaCreateTime and arenaType:
                ctx = {'arenaName': i18n.makeString(arenaType.name),
                 'vehicleNames': 'N/A',
                 'xp': '0',
                 Currency.CREDITS: '0'}
                vehicleNames = {intCD:self.itemsCache.items.getItemByCD(intCD) for intCD in battleResults.get('playerVehicles', {}).keys()}
                ctx['vehicleNames'] = ', '.join(map(operator.attrgetter('userName'), sorted(vehicleNames.values())))
                xp = battleResults.get('xp')
                if xp:
                    ctx['xp'] = BigWorld.wg_getIntegralFormat(xp)
                battleResKey = battleResults.get('isWinner', 0)
                ctx['xpEx'] = self.__makeXpExString(xp, battleResKey, battleResults.get('xpPenalty', 0), battleResults)
                ctx[Currency.GOLD] = self.__makeGoldString(battleResults.get(Currency.GOLD, 0))
                accCredits = battleResults.get(Currency.CREDITS) - battleResults.get('creditsToDraw', 0)
                if accCredits:
                    ctx[Currency.CREDITS] = self.__makeCurrencyString(Currency.CREDITS, accCredits)
                accCrystal = battleResults.get(Currency.CRYSTAL)
                ctx['crystalStr'] = ''
                if accCrystal:
                    ctx[Currency.CRYSTAL] = self.__makeCurrencyString(Currency.CRYSTAL, accCrystal)
                    ctx['crystalStr'] = g_settings.htmlTemplates.format('battleResultCrystal', {Currency.CRYSTAL: ctx[Currency.CRYSTAL]})
                ctx['creditsEx'] = self.__makeCreditsExString(accCredits, battleResults.get('creditsPenalty', 0), battleResults.get('creditsContributionIn', 0), battleResults.get('creditsContributionOut', 0))
                guiType = battleResults.get('guiType', 0)
                ctx['achieves'], ctx['badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
                ctx['lock'] = self.__makeVehicleLockString(vehicleNames, battleResults)
                ctx['quests'] = self.__makeQuestsAchieve(message)
                team = battleResults.get('team', 0)
                if guiType == ARENA_GUI_TYPE.FORT_BATTLE_2 or guiType == ARENA_GUI_TYPE.SORTIE_2:
                    if battleResKey == 0:
                        winnerIfDraw = battleResults.get('winnerIfDraw')
                        if winnerIfDraw:
                            battleResKey = 1 if winnerIfDraw == team else -1
                templateName = self.__battleResultKeys[battleResKey]
                bgIconSource = None
                arenaUniqueID = battleResults.get('arenaUniqueID', 0)
                formatted = g_settings.msgTemplates.format(templateName, ctx=ctx, data={'timestamp': arenaCreateTime,
                 'savedData': arenaUniqueID}, bgIconSource=bgIconSource)
                settings = self._getGuiSettings(message, templateName)
                settings.showAt = BigWorld.time()
                callback([_MessageData(formatted, settings)])
            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return

    def __makeQuestsAchieve(self, message):
        fmtMsg = TokenQuestsFormatter.formatQuestAchieves(message.data, asBattleFormatter=True)
        return g_settings.htmlTemplates.format('battleQuests', {'achieves': fmtMsg}) if fmtMsg is not None else ''

    def __makeVehicleLockString(self, vehicleNames, battleResults):
        locks = []
        for vehIntCD, battleResult in battleResults.get('playerVehicles', {}).iteritems():
            expireTime = battleResult.get('vehTypeUnlockTime', 0)
            if not expireTime:
                continue
            vehicleName = vehicleNames.get(vehIntCD)
            if vehicleName is None:
                continue
            locks.append(g_settings.htmlTemplates.format('battleResultLocks', ctx={'vehicleName': vehicleName,
             'expireTime': TimeFormatter.getLongDatetimeFormat(expireTime)}))

        return ', '.join(locks)

    def __makeXpExString(self, xp, battleResKey, xpPenalty, battleResults):
        if not xp:
            return ''
        exStrings = []
        if xpPenalty > 0:
            exStrings.append(i18n.makeString(self.__i18n_penalty, BigWorld.wg_getIntegralFormat(xpPenalty)))
        if battleResKey == 1:
            xpFactorStrings = []
            xpFactor = battleResults.get('dailyXPFactor', 1)
            if xpFactor > 1:
                xpFactorStrings.append(i18n.makeString('#%s:serviceChannelMessages/battleResults/doubleXpFactor' % MESSENGER_I18N_FILE) % xpFactor)
            if xpFactorStrings:
                exStrings.append(', '.join(xpFactorStrings))
        return ' ({0:s})'.format('; '.join(exStrings)) if exStrings else ''

    def __makeCreditsExString(self, accCredits, creditsPenalty, creditsContributionIn, creditsContributionOut):
        if not accCredits:
            return ''
        formatter = getBWFormatter(Currency.CREDITS)
        exStrings = []
        penalty = sum([creditsPenalty, creditsContributionOut])
        if penalty > 0:
            exStrings.append(i18n.makeString(self.__i18n_penalty, formatter(penalty)))
        if creditsContributionIn > 0:
            exStrings.append(i18n.makeString(self.__i18n_contribution, formatter(creditsContributionIn)))
        return ' ({0:s})'.format('; '.join(exStrings)) if exStrings else ''

    def __makeGoldString(self, gold):
        if not gold:
            return ''
        formatter = getBWFormatter(Currency.GOLD)
        return g_settings.htmlTemplates.format(self.__goldTemplateKey, {Currency.GOLD: formatter(gold)})

    def __makeCurrencyString(self, currency, credit):
        formatter = getBWFormatter(currency)
        return formatter(credit)

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
                if achieve is not None and not achieve.isApproachable() and achieve not in popUpRecords:
                    popUpRecords.append(achieve)

            if 'markOfMastery' in vehBattleResults and vehBattleResults['markOfMastery'] > 0:
                popUpRecords.append(getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, 'markOfMastery')).create(value=vehBattleResults['markOfMastery']))

        achievementsStrings = [ a.getUserName() for a in sorted(popUpRecords) ]
        raresStrings = _getRaresAchievementsStirngs(battleResults)
        if raresStrings:
            achievementsStrings.extend(raresStrings)
        if battleResults.get('guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankedController = dependency.instance(IRankedBattlesController)
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            stateChange = rankedController.getRankChangeStatus(rankInfo)
            winnerStr = 'win' if battleResults.get('isWinner', 0) > 0 else 'lose'
            if stateChange in self.__RANKED_STATES_WITH_NUMBER:
                if stateChange == self.__RANKED_STATES_WITH_NUMBER[0]:
                    rankID = rankInfo.accRank
                else:
                    rankID = rankInfo.prevAccRank
                stateChangeStr = i18n.makeString(MESSENGER.rankedStateChange(winnerStr, stateChange), rank=rankID)
            else:
                stateChangeStr = i18n.makeString(MESSENGER.rankedStateChange(winnerStr, stateChange))
            achievementsStrings.append(stateChangeStr)
            shieldsStr = MESSENGER.rankedShieldStateChange(rankInfo.shieldState)
            if shieldsStr is not None:
                achievementsStrings.append(i18n.makeString(shieldsStr))
        achievementsBlock = ''
        if achievementsStrings:
            achievementsBlock = g_settings.htmlTemplates.format('battleResultAchieves', {'achieves': ', '.join(achievementsStrings)})
        badgesBlock = ''
        if badges:
            badgesStr = ', '.join([ i18n.makeString(BADGE.badgeName(badgeID)) for badgeID in badges ])
            badgesBlock = '<br/>' + g_settings.htmlTemplates.format('badgeAchievement', {'badges': badgesStr})
        return (achievementsBlock, badgesBlock)


class AutoMaintenanceFormatter(ServiceChannelFormatter):
    __messages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairError',
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadError',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipError',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: '#messenger:serviceChannelMessages/autoEquipBoosterError',
                                                 AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleError'},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSuccess',
                                  AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSuccess',
                                  AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSuccess',
                                  AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: '#messenger:serviceChannelMessages/autoEquipBoosterSuccess',
                                  AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleSuccess'},
     AUTO_MAINTENANCE_RESULT.NOT_PERFORMED: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSkipped',
                                             AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSkipped',
                                             AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSkipped',
                                             AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: '#messenger:serviceChannelMessages/autoEquipBoosterSkipped',
                                             AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleSkipped'},
     AUTO_MAINTENANCE_RESULT.DISABLED_OPTION: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: '#messenger:serviceChannelMessages/autoEquipBoosterDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleDisabledOption'},
     AUTO_MAINTENANCE_RESULT.NO_WALLET_SESSION: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: '#messenger:serviceChannelMessages/autoBoosterErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleErrorNoWallet'},
     AUTO_MAINTENANCE_RESULT.RENT_IS_OVER: {AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleRentIsOver/text'},
     AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER: {AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: '#messenger:serviceChannelMessages/autoRentStyleRentIsAlmostOver/text'}}
    __currencyTemplates = {Currency.CREDITS: 'PurchaseForCreditsSysMessage',
     Currency.GOLD: 'PurchaseForGoldSysMessage',
     Currency.CRYSTAL: 'PurchaseForCrystalSysMessage'}

    def isNotify(self):
        return True

    def format(self, message, *args):
        vehicleCompDescr = message.data.get('vehTypeCD', None)
        styleId = message.data.get('styleID', None)
        result = message.data.get('result', None)
        typeID = message.data.get('typeID', None)
        cost = Money(*message.data.get('cost', ()))
        if vehicleCompDescr is not None and result is not None and typeID is not None:
            vehType = vehicles_core.getVehicleType(vehicleCompDescr)
            if typeID == AUTO_MAINTENANCE_TYPE.REPAIR:
                formatMsgType = 'RepairSysMessage'
            else:
                formatMsgType = self._getTemplateByCurrency(cost.getCurrency(byWeight=False))
            msgTmpl = i18n.makeString(self.__messages[result].get(typeID, None))
            if not msgTmpl:
                LOG_WARNING('Invalid typeID field in message: ', message)
                return [_MessageData(None, None)]
            msg = ''
            data = None
            if result in (AUTO_MAINTENANCE_RESULT.RENT_IS_OVER, AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER):
                cc = vehicles_core.g_cache.customization20()
                style = cc.styles.get(styleId, None)
                if style:
                    styleName = style.userString
                    vehName = getShortUserName(vehType)
                    msg = msgTmpl % (styleName, vehName)
                    data = {'savedData': {'styleIntCD': style.compactDescr,
                                   'vehicleIntCD': vehicleCompDescr}}
            else:
                vehName = getUserName(vehType)
                msg = msgTmpl % vehName
            priorityLevel = NotificationPriorityLevel.MEDIUM
            if result == AUTO_MAINTENANCE_RESULT.OK:
                priorityLevel = NotificationPriorityLevel.LOW
                templateName = formatMsgType
            elif result == AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS:
                templateName = 'ErrorSysMessage'
            elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_OVER:
                templateName = 'RentOfStyleIsExpiredSysMessage'
            elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER:
                templateName = 'RentOfStyleIsAlmostExpiredSysMessage'
            else:
                templateName = 'WarningSysMessage'
            if result == AUTO_MAINTENANCE_RESULT.OK:
                msg += shared_fmts.formatPrice(cost.toAbs())
            formatted = g_settings.msgTemplates.format(templateName, {'text': msg}, data=data)
            return [_MessageData(formatted, self._getGuiSettings(message, priorityLevel=priorityLevel, messageType=result))]
        else:
            return [_MessageData(None, None)]
            return

    def _getTemplateByCurrency(self, currency):
        return self.__currencyTemplates.get(currency, 'PurchaseForCreditsSysMessage')


class AchievementFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def isAsync(self):
        return True

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        achievesList, badgesList = [], []
        achieves = message.data.get('popUpRecords')
        if achieves is not None:
            for (block, name), value in achieves.iteritems():
                if block == BADGES_BLOCK:
                    badgesList.append(i18n.makeString(BADGE.badgeName(name)))
                achieve = getAchievementFactory((block, name)).create(value)
                if achieve is not None:
                    achievesList.append(achieve.getUserName())
                achievesList.append(i18n.makeString('#achievements:{0:s}'.format(name)))

        rares = [ rareID for rareID in message.data.get('rareAchievements', []) if rareID > 0 ]
        raresList = _processRareAchievements(rares)
        achievesList.extend(raresList)
        if not achievesList:
            callback([_MessageData(None, None)])
            return
        else:
            formatted = g_settings.msgTemplates.format('achievementReceived', {'achieves': ', '.join(achievesList)})
            if badgesList:
                badgesBlock = g_settings.htmlTemplates.format('badgeAchievement', {'badges': ', '.join(badgesList)})
                formatted = _EOL.join([formatted, badgesBlock])
            callback([_MessageData(formatted, self._getGuiSettings(message, 'achievementReceived'))])
            return


class CurrencyUpdateFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        currencyCode = data['currency_code']
        amountDelta = data['amount_delta']
        transactionTime = data['date']
        if currencyCode and amountDelta and transactionTime:
            ms = i18n.makeString
            xmlKey = 'currencyUpdate'
            formatted = g_settings.msgTemplates.format(xmlKey, ctx={'date': TimeFormatter.getLongDatetimeFormat(transactionTime),
             'currency': ms(MESSENGER.currencyUpdateSelect(operationName='debited' if amountDelta < 0 else 'received', currencyCode=currencyCode)),
             'amount': getStyle(currencyCode)(getBWFormatter(currencyCode)(abs(amountDelta)))}, data={'icon': currencyCode.title() + 'Icon'})
            return [_MessageData(formatted, self._getGuiSettings(message, xmlKey))]
        else:
            return [_MessageData(None, None)]


class GiftReceivedFormatter(ServiceChannelFormatter):
    __handlers = {'money': ('_GiftReceivedFormatter__formatMoneyGiftMsg', {1: 'creditsReceivedAsGift',
                2: 'goldReceivedAsGift',
                3: 'creditsAndGoldReceivedAsGift'}),
     'xp': ('_GiftReceivedFormatter__formatXPGiftMsg', 'xpReceivedAsGift'),
     'premium': ('_GiftReceivedFormatter__formatPremiumGiftMsg', 'premiumReceivedAsGift'),
     'item': ('_GiftReceivedFormatter__formatItemGiftMsg', 'itemReceivedAsGift'),
     'vehicle': ('_GiftReceivedFormatter__formatVehicleGiftMsg', 'vehicleReceivedAsGift')}

    def format(self, message, *args):
        data = message.data
        giftType = data.get('type')
        if giftType is not None:
            handlerName, templateKey = self.__handlers.get(giftType, (None, None))
            if handlerName is not None:
                formatted, templateKey = getattr(self, handlerName)(templateKey, data)
                return [_MessageData(formatted, self._getGuiSettings(message, templateKey))]
        return [_MessageData(None, None)]

    def __formatMoneyGiftMsg(self, keys, data):
        result = (None, '')
        ctx = {}
        idx = 0
        for i, currency in enumerate(Currency.ALL):
            value = data.get(currency, 0)
            if value > 0:
                formatter = getBWFormatter(currency)
                idx |= 1 << i
                ctx[currency] = formatter(value)

        if idx in keys:
            key = keys[idx]
            result = (g_settings.msgTemplates.format(keys[idx], ctx), key)
        return result

    def __formatXPGiftMsg(self, key, data):
        xp = data.get('amount', 0)
        result = None
        if xp > 0:
            result = g_settings.msgTemplates.format(key, ctx={'freeXP': BigWorld.wg_getIntegralFormat(xp)})
        return (result, key)

    def __formatPremiumGiftMsg(self, key, data):
        days = data.get('amount', 0)
        result = None
        if days > 0:
            result = g_settings.msgTemplates.format(key, ctx={'days': days})
        return (result, key)

    def __formatItemGiftMsg(self, key, data):
        amount = data.get('amount', 0)
        result = None
        itemTypeIdx = data.get('itemTypeIdx')
        itemCompactDesc = data.get('itemCD')
        if amount > 0 and itemTypeIdx is not None and itemCompactDesc is not None:
            result = g_settings.msgTemplates.format(key, ctx={'typeName': getTypeInfoByIndex(itemTypeIdx)['userString'],
             'itemName': vehicles_core.getItemByCompactDescr(itemCompactDesc).i18n.userString,
             'amount': amount})
        return (result, key)

    def __formatVehicleGiftMsg(self, key, data):
        vCompDesc = data.get('typeCD', None)
        result = None
        if vCompDesc is not None:
            result = g_settings.msgTemplates.format(key, ctx={'vehicleName': getUserName(vehicles_core.getVehicleType(vCompDesc))})
        return (result, key)


class InvoiceReceivedFormatter(WaitItemsSyncFormatter):
    __assetHandlers = {INVOICE_ASSET.GOLD: '_formatAmount',
     INVOICE_ASSET.CREDITS: '_formatAmount',
     INVOICE_ASSET.CRYSTAL: '_formatAmount',
     INVOICE_ASSET.PREMIUM: '_formatAmount',
     INVOICE_ASSET.FREE_XP: '_formatAmount',
     INVOICE_ASSET.DATA: '_formatData'}
    __currencyToInvoiceAsset = {Currency.GOLD: INVOICE_ASSET.GOLD,
     Currency.CREDITS: INVOICE_ASSET.CREDITS,
     Currency.CRYSTAL: INVOICE_ASSET.CRYSTAL}
    __operationTemplateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: 'crystalAccruedInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpAccruedInvoiceReceived',
     INVOICE_ASSET.GOLD | 16: 'goldDebitedInvoiceReceived',
     INVOICE_ASSET.CREDITS | 16: 'creditsDebitedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL | 16: 'crystalDebitedInvoiceReceived',
     INVOICE_ASSET.PREMIUM | 16: 'premiumDebitedInvoiceReceived',
     INVOICE_ASSET.FREE_XP | 16: 'freeXpDebitedInvoiceReceived'}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: 'goldInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: 'crystalInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: 'dataInvoiceReceived'}
    __i18nPiecesString = '#{0:s}:serviceChannelMessages/invoiceReceived/pieces'.format(MESSENGER_I18N_FILE)
    __i18nCrewString = '#{0:s}:serviceChannelMessages/invoiceReceived/crewOnVehicle'.format(MESSENGER_I18N_FILE)
    __i18nCrewWithLvlDroppedString = '#{0:s}:serviceChannelMessages/invoiceReceived/crewWithLvlDroppedToBarracks'.format(MESSENGER_I18N_FILE)
    __i18nCrewDroppedString = '#{0:s}:serviceChannelMessages/invoiceReceived/crewDroppedToBarracks'.format(MESSENGER_I18N_FILE)
    __i18nCrewWithdrawnString = '#{0:s}:serviceChannelMessages/invoiceReceived/crewWithdrawn'.format(MESSENGER_I18N_FILE)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data
            self.__prerocessRareAchievements(data)
            assetType = data.get('assetType', -1)
            handler = self.__assetHandlers.get(assetType)
            if handler is not None:
                formatted = getattr(self, handler)(assetType, data)
            if formatted is not None:
                settings = self._getGuiSettings(message, self._getMessageTemplateKey(assetType))
        callback([_MessageData(formatted, settings)])
        return

    def _getMessageTemplateKey(self, assetType):
        return self.__messageTemplateKeys[assetType]

    def _getOperationTimeString(self, data):
        operationTime = data.get('at', None)
        if operationTime:
            fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
        else:
            fDatetime = 'N/A'
        return fDatetime

    @classmethod
    def _getVehicleNames(cls, vehicles):
        addVehNames = []
        removeVehNames = []
        rentedVehNames = []
        for vehCompDescr, vehData in vehicles.iteritems():
            if 'customCompensation' in vehData:
                continue
            isNegative = False
            if isinstance(vehCompDescr, types.IntType):
                isNegative = vehCompDescr < 0
            isRented = 'rent' in vehData
            vehicleName = cls.__getVehicleName(vehCompDescr)
            if vehicleName is None:
                continue
            vehicleInfo = cls.__getVehicleInfo(vehData, isNegative)
            vehicleInfoString = ' ({0:s})'.format(vehicleInfo) if vehicleInfo else ''
            vehUserString = '{0:s}{1:s}'.format(vehicleName, vehicleInfoString)
            if isNegative:
                removeVehNames.append(vehUserString)
            if isRented:
                rentedVehNames.append(vehUserString)
            addVehNames.append(vehUserString)

        return (addVehNames, removeVehNames, rentedVehNames)

    @classmethod
    def getVehiclesString(cls, vehicles, htmlTplPostfix='InvoiceReceived'):
        addVehNames, removeVehNames, rentedVehNames = cls._getVehicleNames(vehicles)
        result = []
        if addVehNames:
            result.append(g_settings.htmlTemplates.format('vehiclesAccrued' + htmlTplPostfix, ctx={'vehicles': ', '.join(addVehNames)}))
        if removeVehNames:
            result.append(g_settings.htmlTemplates.format('vehiclesDebited' + htmlTplPostfix, ctx={'vehicles': ', '.join(removeVehNames)}))
        if rentedVehNames:
            result.append(g_settings.htmlTemplates.format('vehiclesRented' + htmlTplPostfix, ctx={'vehicles': ', '.join(rentedVehNames)}))
        return '<br/>'.join(result)

    @classmethod
    def _getCompensationString(cls, compensationMoney, strItemNames, htmlTplPostfix):
        htmlTemplates = g_settings.htmlTemplates
        values = []
        result = ''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            formatter = getBWFormatter(currency)
            key = '{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={'amount': formatter(compensationMoney.get(currency))}))

        if values:
            result = htmlTemplates.format('compensationFor' + htmlTplPostfix, ctx={'items': ', '.join(strItemNames),
             'compensation': ', '.join(values)})
        return result

    @classmethod
    def _getCustomizationCompensationString(cls, compensationMoney, strItemType, strItemName, amount, htmlTplPostfix):
        htmlTemplates = g_settings.htmlTemplates
        values = []
        result = ''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            formatter = getBWFormatter(currency)
            key = '{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={'amount': formatter(compensationMoney.get(currency))}))

        if values:
            result = htmlTemplates.format('customizationCompensation' + htmlTplPostfix, ctx={'type': strItemType,
             'name': strItemName,
             'amount': str(amount),
             'compensation': ', '.join(values)})
        return result

    @classmethod
    def getVehiclesCompensationString(cls, vehicles, htmlTplPostfix='InvoiceReceived'):
        htmlTemplates = g_settings.htmlTemplates
        result = []
        for vehCompDescr, vehData in vehicles.iteritems():
            vehicleName = cls.__getVehicleName(vehCompDescr)
            if vehicleName is None:
                continue
            if 'rentCompensation' in vehData:
                comp = Money.makeFromMoneyTuple(vehData['rentCompensation'])
                currency = comp.getCurrency(byWeight=True)
                formatter = getBWFormatter(currency)
                key = '{}RentCompensationReceived'.format(currency)
                ctx = {currency: formatter(comp.get(currency)),
                 'vehicleName': vehicleName}
                result.append(htmlTemplates.format(key, ctx=ctx))
            if 'customCompensation' in vehData:
                itemNames = (vehicleName,)
                comp = Money.makeFromMoneyTuple(vehData['customCompensation'])
                result.append(cls._getCompensationString(comp, itemNames, htmlTplPostfix))

        return '<br/>'.join(result)

    @classmethod
    def getCustomizationCompensationString(cls, customizationItem, htmlTplPostfix='InvoiceReceived'):
        result = ''
        if 'customCompensation' not in customizationItem:
            return result
        customItemData = _getCustomizationItemData(customizationItem['id'], customizationItem['custType'])
        strItemType = i18n.makeString('#messenger:serviceChannelMessages/invoiceReceived/compensation/{}'.format(customItemData.guiItemType))
        comp = Money.makeFromMoneyTuple(customizationItem['customCompensation'])
        result = cls._getCustomizationCompensationString(comp, strItemType, customItemData.userName, customizationItem['compensatedNumber'], htmlTplPostfix)
        return result

    @classmethod
    def getTankmenString(cls, tmen):
        tmanUserStrings = []
        for tmanData in tmen:
            try:
                if isinstance(tmanData, dict):
                    tankman = Tankman(tmanData['tmanCompDescr'])
                else:
                    tankman = Tankman(tmanData)
                tmanUserStrings.append('{0:s} {1:s} ({2:s}, {3:s}, {4:d}%)'.format(tankman.rankUserName, tankman.lastUserName, tankman.roleUserName, getUserName(tankman.vehicleNativeDescr.type), tankman.roleLevel))
            except Exception:
                LOG_ERROR('Wrong tankman data', tmanData)
                LOG_CURRENT_EXCEPTION()

        result = ''
        if tmanUserStrings:
            result = g_settings.htmlTemplates.format('tankmenInvoiceReceived', ctx={'tankman': ', '.join(tmanUserStrings)})
        return result

    @classmethod
    def getGoodiesString(cls, goodies):
        result = []
        boostersStrings = []
        discountsStrings = []
        for goodieID, ginfo in goodies.iteritems():
            if goodieID in cls.itemsCache.items.shop.boosters:
                booster = cls.goodiesCache.getBooster(goodieID)
                if booster is not None and booster.enabled:
                    if ginfo.get('count'):
                        boostersStrings.append(i18n.makeString(SYSTEM_MESSAGES.BONUSES_BOOSTER_VALUE, name=booster.userName, count=ginfo.get('count')))
                    else:
                        boostersStrings.append(booster.userName)
            discount = cls.goodiesCache.getDiscount(goodieID)
            if discount is not None and discount.enabled:
                discountsStrings.append(discount.description)

        if boostersStrings:
            result.append(g_settings.htmlTemplates.format('boostersInvoiceReceived', ctx={'boosters': ', '.join(boostersStrings)}))
        if discountsStrings:
            result.append(g_settings.htmlTemplates.format('discountsInvoiceReceived', ctx={'discounts': ', '.join(discountsStrings)}))
        return '; '.join(result)

    @classmethod
    def _processCompensations(cls, data):
        vehicles = data.get('vehicles')
        comp = MONEY_UNDEFINED
        if vehicles is not None:
            for value in vehicles.itervalues():
                if 'rentCompensation' in value:
                    comp += Money.makeFromMoneyTuple(value['rentCompensation'])
                if 'customCompensation' in value:
                    comp += Money.makeFromMoneyTuple(value['customCompensation'])

        for currency in cls.__currencyToInvoiceAsset:
            if currency in data and comp.isSet(currency):
                data[currency] -= comp.get(currency)
                if data[currency] == 0:
                    del data[currency]

        return

    def _formatAmount(self, assetType, data):
        amount = data.get('amount', None)
        return None if amount is None else g_settings.msgTemplates.format(self._getMessageTemplateKey(assetType), ctx={'at': self._getOperationTimeString(data),
         'desc': self.__getL10nDescription(data),
         'op': self.__getFinOperationString(assetType, amount)})

    def _composeOperations(self, data):
        dataEx = data.get('data', {})
        if not dataEx:
            return
        else:
            operations = []
            self._processCompensations(dataEx)
            for currency, invAsset in self.__currencyToInvoiceAsset.iteritems():
                if currency in dataEx:
                    operations.append(self.__getFinOperationString(invAsset, dataEx[currency], formatter=getBWFormatter(currency)))

            freeXp = dataEx.get('freeXP')
            if freeXp is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.FREE_XP, freeXp))
            premium = dataEx.get('premium')
            if premium is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.PREMIUM, premium))
            items = dataEx.get('items', {})
            if items:
                operations.append(self.__getItemsString(items))
            tmen = dataEx.get('tankmen', [])
            vehicles = dataEx.get('vehicles', {})
            vehicleItems = {}
            if vehicles:
                result = self.getVehiclesString(vehicles)
                if result:
                    operations.append(result)
                comptnStr = self.getVehiclesCompensationString(vehicles)
                if comptnStr:
                    operations.append(comptnStr)
                for v in vehicles.itervalues():
                    tmen.extend(v.get('tankmen', []))
                    items = v.get('items', {})
                    for intCD, count in items.iteritems():
                        if intCD in vehicleItems:
                            vehicleItems[intCD] += count
                        vehicleItems[intCD] = count

            if vehicleItems:
                operations.append(self.__getItemsString(vehicleItems, installed=True))
            if tmen:
                operations.append(self.getTankmenString(tmen))
            slots = dataEx.get('slots')
            if slots:
                operations.append(self.__getSlotsString(slots))
            berths = dataEx.get('berths')
            if berths:
                operations.append(self.__getBerthsString(berths))
            goodies = dataEx.get('goodies', {})
            if goodies:
                strGoodies = self.getGoodiesString(goodies)
                if strGoodies:
                    operations.append(strGoodies)
            dossier = dataEx.get('dossier', {})
            if dossier:
                operations.append(self.__getDossierString())
            _extendCustomizationData(dataEx, operations, htmlTplPostfix='InvoiceReceived')
            tankmenFreeXP = dataEx.get('tankmenFreeXP', {})
            if tankmenFreeXP:
                operations.append(self.__getTankmenFreeXPString(tankmenFreeXP))
            tokensStr = self.__getTokensString(dataEx.get('tokens', {}))
            if tokensStr:
                operations.append(tokensStr)
            return operations

    def _formatData(self, assetType, data):
        operations = self._composeOperations(data)
        compensation = Money()
        for customizationData in data['data'].get('customizations', ()):
            compensation += Money.makeFromMoneyTuple(customizationData.get('customCompensation', (0, 0)))

        if compensation.gold > 0:
            icon = 'goldIcon'
        elif compensation.credits > 0:
            icon = 'creditsIcon'
        else:
            icon = 'informationIcon'
        return None if not operations else g_settings.msgTemplates.format(self._getMessageTemplateKey(assetType), ctx={'at': self._getOperationTimeString(data),
         'desc': self.__getL10nDescription(data),
         'op': '<br/>'.join(operations)}, data={'icon': icon})

    def __getSlotsString(self, slots):
        if slots > 0:
            template = 'slotsAccruedInvoiceReceived'
        else:
            template = 'slotsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': BigWorld.wg_getIntegralFormat(abs(slots))})

    @classmethod
    def __getBerthsString(cls, berths):
        if berths > 0:
            template = 'berthsAccruedInvoiceReceived'
        else:
            template = 'berthsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': BigWorld.wg_getIntegralFormat(abs(berths))})

    def __prerocessRareAchievements(self, data):
        dossiers = data.get('data', {}).get('dossier', {})
        if dossiers:
            self.__dossierResult = []
            rares = [ rec['value'] for d in dossiers.itervalues() for (blck, _), rec in d.iteritems() if blck == ACHIEVEMENT_BLOCK.RARE ]
            ms = i18n.makeString
            addDossierStrings, addBadgesStrings, removedBadgesStrings = [], [], []
            for rec in dossiers.itervalues():
                for (block, name), recData in rec.iteritems():
                    if name != '':
                        if block == BADGES_BLOCK:
                            if recData['value'] < 0:
                                removedBadgesStrings.append(ms(BADGE.badgeName(name)))
                            else:
                                addBadgesStrings.append(ms(BADGE.badgeName(name)))
                        elif block != ACHIEVEMENT_BLOCK.RARE:
                            achieve = getAchievementFactory((block, name)).create(recData['actualValue'])
                            if achieve is not None:
                                addDossierStrings.append(achieve.getUserName())
                            else:
                                addDossierStrings.append(ms('#achievements:{0:s}'.format(name)))

            addDossiers = [ rare for rare in rares if rare > 0 ]
            if addDossiers:
                addDossierStrings += _processRareAchievements(addDossiers)
            if addDossierStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersAccruedInvoiceReceived', ctx={'dossiers': ', '.join(addDossierStrings)}))
            delDossiers = [ abs(rare) for rare in rares if rare < 0 ]
            if delDossiers:
                delDossierStrings = _processRareAchievements(delDossiers)
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersDebitedInvoiceReceived', ctx={'dossiers': ', '.join(delDossierStrings)}))
            if addBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('badgeAchievement', ctx={'badges': ', '.join(addBadgesStrings)}))
            if removedBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('removedBadgeAchievement', ctx={'badges': ', '.join(removedBadgesStrings)}))
        return

    def __getDossierString(self):
        return '<br/>'.join(self.__dossierResult)

    def __getTankmenFreeXPString(self, data):
        freeXP = set()
        spec = []
        for tankmenDescr, xp in data.iteritems():
            freeXP.add(xp)
            tankman = Tankman(tankmenDescr)
            spec.append('{} {} {}'.format(tankman.fullUserName, tankman.roleUserName, getShortUserName(tankman.vehicleNativeDescr.type)))

        specStr = ' ({})'.format(', '.join(spec)) if spec else ''
        freeXP = freeXP.pop()
        if freeXP > 0:
            template = 'tankmenFreeXpAccruedInvoiceReceived'
        else:
            template = 'tankmenFreeXpDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'tankmenFreeXp': BigWorld.wg_getIntegralFormat(abs(freeXP)),
         'spec': specStr})

    def __getL10nDescription(self, data):
        descr = ''
        lData = getLocalizedData(data.get('data', {}), 'localized_description', defVal=None)
        if lData:
            descr = i18n.encodeUtf8(html.escape(lData.get('description', u'')))
            if descr:
                descr = '<br/>' + descr
        return descr

    def __getFinOperationString(self, assetType, amount, formatter=None):
        templateKey = 0 if amount > 0 else 16
        templateKey |= assetType
        ctx = {}
        if formatter is not None:
            ctx['amount'] = formatter(abs(amount))
        else:
            ctx['amount'] = BigWorld.wg_getIntegralFormat(abs(amount))
        return g_settings.htmlTemplates.format(self.__operationTemplateKeys[templateKey], ctx=ctx)

    def __getItemsString(self, items, installed=False):
        accrued = []
        debited = []
        for itemCompactDescr, count in items.iteritems():
            if count:
                try:
                    item = vehicles_core.getItemByCompactDescr(itemCompactDescr)
                    itemString = '{0:s} "{1:s}" - {2:d} {3:s}'.format(getTypeInfoByName(item.itemTypeName)['userString'], item.i18n.userString, abs(count), i18n.makeString(self.__i18nPiecesString))
                    if count > 0:
                        accrued.append(itemString)
                    else:
                        debited.append(itemString)
                except Exception:
                    LOG_ERROR('itemCompactDescr can not parse ', itemCompactDescr)
                    LOG_CURRENT_EXCEPTION()

        result = ''
        if accrued:
            if installed:
                templateId = 'itemsInstalledInvoiceReceived'
            else:
                templateId = 'itemsAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={'items': ', '.join(accrued)})
        if debited:
            if result:
                result += '<br/>'
            result += g_settings.htmlTemplates.format('itemsDebitedInvoiceReceived', ctx={'items': ', '.join(debited)})
        return result

    @classmethod
    def __getVehicleInfo(cls, vehData, isWithdrawn):
        vInfo = []
        if isWithdrawn:
            toBarracks = not vehData.get('dismissCrew', False)
            action = cls.__i18nCrewDroppedString if toBarracks else cls.__i18nCrewWithdrawnString
            vInfo.append(i18n.makeString(action))
        else:
            if 'rent' in vehData:
                rentData = vehData['rent']
                rentLeftCount = 0
                rentTypeName = None
                for rentType in _RENT_TYPES:
                    rentTypeValue = rentData.get(rentType, 0)
                    if rentTypeValue > 0 and rentTypeValue != float('inf'):
                        rentTypeName = _RENT_TYPES[rentType]
                        rentLeftCount = int(rentTypeValue)
                        break

                if rentTypeName is not None and rentLeftCount > 0:
                    rentLeftStr = i18n.makeString(TOOLTIPS.getRentLeftTypeLabel(rentTypeName), count=rentLeftCount)
                    vInfo.append(rentLeftStr)
            crewLevel = VehiclesBonus.getTmanRoleLevel(vehData)
            if crewLevel is not None and crewLevel > DEFAULT_CREW_LVL:
                if 'crewInBarracks' in vehData and vehData['crewInBarracks']:
                    crewWithLevelString = i18n.makeString(cls.__i18nCrewWithLvlDroppedString, crewLevel)
                else:
                    crewWithLevelString = i18n.makeString(cls.__i18nCrewString, crewLevel)
                vInfo.append(crewWithLevelString)
        return '; '.join(vInfo)

    @classmethod
    def __getVehicleName(cls, vehCompDescr):
        vehicleName = None
        try:
            if vehCompDescr < 0:
                vehCompDescr = abs(vehCompDescr)
            vehicleName = getUserName(vehicles_core.getVehicleType(vehCompDescr))
        except Exception:
            LOG_ERROR('Wrong vehicle compact descriptor', vehCompDescr)
            LOG_CURRENT_EXCEPTION()

        return vehicleName

    @staticmethod
    def __getTokensString(data):
        count = 0
        for tokenName, tokenData in data.iteritems():
            if tokenName == constants.PERSONAL_MISSION_FREE_TOKEN_NAME:
                count += tokenData.get('count', 0)

        if count != 0:
            template = 'awardListAccruedInvoiceReceived' if count > 0 else 'awardListDebitedInvoiceReceived'
            return g_settings.htmlTemplates.format(template, {'count': count})


class AdminMessageFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = decompressSysMessage(message.data)
        if data:
            dataType = type(data)
            text = ''
            if dataType in types.StringTypes:
                text = data
            elif dataType is types.DictType:
                text = getLocalizedData({'value': data}, 'value')
            if not text:
                LOG_ERROR('Text of message not found', message)
                return (None, None)
            formatted = g_settings.msgTemplates.format('adminMessage', {'text': text})
            return [_MessageData(formatted, self._getGuiSettings(message, 'adminMessage'))]
        else:
            return [_MessageData(None, None)]
            return None


class AccountTypeChangedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        result = [_MessageData(None, None)]
        if isPremium is not None:
            accountTypeName = i18n.makeString('#menu:accountTypes/premium') if isPremium else i18n.makeString('#menu:accountTypes/base')
            expiryDatetime = TimeFormatter.getLongDatetimeFormat(expiryTime) if expiryTime else None
            if expiryDatetime:
                templateKey = 'accountTypeChangedWithExpiration'
                ctx = {'accType': accountTypeName,
                 'expiryTime': expiryDatetime}
            else:
                templateKey = 'accountTypeChanged'
                ctx = {'accType': accountTypeName}
            formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
            result = [_MessageData(formatted, self._getGuiSettings(message, templateKey))]
        return result


class PremiumActionFormatter(ServiceChannelFormatter):
    _templateKey = None

    def _getMessage(self, isPremium, expiryTime):
        return None

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        return [_MessageData(self._getMessage(isPremium, expiryTime), self._getGuiSettings(message, self._templateKey))] if isPremium is not None else [_MessageData(None, None)]


class PremiumBoughtFormatter(PremiumActionFormatter):
    _templateKey = 'premiumBought'

    def _getMessage(self, isPremium, expiryTime):
        result = None
        if isPremium is True and expiryTime > 0:
            result = g_settings.msgTemplates.format(self._templateKey, ctx={'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))})
        return result


class PremiumExtendedFormatter(PremiumBoughtFormatter):
    _templateKey = 'premiumExtended'


class PremiumExpiredFormatter(PremiumActionFormatter):
    _templateKey = 'premiumExpired'

    def _getMessage(self, isPremium, expiryTime):
        result = None
        if isPremium is False:
            result = g_settings.msgTemplates.format(self._templateKey)
        return result


class PrebattleFormatter(ServiceChannelFormatter):
    __battleTypeByPrebattleType = {PREBATTLE_TYPE.TOURNAMENT: 'tournament',
     PREBATTLE_TYPE.CLAN: 'clan'}
    _battleFinishReasonKeys = {}
    _defaultBattleFinishReasonKey = ('base', True)

    def isNotify(self):
        return True

    def _getIconId(self, prbType):
        iconId = 'BattleResultIcon'
        if prbType == PREBATTLE_TYPE.CLAN:
            iconId = 'ClanBattleResultIcon'
        elif prbType == PREBATTLE_TYPE.TOURNAMENT:
            iconId = 'TournamentBattleResultIcon'
        return iconId

    def _makeBattleTypeString(self, prbType):
        typeString = self.__battleTypeByPrebattleType.get(prbType, 'prebattle')
        key = '#{0:s}:serviceChannelMessages/prebattle/battleType/{1:s}'.format(MESSENGER_I18N_FILE, typeString)
        return i18n.makeString(key)

    def _makeDescriptionString(self, data, showBattlesCount=True):
        if 'localized_data' in data and data['localized_data']:
            description = getPrebattleFullDescription(data, escapeHtml=True)
        else:
            prbType = data.get('type')
            description = self._makeBattleTypeString(prbType)
        battlesLimit = data.get('battlesLimit', 0)
        if showBattlesCount and battlesLimit > 1:
            battlesCount = data.get('battlesCount')
            if battlesCount > 0:
                key = '#{0:s}:serviceChannelMessages/prebattle/numberOfBattle'.format(MESSENGER_I18N_FILE)
                numberOfBattleString = i18n.makeString(key, battlesCount)
                description = '{0:s} {1:s}'.format(description, numberOfBattleString)
            else:
                LOG_WARNING('Invalid value of battlesCount ', battlesCount)
        return description

    def _getOpponentsString(self, opponents):
        firstOp = i18n.encodeUtf8(opponents.get('1', {}).get('name', ''))
        secondOp = i18n.encodeUtf8(opponents.get('2', {}).get('name', ''))
        result = ''
        if firstOp and secondOp:
            result = g_settings.htmlTemplates.format('prebattleOpponents', ctx={'first': html.escape(firstOp),
             'second': html.escape(secondOp)})
        return result

    def _getBattleResultString(self, winner, team):
        result = 'undefined'
        if 3 > winner > -1 and team in (1, 2):
            if not winner:
                result = 'draftGame'
            else:
                result = 'defeat' if team != winner else 'win'
        return result

    def _makeBattleResultString(self, finishReason, winner, team):
        finishString, showResult = self._battleFinishReasonKeys.get(finishReason, self._defaultBattleFinishReasonKey)
        if showResult:
            resultString = self._getBattleResultString(winner, team)
            key = '#{0:s}:serviceChannelMessages/prebattle/finish/{1:s}/{2:s}'.format(MESSENGER_I18N_FILE, finishString, resultString)
        else:
            key = '#{0:s}:serviceChannelMessages/prebattle/finish/{1:s}'.format(MESSENGER_I18N_FILE, finishString)
        return i18n.makeString(key)


class PrebattleArenaFinishFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {FINISH_REASON.TECHNICAL: ('technical', True),
     FINISH_REASON.FAILURE: ('failure', False),
     FINISH_REASON.UNKNOWN: ('failure', False)}

    def format(self, message, *args):
        LOG_DEBUG('prbArenaFinish', message)
        data = message.data
        prbType = data.get('type')
        winner = data.get('winner')
        team = data.get('team')
        wins = data.get('wins')
        finishReason = data.get('finishReason')
        if None in [prbType,
         winner,
         team,
         wins,
         finishReason]:
            return []
        else:
            battleResult = self._makeBattleResultString(finishReason, winner, team)
            subtotal = ''
            battlesLimit = data.get('battlesLimit', 0)
            if battlesLimit > 1:
                battlesCount = data.get('battlesCount', -1)
                winsLimit = data.get('winsLimit', -1)
                if battlesCount == battlesLimit or winsLimit == wins[1] or winsLimit == wins[2]:
                    playerTeamWins = wins[team]
                    otherTeamWins = wins[2 if team == 1 else 1]
                    if winsLimit > 0 and playerTeamWins < winsLimit and otherTeamWins < winsLimit:
                        winner = None
                    elif playerTeamWins == otherTeamWins:
                        winner = 0
                    else:
                        winner = 1 if wins[1] > wins[2] else 2
                    sessionResult = self._makeBattleResultString(-1, winner, team)
                    subtotal = g_settings.htmlTemplates.format('prebattleTotal', ctx={'result': sessionResult,
                     'first': wins[1],
                     'second': wins[2]})
                else:
                    subtotal = g_settings.htmlTemplates.format('prebattleSubtotal', ctx={'first': wins[1],
                     'second': wins[2]})
            formatted = g_settings.msgTemplates.format('prebattleArenaFinish', ctx={'desc': self._makeDescriptionString(data),
             'opponents': self._getOpponentsString(data.get('opponents', {})),
             'result': battleResult,
             'subtotal': subtotal}, data={'timestamp': _getTimeStamp(message),
             'icon': self._getIconId(prbType)})
            return [_MessageData(formatted, self._getGuiSettings(message, 'prebattleArenaFinish'))]


class PrebattleKickFormatter(PrebattleFormatter):

    def format(self, message, *args):
        data = message.data
        result = []
        prbType = data.get('type')
        kickReason = data.get('kickReason')
        if prbType > 0 and kickReason > 0:
            ctx = {}
            key = '#system_messages:prebattle/kick/type/unknown'
            if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
                key = '#system_messages:prebattle/kick/type/squad'
            ctx['type'] = i18n.makeString(key)
            kickName = KICK_REASON_NAMES[kickReason]
            key = '#system_messages:prebattle/kick/reason/{0:s}'.format(kickName)
            ctx['reason'] = i18n.makeString(key)
            formatted = g_settings.msgTemplates.format('prebattleKick', ctx=ctx)
            result = [_MessageData(formatted, self._getGuiSettings(message, 'prebattleKick'))]
        return result


class PrebattleDestructionFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {KICK_REASON.ARENA_CREATION_FAILURE: ('failure', False),
     KICK_REASON.AVATAR_CREATION_FAILURE: ('failure', False),
     KICK_REASON.VEHICLE_CREATION_FAILURE: ('failure', False),
     KICK_REASON.PREBATTLE_CREATION_FAILURE: ('failure', False),
     KICK_REASON.BASEAPP_CRASH: ('failure', False),
     KICK_REASON.CELLAPP_CRASH: ('failure', False),
     KICK_REASON.UNKNOWN_FAILURE: ('failure', False),
     KICK_REASON.CREATOR_LEFT: ('creatorLeft', False),
     KICK_REASON.PLAYERKICK: ('playerKick', False),
     KICK_REASON.TIMEOUT: ('timeout', False)}

    def format(self, message, *args):
        LOG_DEBUG('prbDestruction', message)
        data = message.data
        prbType = data.get('type')
        team = data.get('team')
        wins = data.get('wins')
        kickReason = data.get('kickReason')
        if None in [prbType,
         team,
         wins,
         kickReason]:
            return []
        else:
            playerTeamWins = wins[team]
            otherTeamWins = wins[2 if team == 1 else 1]
            winsLimit = data.get('winsLimit')
            if winsLimit > 0 and playerTeamWins < winsLimit and otherTeamWins < winsLimit:
                winner = None
            elif playerTeamWins == otherTeamWins:
                winner = 0
            else:
                winner = 1 if wins[1] > wins[2] else 2
            battleResult = self._makeBattleResultString(kickReason, winner, team)
            total = ''
            if data.get('battlesLimit', 0) > 1:
                total = '({0:d}:{1:d})'.format(wins[1], wins[2])
            formatted = g_settings.msgTemplates.format('prebattleDestruction', ctx={'desc': self._makeDescriptionString(data, showBattlesCount=False),
             'opponents': self._getOpponentsString(data.get('opponents', {})),
             'result': battleResult,
             'total': total}, data={'timestamp': _getTimeStamp(message),
             'icon': self._getIconId(prbType)})
            return [_MessageData(formatted, self._getGuiSettings(message, 'prebattleDestruction'))]


class VehCamouflageTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get('vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format('vehCamouflageTimedOut', ctx={'vehicleName': getUserName(vType)})
        return [_MessageData(formatted, self._getGuiSettings(message, 'vehCamouflageTimedOut'))]


class VehEmblemTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get('vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format('vehEmblemTimedOut', ctx={'vehicleName': getUserName(vType)})
        return [_MessageData(formatted, self._getGuiSettings(message, 'vehEmblemTimedOut'))]


class VehInscriptionTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get('vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format('vehInscriptionTimedOut', ctx={'vehicleName': getUserName(vType)})
        return [_MessageData(formatted, self._getGuiSettings(message, 'vehInscriptionTimedOut'))]


class ConverterFormatter(ServiceChannelFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    def __i18nValue(self, key, isReceived, **kwargs):
        key = ('%sReceived' if isReceived else '%sWithdrawn') % key
        key = '#messenger:serviceChannelMessages/sysMsg/converter/%s' % key
        return i18n.makeString(key) % kwargs

    def __vehName(self, vehCompDescr):
        return getUserName(vehicles_core.getVehicleType(abs(vehCompDescr)))

    def format(self, message, *args):
        data = message.data
        text = []
        if data.get('inscriptions'):
            text.append(i18n.makeString('#messenger:serviceChannelMessages/sysMsg/converter/inscriptions'))
        if data.get('emblems'):
            text.append(i18n.makeString('#messenger:serviceChannelMessages/sysMsg/converter/emblems'))
        if data.get('camouflages'):
            text.append(i18n.makeString('#messenger:serviceChannelMessages/sysMsg/converter/camouflages'))
        if data.get('customizations'):
            text.append(i18n.makeString('#messenger:serviceChannelMessages/sysMsg/converter/customizations'))
        vehicles = data.get('vehicles')
        if vehicles:
            vehiclesReceived = [ self.__vehName(cd) for cd in vehicles if cd > 0 and self.itemsCache.items.doesVehicleExist(cd) ]
            if vehiclesReceived:
                text.append(self.__i18nValue('vehicles', True, vehicles=', '.join(vehiclesReceived)))
            vehiclesWithdrawn = [ self.__vehName(cd) for cd in vehicles if cd < 0 and self.itemsCache.items.doesVehicleExist(abs(cd)) ]
            if vehiclesWithdrawn:
                text.append(self.__i18nValue('vehicles', False, vehicles=', '.join(vehiclesWithdrawn)))
        slots = data.get('slots')
        if slots:
            text.append(self.__i18nValue('slots', slots > 0, slots=BigWorld.wg_getIntegralFormat(abs(slots))))
        for currency in Currency.ALL:
            value = data.get(currency)
            if value:
                formatter = getBWFormatter(currency)
                kwargs = {currency: formatter(abs(value))}
                text.append(self.__i18nValue(currency, (value > 0), **kwargs))

        freeXP = data.get('freeXP')
        if freeXP:
            text.append(self.__i18nValue('freeXP', freeXP > 0, freeXP=BigWorld.wg_getIntegralFormat(abs(freeXP))))
        formatted = g_settings.msgTemplates.format('ConverterNotify', {'text': '<br/>'.join(text)})
        return [_MessageData(formatted, self._getGuiSettings(message, 'ConverterNotify'))]


class ClientSysMessageFormatter(ServiceChannelFormatter):
    __templateKey = '%sSysMessage'

    def format(self, data, *args):
        if args:
            msgType, _, messageData, savedData = args[0]
        else:
            msgType = 'Error'
            messageData = None
            savedData = None
        templateKey = self.__templateKey % msgType
        ctx = {'text': data}
        if messageData:
            ctx.update(messageData)
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx, data={'savedData': savedData})
        return [_MessageData(formatted, self._getGuiSettings(args, templateKey))]

    def _getGuiSettings(self, data, key=None, priorityLevel=None, groupID=None):
        if isinstance(data, types.TupleType) and data:
            auxData = data[0][:]
            if len(data[0]) > 1 and priorityLevel is None:
                priorityLevel = data[0][1]
        else:
            auxData = []
        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        if groupID is None:
            groupID = g_settings.msgTemplates.groupID(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData, groupID=groupID)


class PremiumAccountExpiryFormatter(ClientSysMessageFormatter):

    def format(self, data, *args):
        formatted = g_settings.msgTemplates.format('durationOfPremiumAccountExpires', ctx={'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(data))})
        return [_MessageData(formatted, self._getGuiSettings(args, 'durationOfPremiumAccountExpires'))]


class SessionControlFormatter(ServiceChannelFormatter):

    def _doFormat(self, text, key, auxData):
        formatted = g_settings.msgTemplates.format(key, {'text': text})
        priorityLevel = g_settings.msgTemplates.priority(key)
        return [_MessageData(formatted, NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData))]


class AOGASNotifyFormatter(SessionControlFormatter):

    def format(self, data, *args):
        return self._doFormat(i18n.makeString('#aogas:{0:s}'.format(data.name())), 'AOGASNotify', *args)


class KoreaParentalControlFormatter(SessionControlFormatter):

    def format(self, data, *args):
        return self._doFormat(data, ('%sSysMessage' % SM_TYPE.Warning), *args)


class VehicleTypeLockExpired(ServiceChannelFormatter):

    def format(self, message, *args):
        result = []
        if message.data:
            ctx = {}
            vehTypeCompDescr = message.data.get('vehTypeCompDescr')
            if vehTypeCompDescr is None:
                templateKey = 'vehiclesAllLockExpired'
            else:
                templateKey = 'vehicleLockExpired'
                ctx['vehicleName'] = getUserName(vehicles_core.getVehicleType(vehTypeCompDescr))
            formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
            result = [_MessageData(formatted, self._getGuiSettings(message, 'vehicleLockExpired'))]
        return result


class ServerDowntimeCompensation(ServiceChannelFormatter):
    __templateKey = 'serverDowntimeCompensation'

    def format(self, message, *args):
        result = []
        subjects = ''
        data = message.data
        if data is not None:
            for key, value in data.items():
                if value:
                    if subjects:
                        subjects += ', '
                    subjects += i18n.makeString('#%s:serviceChannelMessages/' % MESSENGER_I18N_FILE + self.__templateKey + '/' + key)

            if subjects:
                formatted = g_settings.msgTemplates.format(self.__templateKey, ctx={'text': i18n.makeString('#%s:serviceChannelMessages/' % MESSENGER_I18N_FILE + self.__templateKey) % subjects})
                result = [_MessageData(formatted, self._getGuiSettings(message, self.__templateKey))]
        return result


class ActionNotificationFormatter(ClientSysMessageFormatter):
    __templateKey = 'action%s'

    def format(self, message, *args):
        result = []
        data = message.get('data')
        if data:
            templateKey = self.__templateKey % message.get('state', '')
            formatted = g_settings.msgTemplates.format(templateKey, ctx={'text': data}, data={'icon': message.get('type', '')})
            result = [_MessageData(formatted, self._getGuiSettings(args, templateKey))]
        return result


class BattleTutorialResultsFormatter(ClientSysMessageFormatter):
    __resultKeyWithBonuses = 'battleTutorialResBonuses'
    __resultKeyWoBonuses = 'battleTutorialResWoBonuses'

    def isNotify(self):
        return True

    def format(self, data, *args):
        LOG_DEBUG('message data', data)
        finishReason = data.get('finishReason', -1)
        resultKey = data.get('resultKey', None)
        finishKey = data.get('finishKey', None)
        if finishReason > -1 and resultKey and finishKey:
            resultString = i18n.makeString('#{0:s}:serviceChannelMessages/battleTutorial/results/{1:s}'.format(MESSENGER_I18N_FILE, resultKey))
            reasonString = i18n.makeString('#{0:s}:serviceChannelMessages/battleTutorial/reasons/{1:s}'.format(MESSENGER_I18N_FILE, finishKey))
            arenaTypeID = data.get('arenaTypeID', 0)
            arenaName = 'N/A'
            if arenaTypeID > 0:
                arenaName = ArenaType.g_cache[arenaTypeID].name
            vTypeCD = data.get('vTypeCD', None)
            vName = 'N/A'
            if vTypeCD is not None:
                vName = getUserName(vehicles_core.getVehicleType(vTypeCD))
            ctx = {'result': resultString,
             'reason': reasonString,
             'arenaName': i18n.makeString(arenaName),
             'vehicleName': vName,
             'freeXP': '0',
             Currency.CREDITS: '0'}
            freeXP = 0
            credits_ = 0
            chapters = data.get('chapters', [])
            for chapter in chapters:
                if chapter.get('received', False):
                    bonus = chapter.get('bonus', {})
                    freeXP += bonus.get('freeXP', 0)
                    credits_ += bonus.get(Currency.CREDITS, 0)

            if freeXP:
                ctx['freeXP'] = BigWorld.wg_getIntegralFormat(freeXP)
            if credits_:
                formatter = getBWFormatter(Currency.CREDITS)
                ctx[Currency.CREDITS] = formatter(credits_)
            all_ = data.get('areAllBonusesReceived', False)
            if all_ and credits_ <= 0 and freeXP <= 0:
                key = self.__resultKeyWoBonuses
            else:
                key = self.__resultKeyWithBonuses
            startedAtTime = data.get('startedAt', time.time())
            formatted = g_settings.msgTemplates.format(key, ctx=ctx, data={'timestamp': startedAtTime,
             'savedData': data.get('arenaUniqueID', 0)})
            return [_MessageData(formatted, self._getGuiSettings(args, key))]
        else:
            return []
            return


class BootcampResultsFormatter(WaitItemsSyncFormatter):

    def isNotify(self):
        return True

    @async
    @process
    def format(self, message, callback):
        LOG_DEBUG('message data', message)
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            text = []
            results = message.data
            if results:
                text.append(self.__formatAwards(results))
            else:
                text.append(i18n.makeString('#%s:serviceChannelMessages/bootcamp/no_awards' % MESSENGER_I18N_FILE))
            settings = self._getGuiSettings(message, 'bootcampResults')
            formatted = g_settings.msgTemplates.format('bootcampResults', {'text': '<br/>'.join(text)}, data={'timestamp': _getTimeStamp(message)})
        callback([_MessageData(formatted, settings)])
        return None

    def __formatAwards(self, results):
        awards = i18n.makeString('#%s:serviceChannelMessages/bootcamp/awards' % MESSENGER_I18N_FILE) + '<br/>'
        awards += self.__getAssetString(results, INVOICE_ASSET.GOLD, 'gold')
        awards += self.__getAssetString(results, INVOICE_ASSET.PREMIUM, 'premium')
        awards += self.__getAssetString(results, INVOICE_ASSET.CREDITS, 'credits')
        vehicles = results.get('vehicles', {})
        vehiclesNames = []
        devicesAndCrew = ''
        for vehID, vehData in vehicles.iteritems():
            vehicle = self.itemsCache.items.getItemByCD(vehID)
            if vehicle:
                if vehData.get('devices', None):
                    devicesAndCrew += self.__formatDevicesAndCrew(vehicle.userName, vehData)
                else:
                    vehiclesNames.append(vehicle.userName)

        awards += '<br/>'
        if vehiclesNames:
            awards += g_settings.htmlTemplates.format('vehiclesAccruedInvoiceReceived', ctx={'vehicles': ', '.join(vehiclesNames)}) + '<br/>'
        slots = results.get('slots', 0)
        if slots:
            awards += '<br/>' + g_settings.htmlTemplates.format('slotsAccruedInvoiceReceived', {'amount': BigWorld.wg_getIntegralFormat(abs(slots))})
        if devicesAndCrew:
            awards += devicesAndCrew
        return awards

    @staticmethod
    def __formatDevicesAndCrew(vehName, vehData):
        devices = vehData.get('devices', [])
        name = '<br/><br/><b>' + vehName + '</b>: <br/>'
        message = ''
        if devices:
            message += name
            message += i18n.makeString('#%s:serviceChannelMessages/bootcamp/devices' % MESSENGER_I18N_FILE)
            itemsNames = []
            for intCD, count in devices:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                if itemDescr.i18n.userString != '':
                    itemsNames.append(i18n.makeString('#%s:serviceChannelMessages/battleResults/quests/items/name' % MESSENGER_I18N_FILE, name=itemDescr.i18n.userString, count=BigWorld.wg_getIntegralFormat(count)))

            if itemsNames:
                message += '<br/>' + ', '.join(itemsNames) + '<br/>'
        crewInBarracks = vehData.get('crewInBarracks', False)
        if crewInBarracks:
            message += i18n.makeString('#%s:serviceChannelMessages/bootcamp/crew' % MESSENGER_I18N_FILE)
        return message

    @staticmethod
    def __getAssetString(results, assetType, amountType):
        amount = results.get(amountType, 0)
        if amount:
            templateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
             INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
             INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived'}
            return '<br/>' + g_settings.htmlTemplates.format(templateKeys[assetType], ctx={'amount': BigWorld.wg_getIntegralFormat(abs(amount))})


class TokenQuestsFormatter(WaitItemsSyncFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    __PERSONAL_MISSIONS_CUSTOM_TEMPLATE = 'personalMissionsCustom'

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageData = None
        if isSynced:
            data = message.data or {}
            completedQuestIDs = data.get('completedQuestIDs', set())
            completedQuestIDs.update(data.get('rewardsGottenQuestIDs', set()))
            if getSourceIdFromQuest(first(completedQuestIDs, '')):
                result = yield RecruitQuestsFormatter().format(message)
                callback(result)
                return
            if ranked_helpers.isRankedQuestID(first(completedQuestIDs, '')):
                result = yield RankedQuestFormatter(forToken=True).format(message)
                callback(result)
                return
            if self.__processPersonalMissionsSpecial(completedQuestIDs, message, callback):
                return
            messageData = self.__buildMessageData(message, completedQuestIDs)
        if messageData is None:
            messageData = _MessageData(None, None)
        callback([messageData])
        return

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True):
        result = []
        tokenResult = cls._processTokens(data)
        if tokenResult:
            result.append(tokenResult)
        if not asBattleFormatter:
            crystal = data.get(Currency.CRYSTAL, 0)
            if crystal:
                fomatter = getBWFormatter(Currency.CRYSTAL)
                result.append(cls.__makeQuestsAchieve('battleQuestsCrystal', crystal=fomatter(crystal)))
            gold = data.get(Currency.GOLD, 0)
            if gold:
                fomatter = getBWFormatter(Currency.GOLD)
                result.append(cls.__makeQuestsAchieve('battleQuestsGold', gold=fomatter(gold)))
        premium = data.get('premium', 0)
        if premium:
            result.append(cls.__makeQuestsAchieve('battleQuestsPremium', days=premium))
        if not asBattleFormatter:
            freeXP = data.get('freeXP', 0)
            if freeXP:
                result.append(cls.__makeQuestsAchieve('battleQuestsFreeXP', freeXP=BigWorld.wg_getIntegralFormat(freeXP)))
        vehiclesList = data.get('vehicles', [])
        for vehiclesData in vehiclesList:
            if vehiclesData:
                msg = InvoiceReceivedFormatter.getVehiclesString(vehiclesData, htmlTplPostfix='QuestsReceived')
                if msg:
                    result.append(msg)
                comptnStr = InvoiceReceivedFormatter.getVehiclesCompensationString(vehiclesData, htmlTplPostfix='QuestsReceived')
                if comptnStr:
                    result.append('<br/>' + comptnStr)

        if not asBattleFormatter:
            creditsVal = data.get(Currency.CREDITS, 0)
            if creditsVal:
                fomatter = getBWFormatter(Currency.CREDITS)
                result.append(cls.__makeQuestsAchieve('battleQuestsCredits', credits=fomatter(creditsVal)))
        slots = data.get('slots', 0)
        if slots:
            result.append(cls.__makeQuestsAchieve('battleQuestsSlots', slots=BigWorld.wg_getIntegralFormat(slots)))
        items = data.get('items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemDescr = vehicles_core.getItemByCompactDescr(intCD)
            itemsNames.append(i18n.makeString('#messenger:serviceChannelMessages/battleResults/quests/items/name', name=itemDescr.i18n.userString, count=BigWorld.wg_getIntegralFormat(count)))

        if itemsNames:
            result.append(cls.__makeQuestsAchieve('battleQuestsItems', names=', '.join(itemsNames)))
        if processCustomizations:
            _extendCustomizationData(data, result, htmlTplPostfix='QuestsReceived')
        berths = data.get('berths', 0)
        if berths:
            result.append(cls.__makeQuestsAchieve('battleQuestsBerths', berths=BigWorld.wg_getIntegralFormat(berths)))
        tmen = data.get('tankmen', {})
        if tmen:
            result.append(InvoiceReceivedFormatter.getTankmenString(tmen))
        goodies = data.get('goodies', {})
        if goodies:
            strGoodies = InvoiceReceivedFormatter.getGoodiesString(goodies)
            if strGoodies:
                result.append(strGoodies)
        if not asBattleFormatter:
            achieves = data.get('popUpRecords', [])
            achievesNames = set()
            badgesNames = set()
            for recordIdx, value in achieves:
                record = DB_ID_TO_RECORD[recordIdx]
                if record[0] == BADGES_BLOCK:
                    badgesNames.add(i18n.makeString(BADGE.badgeName(record[1])))
                    continue
                factory = getAchievementFactory(record)
                if factory is not None:
                    a = factory.create(value=int(value))
                    if a is not None:
                        achievesNames.add(a.getUserName())

            if achievesNames:
                result.append(cls.__makeQuestsAchieve('battleQuestsPopUps', achievements=', '.join(achievesNames)))
            if badgesNames:
                result.append(cls.__makeQuestsAchieve('badgeAchievement', badges=', '.join(badgesNames)))
        return '<br/>'.join(result) if result else None

    @classmethod
    def _processTokens(cls, tokens):
        pass

    @property
    def _templateName(self):
        pass

    @classmethod
    def __makeQuestsAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)

    def __processPersonalMissionsSpecial(self, questIDs, message, callback):
        result = []
        newAwardListCount = 0
        retAwardListCount = 0
        camouflageGivenFor = set()
        camouflageUnlockedFor = set()
        tankmenAward = False
        badges = []
        for quest in self._eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs).values():
            if quest.getID().endswith('camouflage'):
                for bonus in quest.getBonuses('customizations'):
                    camouflage = findFirst(lambda c: c.get('custType') == 'camouflage' and c.get('vehTypeCompDescr'), bonus.getCustomizations())
                    if camouflage:
                        camouflageGivenFor.add(camouflage.get('vehTypeCompDescr'))

            regex = re.search('pt_final_s(\\d)_t(\\d)_badge', quest.getID())
            if regex:
                operationID = int(regex.group(2))
                operations = self._eventsCache.getPersonalMissions().getAllOperations()
                if operationID in operations:
                    operation = operations[operationID]
                    camouflageUnlockedFor.add(operation.getVehicleBonus().intCD)
            for bonus in quest.getBonuses('dossier', []):
                for badge in bonus.getBadges():
                    name = badge.getShortUserName()
                    if name is None:
                        LOG_ERROR("Couldn't find user name for the badge {}! Declare necessary localizations in the badge.po file!".format(badge.badgeID))
                    badges.append(name)

        for qID in questIDs:
            if personal_missions.g_cache.isPersonalMission(qID):
                pmType = personal_missions.g_cache.questByUniqueQuestID(qID)
                quest = self._eventsCache.getPersonalMissions().getAllQuests().get(pmType.id)
                if quest and (qID.endswith('_main') or qID.endswith('_main_award_list')):
                    tmBonus = quest.getTankmanBonus()
                    if tmBonus.tankman:
                        tankmenAward = True
                if qID.endswith('add_award_list'):
                    addAwardListQI = pmType.addAwardListQuestInfo
                    tokensBonuses = addAwardListQI.get('bonus', {}).get('tokens', {})
                    for token in (constants.PERSONAL_MISSION_FREE_TOKEN_NAME, constants.PERSONAL_MISSION_2_FREE_TOKEN_NAME):
                        if token in tokensBonuses:
                            retAwardListCount += tokensBonuses[token]['count']

                if qID.endswith('add'):
                    addAwardListQI = pmType.addQuestInfo
                    tokensBonuses = addAwardListQI.get('bonus', {}).get('tokens', {})
                    for token in (constants.PERSONAL_MISSION_FREE_TOKEN_NAME, constants.PERSONAL_MISSION_2_FREE_TOKEN_NAME):
                        if token in tokensBonuses:
                            newAwardListCount += tokensBonuses[token]['count']

        if retAwardListCount > 0:
            text = i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_FREEAWARDLISTRETURN, count=retAwardListCount)
            result.append(text)
        if newAwardListCount > 0:
            text = i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_FREEAWARDLISTGAIN, count=newAwardListCount)
            result.append(text)
        for vehIntCD in camouflageGivenFor:
            vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
            text = i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_CAMOUFLAGEGIVEN, vehicleName=vehicle.userName)
            result.append(text)

        for vehIntCD in camouflageUnlockedFor:
            vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
            nationName = i18n.makeString(MENU.nations(vehicle.nationName))
            text = i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_CAMOUFLAGEUNLOCKED, vehicleName=vehicle.userName, nation=nationName)
            result.append(text)

        if badges:
            text = i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_BADGE, name=', '.join(badges))
            result.append(text)
        if tankmenAward:
            result.append(i18n.makeString(SYSTEM_MESSAGES.PERSONALMISSIONS_TANKMENGAIN))
        if result:
            callbackResult = []
            messageData = self.__buildMessageData(message, questIDs, withCustomizations=False)
            if messageData is not None:
                callbackResult.append(messageData)
            data = message.data or {}
            if not data.get('tankmen'):
                callbackResult.append(_MessageData(_getDefaultMessage(normal=_EOL.join(result)), self._getGuiSettings(message, _DEFAULT_MESSAGE)))
            callback(callbackResult)
            return True
        else:
            return False

    def __buildMessageData(self, message, questIDs, withCustomizations=True):
        data = message.data or {}
        fmt = self.formatQuestAchieves(data, asBattleFormatter=False, processCustomizations=withCustomizations)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            campaigns = set()
            for qID in questIDs:
                if personal_missions.g_cache.isPersonalMission(qID):
                    pmID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                    mission = self._eventsCache.getPersonalMissions().getAllQuests()[pmID]
                    campaigns.add(mission.getCampaignID())

            if campaigns:
                templateName = self.__PERSONAL_MISSIONS_CUSTOM_TEMPLATE
                campaignNameKey = 'both' if len(campaigns) == 2 else str(first(campaigns))
                templateParams['text'] = i18n.makeString(MESSENGER.personalMissionText(campaignNameKey))
            else:
                templateName = self._templateName
            settings = self._getGuiSettings(message, templateName)
            formatted = g_settings.msgTemplates.format(templateName, templateParams)
            return _MessageData(formatted, settings)
        else:
            return


class NCMessageFormatter(ServiceChannelFormatter):
    __templateKeyFormat = 'notificationsCenterMessage_{0}'

    def format(self, message, *args):
        LOG_DEBUG('Message has received from notification center', message)
        data = z_loads(message.data)
        if not data:
            return []
        if 'body' not in data or not data['body']:
            return []
        templateKey = self.__getTemplateKey(data)
        priority = self.__getGuiPriority(data)
        topic = self.__getTopic(data)
        body = self.__getBody(data)
        settings = self._getGuiSettings(message, templateKey, priority)
        msgType = data['type']
        if msgType == NC_MESSAGE_TYPE.POLL:
            if not GUI_SETTINGS.isPollEnabled:
                return []
            if not self.__fetchPollData(data, settings):
                return []
        formatted = g_settings.msgTemplates.format(templateKey, ctx={'topic': topic,
         'body': body})
        return [_MessageData(formatted, settings)]

    def __getTemplateKey(self, data):
        if 'type' in data:
            msgType = data['type']
            if msgType not in NC_MESSAGE_TYPE.RANGE:
                LOG_WARNING('Type of message is not valid, uses default type', msgType)
                msgType = NC_MESSAGE_TYPE.INFO
        else:
            msgType = NC_MESSAGE_TYPE.INFO
        return self.__templateKeyFormat.format(msgType)

    def __getGuiPriority(self, data):
        priority = NC_MESSAGE_PRIORITY.DEFAULT
        if 'priority' in data:
            priority = data['priority']
            if priority not in NC_MESSAGE_PRIORITY.ORDER:
                LOG_WARNING('Priority of message is not valid, uses default priority', priority)
                priority = NC_MESSAGE_PRIORITY.DEFAULT
        return NotificationPriorityLevel.convertFromNC(priority)

    def __getTopic(self, data):
        topic = ''
        if 'topic' in data:
            topic = i18n.encodeUtf8(data['topic'])
        if topic:
            topic = g_settings.htmlTemplates.format('notificationsCenterTopic', ctx={'topic': topic})
        return topic

    def __getBody(self, data):
        body = i18n.encodeUtf8(data['body'])
        if 'context' in data:
            body = body % self.__formatContext(data['context'])
        return body

    def __fetchPollData(self, data, settings):
        result = False
        if 'link' in data and data['link']:
            if 'topic' in data:
                topic = i18n.encodeUtf8(data['topic'])
            else:
                topic = ''
            settings.auxData = [data['link'], topic]
            result = True
        return result

    def __formatContext(self, ctx):
        result = {}
        if not isinstance(ctx, types.DictType):
            LOG_ERROR('Context is invalid', ctx)
            return result
        getItemFormat = NCContextItemFormatter.getItemFormat
        for key, item in ctx.iteritems():
            if len(item) > 1:
                itemType, itemValue = item[0:2]
                result[key] = getItemFormat(itemType, itemValue)
            LOG_ERROR('Context item is invalid', item)
            result[key] = str(item)

        return result


class ClanMessageFormatter(ServiceChannelFormatter):
    __templates = {SYS_MESSAGE_CLAN_EVENT.LEFT_CLAN: 'clanMessageWarning'}

    def format(self, message, *args):
        LOG_DEBUG('Message has received from clan', message)
        data = message.data
        if data and 'event' in data:
            event = data['event']
            templateKey = self.__templates.get(event)
            fullName = getClanFullName(passCensor(data['clanName']), passCensor(data['clanAbbrev']))
            message = i18n.makeString('#messenger:serviceChannelMessages/clan/%s' % SYS_MESSAGE_CLAN_EVENT_NAMES[event])
            formatted = g_settings.msgTemplates.format(templateKey, ctx={'message': message,
             'fullClanName': fullName})
            settings = self._getGuiSettings(message, templateKey)
            return [_MessageData(formatted, settings)]
        return []


class StrongholdMessageFormatter(ServiceChannelFormatter):
    __templates = {constants.SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED: 'fortReserveActivatedMessage'}
    DEFAULT_WARNING = 'fortMessageWarning'

    def __init__(self):
        super(StrongholdMessageFormatter, self).__init__()
        self.__messagesFormatters = {constants.SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED: BoundMethodWeakref(self._reserveActivatedMessage),
         constants.SYS_MESSAGE_FORT_EVENT.RESERVE_EXPIRED: BoundMethodWeakref(self._reserveExpiredMessage)}

    def format(self, message, *args):
        LOG_DEBUG('Message has received from fort', message)
        data = message.data
        if data and 'event' in data:
            event = data['event']
            templateKey = self.__templates.get(event, self.DEFAULT_WARNING)
            formatter = self.__messagesFormatters.get(event)
            if formatter is not None:
                messageSting = formatter(data)
                formatted = g_settings.msgTemplates.format(templateKey, ctx={'message': messageSting})
                settings = self._getGuiSettings(message, templateKey)
                return [_MessageData(formatted, settings)]
            LOG_WARNING('StrongholdMessageFormatter has no available formatters for given message type: ', event)
        return []

    def _buildMessage(self, event, ctx=None):
        if ctx is None:
            ctx = {}
        return i18n.makeString(('#messenger:serviceChannelMessages/fort/%s' % SYS_MESSAGE_FORT_EVENT_NAMES[event]), **ctx)

    def getOrderUserString(self, orderTypeID):
        return i18n.makeString('#fortifications:orders/%s' % constants.FORT_ORDER_TYPE_NAMES[orderTypeID])

    def _reserveActivatedMessage(self, data):
        event = data['event']
        orderTypeID = data['orderTypeID']
        expirationTime = data['timeExpiration']
        order = text_styles.neutral(self.getOrderUserString(orderTypeID))
        return self._buildMessage(event, {'order': order,
         'timeLeft': time_utils.getTillTimeString(time_utils.getTimeDeltaFromNow(expirationTime), MENU.TIME_TIMEVALUEWITHSECS)})

    def _reserveExpiredMessage(self, data):
        return self._buildMessage(data['event'], {'order': self.getOrderUserString(data['orderTypeID'])})


class VehicleRentedFormatter(ServiceChannelFormatter):
    _templateKey = 'vehicleRented'

    def format(self, message, *args):
        data = message.data
        vehTypeCD = data.get('vehTypeCD', None)
        expiryTime = data.get('time', None)
        return [_MessageData(self._getMessage(vehTypeCD, expiryTime), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else []

    def _getMessage(self, vehTypeCD, expiryTime):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {'vehicleName': vehicleName,
         'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class RentalsExpiredFormatter(ServiceChannelFormatter):
    _templateKey = 'rentalsExpired'

    def format(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD', None)
        return [_MessageData(self._getMessage(vehTypeCD), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else (None, None)

    def _getMessage(self, vehTypeCD):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {'vehicleName': vehicleName}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class RefSystemReferralBoughtVehicleFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        settings = self._getGuiSettings(message, 'refSystemBoughtVehicle')
        formatted = g_settings.msgTemplates.format('refSystemBoughtVehicle', {'userName': message.data.get('nickName', '')})
        return [_MessageData(formatted, settings)]


class RefSystemReferralContributedXPFormatter(WaitItemsSyncFormatter):
    eventsCache = dependency.descriptor(IEventsCache)

    def isNotify(self):
        return True

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            refSystemQuests = self.eventsCache.getHiddenQuests(lambda x: x.getType() == EVENT_TYPE.REF_SYSTEM_QUEST)
            notCompleted = findFirst(lambda q: not q.isCompleted(), refSystemQuests.values())
            if notCompleted:
                data = message.data
                settings = self._getGuiSettings(message, 'refSystemContributeXp')
                formatted = g_settings.msgTemplates.format('refSystemContributeXp', {'userName': data.get('nickName', ''),
                 'xp': BigWorld.wg_getIntegralFormat(data.get('xp', 0))})
                callback([_MessageData(formatted, settings)])
            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return


class RefSystemQuestsFormatter(TokenQuestsFormatter):

    @property
    def _templateName(self):
        pass


class RecruitQuestsFormatter(WaitItemsSyncFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data or {}
            fmt = TokenQuestsFormatter.formatQuestAchieves(data, asBattleFormatter=False)
            if fmt is not None:
                operationTime = message.sentTime
                if operationTime:
                    fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
                else:
                    fDatetime = 'N/A'
                formatted = g_settings.msgTemplates.format(self._getTemplateName(), ctx={'at': fDatetime,
                 'desc': '',
                 'op': fmt})
                settings = self._getGuiSettings(message, self._getTemplateName())
        callback([_MessageData(formatted, settings)])
        return

    def _getTemplateName(self):
        pass


class PersonalMissionsFormatter(TokenQuestsFormatter):

    @property
    def _templateName(self):
        pass

    @classmethod
    def _processTokens(cls, data):
        quest = cls._eventsCache.getPersonalMissions().getAllQuests().get(data.get('potapovQuestID'))
        if quest:
            result = []
            completionToken = PERSONAL_MISSION_TOKEN % (quest.getCampaignID(), quest.getOperationID())
            if completionToken in data.get('tokens', {}):
                bonuses = quest.getBonuses('tokens')
                if bonuses:
                    for b in bonuses:
                        if b.getName() == 'completionTokens' and completionToken in b.getTokens().keys():
                            tUserName = first(CompletionTokensBonusFormatter().format(b)).userName
                            result.append(g_settings.htmlTemplates.format('completionTokens', {'completionToken': tUserName}))

            return ', '.join(result)


class GoodyFormatter(WaitItemsSyncFormatter):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            goodieID = message.data.get('gid', None)
            if goodieID is not None:
                booster = self.goodiesCache.getBooster(goodieID)
                if booster is not None:
                    formatted = g_settings.msgTemplates.format(self._getTemplateName(), ctx={'boosterName': booster.userName})
                    callback([_MessageData(formatted, self._getGuiSettings(message, self._getTemplateName()))])
                    return
            callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return

    def _getTemplateName(self):
        raise NotImplementedError

    def canBeEmpty(self):
        return True


class GoodyRemovedFormatter(GoodyFormatter):

    def _getTemplateName(self):
        pass


class GoodyDisabledFormatter(GoodyFormatter):

    def _getTemplateName(self):
        pass


class TelecomStatusFormatter(ServiceChannelFormatter):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def __getVehicleNames(cls, vehTypeCompDescrs):
        itemGetter = cls.itemsCache.items.getItemByCD
        return ', '.join((itemGetter(vehicleCD).userName for vehicleCD in vehTypeCompDescrs))

    def format(self, message, *args):
        formatted, settings = (None, None)
        try:
            template = 'telecomVehicleStatus'
            ctx = self.__getMessageContext(message.data)
            settings = self._getGuiSettings(message, template)
            formatted = g_settings.msgTemplates.format(template, ctx, data={'timestamp': time.time()})
        except Exception:
            LOG_ERROR("Can't format telecom status message ", message)
            LOG_CURRENT_EXCEPTION()

        return [_MessageData(formatted, settings)]

    def __getMessageContext(self, data):
        key = 'vehicleUnblocked' if data['orderStatus'] else 'vehicleBlocked'
        vehTypeDescrs = data['vehTypeCompDescrs']
        if vehTypeDescrs:
            serverSettings = self.lobbyContext.getServerSettings()
            vehInvID = self.itemsCache.items.getItemByCD(list(vehTypeDescrs)[0]).invID
            provider = BigWorld.player().inventory.getProviderForVehInvId(vehInvID, serverSettings)
        else:
            provider = ''
        if provider:
            i18nProvider = i18n.makeString(MENU.internetProviderName(provider))
            if i18nProvider is None:
                i18nProvider = ''
        else:
            i18nProvider = ''
        msgctx = {'vehicles': self.__getVehicleNames(vehTypeDescrs),
         'provider': i18nProvider}
        ctx = {}
        for txtBlock in ('title', 'comment', 'subcomment'):
            ctx[txtBlock] = i18n.makeString('#system_messages:telecom/notifications/{0:s}/{1:s}'.format(key, txtBlock), **msgctx)

        return ctx


class TelecomReceivedInvoiceFormatter(InvoiceReceivedFormatter):

    @staticmethod
    def invoiceHasCrew(data):
        dataEx = data.get('data', {})
        hasCrew = False
        vehicles = dataEx.get('vehicles', {})
        for vehicle in vehicles:
            if vehicles[vehicle].get('tankmen', None):
                hasCrew = True

        return hasCrew

    @staticmethod
    def invoiceHasBrotherhood(data):
        dataEx = data.get('data', {})
        hasBrotherhood = False
        vehicles = dataEx.get('vehicles', {})
        for vehicle in vehicles:
            tankmens = vehicles[vehicle].get('tankmen', [])
            for tman in tankmens:
                if isinstance(tman, str):
                    tankmanDecsr = tankmen.TankmanDescr(compactDescr=tman)
                    if 'brotherhood' in tankmanDecsr.freeSkills:
                        hasBrotherhood = True
                        break
                if 'brotherhood' in tman.get('freeSkills', []):
                    hasBrotherhood = True
                    break

        return hasBrotherhood

    def _getVehicles(self, data):
        dataEx = data.get('data', {})
        if not dataEx:
            return
        else:
            vehicles = dataEx.get('vehicles', {})
            rentedVehNames = None
            if vehicles:
                _, _, rentedVehNames = self._getVehicleNames(vehicles)
            return rentedVehNames

    def _getMessageTemplateKey(self, data):
        pass

    def _getMessageContext(self, data, vehicleNames):
        ctx = {}
        hasCrew = self.invoiceHasCrew(data)
        if hasCrew:
            if self.invoiceHasBrotherhood(data):
                skills = ' (%s)' % i18n.makeString(ITEM_TYPES.TANKMAN_SKILLS_BROTHERHOOD)
            else:
                skills = ''
            ctx['crew'] = i18n.makeString(SYSTEM_MESSAGES.TELECOM_NOTIFICATIONS_VEHICLERECEIVED_CREW, skills=skills)
        else:
            ctx['crew'] = ''
        ctx['vehicles'] = ', '.join(vehicleNames)
        ctx['datetime'] = self._getOperationTimeString(data)
        return ctx

    def _formatData(self, assetType, data):
        vehicleNames = self._getVehicles(data)
        return None if not vehicleNames else g_settings.msgTemplates.format(self._getMessageTemplateKey(None), ctx=self._getMessageContext(data, vehicleNames), data={'timestamp': time.time()})


class TelecomRemovedInvoiceFormatter(TelecomReceivedInvoiceFormatter):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getMessageTemplateKey(self, data):
        pass

    def _getVehicles(self, data):
        dataEx = data.get('data', {})
        if not dataEx:
            return
        else:
            vehicles = dataEx.get('vehicles', {})
            removedVehNames = None
            if vehicles:
                _, removedVehNames, _ = self._getVehicleNames(vehicles)
            return removedVehNames

    def _getMessageContext(self, data, vehicleNames):
        provider = ''
        if 'data' in data and 'vehicles' in data['data']:
            vehicles = data['data']['vehicles']
            for vehCompDescr in vehicles.iterkeys():
                if vehCompDescr < 0:
                    serverSettings = self.lobbyContext.getServerSettings()
                    vehInvID = self.itemsCache.items.getItemByCD(abs(vehCompDescr)).invID
                    provider = BigWorld.player().inventory.getProviderForVehInvId(vehInvID, serverSettings)
                    break

        return {'vehicles': ', '.join(vehicleNames),
         'datetime': self._getOperationTimeString(data),
         'tariff': i18n.makeString(MENU.internetProviderTariff(provider))}


class PrbVehicleKickFormatter(ServiceChannelFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        self.itemsCache.items.getVehicle(vehInvID)
        if vehInvID:
            vehicle = self.itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format('prbVehicleKick', ctx={'vehName': vehicle.userName})
        return [_MessageData(formatted, self._getGuiSettings(message, 'prbVehicleKick'))]


class PrbVehicleMaxSpgKickFormatter(ServiceChannelFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        if vehInvID:
            vehicle = self.itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format('prbVehicleMaxSpgKick', ctx={'vehName': vehicle.userName})
        return [_MessageData(formatted, self._getGuiSettings(message, 'prbVehicleMaxSpgKick'))]


class RotationGroupLockFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        templateKey = self._getMessageTemplateKey()
        if isinstance(message.data, list):
            groups = ', '.join(map(str, message.data))
        else:
            groups = message.data
        formatted = g_settings.msgTemplates.format(templateKey, ctx={'groupNum': groups})
        return [_MessageData(formatted, self._getGuiSettings(message, templateKey))]

    def _getMessageTemplateKey(self):
        pass


class RotationGroupUnlockFormatter(RotationGroupLockFormatter):

    def _getMessageTemplateKey(self):
        pass


class RankedQuestFormatter(WaitItemsSyncFormatter):
    eventsCache = dependency.descriptor(IEventsCache)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, forToken=False):
        super(RankedQuestFormatter, self).__init__()
        self.__forToken = forToken
        self.__rankAwardsFormatters = ((Currency.CRYSTAL, getBWFormatter(Currency.CRYSTAL)),
         (Currency.CREDITS, getBWFormatter(Currency.CREDITS)),
         (Currency.GOLD, getBWFormatter(Currency.GOLD)),
         ('points', lambda b: b))
        self.__finalAwardsFormatters = (('league', lambda b: b), ('league/cycle', lambda b: b), ('points', lambda b: b))
        self.__awardsStyles = {Currency.CREDITS: text_styles.credits,
         Currency.GOLD: text_styles.gold,
         Currency.CRYSTAL: text_styles.crystal}

    @async
    @process
    def format(self, message, callback=None):
        data = message.data.copy()
        formattedRanks = []
        finalAwards = None
        savedData = None
        title = ''
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            quests = self.eventsCache.getHiddenQuests()
            completedQuestIDs = message.data.get('completedQuestIDs', set())
            for questID in completedQuestIDs:
                quest = quests.get(questID)
                if quest is not None:
                    if self.__forToken:
                        seasonID, _, _ = ranked_helpers.getRankedDataFromTokenQuestID(quest.getID())
                        season = self.rankedController.getSeason(seasonID)
                        if season is not None:
                            title = i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATIONS_SEASONRESULTS)
                            extraAwards = {'points': season.getPoints()}
                            leagueData = yield self.rankedController.getLeagueData()
                            if leagueData is not None:
                                extraAwards['league'] = leagueData['league']
                            finalAwards = self.__packFinalAwards(self.__makeAwardsDict(extraAwards, data))
                            savedData = {'quest': quest,
                             'awards': data}
                    elif quest.isForRank() or quest.isForVehicleMastering():
                        if quest.isForVehicleMastering():
                            vehicleIntCD = first(data.get('playerVehicles'))
                            vehicle = self.itemsCache.items.getItemByCD(vehicleIntCD)
                            locKey = SYSTEM_MESSAGES.RANKED_NOTIFICATIONS_SINGLEVEHRANK_TEXT
                            rank = self.rankedController.getCurrentRank(vehicle)
                        else:
                            locKey = SYSTEM_MESSAGES.RANKED_NOTIFICATIONS_SINGLERANK_TEXT
                            rank = self.rankedController.getRank(quest.getRank())
                        awards = self.__packRankAwards(self.__makeAwardsDict({'points': rank.getPoints()}, {}))
                        formattedRanks.append(i18n.makeString(locKey, rankName=rank.getUserName(), awards=awards))
                    elif quest.isProcessedAtCycleEnd():
                        season = self.rankedController.getSeason(quest.getSeasonID())
                        if season is not None:
                            cycle = season.getAllCycles().get(quest.getCycleID())
                            extraAwards = {'points': cycle.points}
                            leagueData = yield self.rankedController.getLeagueData()
                            if leagueData is not None:
                                extraAwards['league/cycle'] = leagueData['league']
                            cycleNumber = cycle.ordinalNumber
                            title = i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATIONS_CYCLERESULTS, number=cycleNumber)
                            finalAwards = self.__packFinalAwards(self.__makeAwardsDict(extraAwards, data))

        if finalAwards:
            awardsBlocks = [finalAwards]
            awardsBlocks.extend(formattedRanks)
            additionalData = None
            if savedData is not None:
                additionalData = {'savedData': savedData}
            formatted = g_settings.msgTemplates.format('rankedCycleQuest', ctx={'awardsBlocks': _EOL.join(awardsBlocks),
             'title': title}, data=additionalData)
            if additionalData is None and 'buttonsStates' in formatted:
                formatted['buttonsStates'].update({'submit': 0})
        elif formattedRanks:
            overallAwardsExceptPoints = self.__packRankAwards(data.copy())
            if overallAwardsExceptPoints:
                formattedRanks.append(overallAwardsExceptPoints)
            formatted = g_settings.msgTemplates.format('rankedRankQuest', ctx={'rankBlocks': _EOL.join(formattedRanks)})
        else:
            formatted = None
        callback([_MessageData(formatted, self._getGuiSettings(message))])
        return

    @staticmethod
    def __makeAwardsDict(extraAwards, awards):
        awardsDict = awards.copy()
        awardsDict.update(extraAwards)
        return awardsDict

    def __packRankAwards(self, awardsDict):
        result = self.__packAwards(awardsDict, self.__rankAwardsFormatters)
        otherStr = TokenQuestsFormatter.formatQuestAchieves(awardsDict, asBattleFormatter=False)
        if otherStr:
            result.append(otherStr)
        return _EOL.join(result)

    def __packFinalAwards(self, awardsDict):
        result = self.__packAwards(awardsDict, self.__finalAwardsFormatters, '/final')
        result.append(i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATION_FINAL_BEFORECOMMONLIST))
        result.append(self.__packRankAwards(awardsDict))
        return _EOL.join(result)

    def __packAwards(self, awardsDict, formattersList, extraKey=''):
        result = []
        for awardName, extractor in formattersList:
            award = None
            if awardName in awardsDict:
                award = awardsDict.pop(awardName)
            elif awardName == 'other':
                award = awardsDict
            if award is not None:
                value = extractor(award)
                if value and value != '0':
                    result.append(self.__packAward(awardName, value, extraKey))

        return result

    def __packAward(self, key, value, extraKey):
        return '{} {}'.format(i18n.makeString(SYSTEM_MESSAGES.getRankedNotificationBonusName(name=key, extra=extraKey)), self.__awardsStyles.get(key, text_styles.stats)(value))


class PersonalMissionFailedFormatter(WaitItemsSyncFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    _template = 'PersonalMissionFailedMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            potapovQuestIDs = data.get('questIDs')
            if potapovQuestIDs:
                questsDict = {}
                for questID in potapovQuestIDs:
                    if questID and personal_missions.g_cache.isPersonalMission(questID):
                        pmType = personal_missions.g_cache.questByUniqueQuestID(questID)
                        quest = self._eventsCache.getPersonalMissions().getAllQuests().get(pmType.id)
                        questsDict.setdefault(pmType.id, [])
                        questsDict[pmType.id].append(quest)

                for questID, questList in questsDict.iteritems():
                    quest = first(questList)
                    operation = self._eventsCache.getPersonalMissions().getAllOperations().get(quest.getOperationID())
                    ctx = {'questID': questID,
                     'operation': operation.getShortUserName(),
                     'missionShortName': quest.getShortUserName(),
                     'missionName': quest.getUserName()}
                    formatted = g_settings.msgTemplates.format(self._template, ctx=ctx, data={'savedData': {'questID': questID}})
                    settings = self._getGuiSettings(message, self._template)
                    settings.showAt = BigWorld.time()
                    callback([_MessageData(formatted, settings)])

            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return


class CustomizationChangedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        text = i18n.makeString('#messenger:serviceChannelMessages/sysMsg/converter/customizations')
        formatted = g_settings.msgTemplates.format('CustomizationChanged', {'text': text})
        return [_MessageData(formatted, self._getGuiSettings(message, 'CustomizationChanged'))]


class LootBoxAutoOpenFormatter(WaitItemsSyncFormatter):
    _template = 'LootBoxesAutoOpenMessage'
    _templateRewards = 'LootBoxRewardsSysMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            if 'boxIDs' in data and 'rewards' in data:
                formatted = g_settings.msgTemplates.format(self._template, ctx={'count': sum(data['boxIDs'].values())}, data={'savedData': {'rewards': data['rewards']}})
                settings = self._getGuiSettings(message, self._template)
                settings.groupID = NotificationGroup.OFFER
                settings.showAt = BigWorld.time()
                fmt = TokenQuestsFormatter.formatQuestAchieves(getMergedLootBoxBonuses((data['rewards'],)), False)
                formattedRewards = g_settings.msgTemplates.format(self._templateRewards, ctx={'text': fmt})
                settingsRewards = self._getGuiSettings(message, self._templateRewards)
                settingsRewards.showAt = BigWorld.time()
                callback([_MessageData(formatted, settings), _MessageData(formattedRewards, settingsRewards)])
            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return
