# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel.py
import time
from collections import defaultdict
import types
import operator
from Queue import Queue
import constants
import account_helpers
import ArenaType
import BigWorld
import potapov_quests
from FortifiedRegionBase import FORT_ATTACK_RESULT, NOT_ACTIVATED
from adisp import async, process
from chat_shared import decompressSysMessage
from club_shared import ladderRating
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from helpers import dependency
from shared_utils import BoundMethodWeakref, findFirst
from gui.goodies import g_goodiesCache
from gui.shared.formatters import text_styles
from gui import GUI_SETTINGS
from gui.LobbyContext import g_lobbyContext
from gui.clubs.formatters import getLeagueString, getDivisionString
from gui.clubs.settings import getLeagueByDivision
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.clans.formatters import getClanAbbrevString, getClanFullName
from gui.shared import formatters as shared_fmts, g_itemsCache
from gui.shared.fortifications import formatters as fort_fmts
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.gui_items.Tankman import Tankman, calculateRoleLevel
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings, MsgCustomEvents
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from gui.shared.utils.transport import z_loads
from gui.shared.gui_items.Vehicle import getUserName
from gui.shared.money import Money, ZERO_MONEY, Currency
from gui.shared.formatters.currency import getBWFormatter
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.prb_control import prbInvitesProperty
from helpers import i18n, html, getClientLanguage, getLocalizedData
from helpers import time_utils
from items import getTypeInfoByIndex, getTypeInfoByName, vehicles as vehicles_core
from account_helpers import rare_achievements
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from messenger import g_settings
from messenger.ext import passCensor
from messenger.m_constants import MESSENGER_I18N_FILE
from predefined_hosts import g_preDefinedHosts
from constants import INVOICE_ASSET, AUTO_MAINTENANCE_TYPE, PREBATTLE_INVITE_STATE, AUTO_MAINTENANCE_RESULT, PREBATTLE_TYPE, FINISH_REASON, KICK_REASON_NAMES, KICK_REASON, NC_MESSAGE_TYPE, NC_MESSAGE_PRIORITY, SYS_MESSAGE_CLAN_EVENT, SYS_MESSAGE_CLAN_EVENT_NAMES, SYS_MESSAGE_FORT_EVENT, SYS_MESSAGE_FORT_EVENT_NAMES, FORT_BUILDING_TYPE, FORT_ORDER_TYPE, FORT_BUILDING_TYPE_NAMES, ARENA_GUI_TYPE, EVENT_TYPE
from messenger.formatters import TimeFormatter, NCContextItemFormatter
from skeletons.gui.server_events import IEventsCache

def _getTimeStamp(message):
    if message.createdAt is not None:
        result = time.mktime(message.createdAt.timetuple())
    else:
        LOG_WARNING('Invalid value of created_at = None')
        result = time.time()
    return result


def _extendCustomizationData(newData, extendable):
    if extendable is None:
        return
    else:
        customizations = newData.get('customizations', [])
        for customizationItem in customizations:
            custType = customizationItem['custType']
            custValue = customizationItem['value']
            custIsPermanent = customizationItem['isPermanent']
            if custValue < 0:
                extendable.append(i18n.makeString('#system_messages:customization/removed/%s' % custType))
            if custIsPermanent and custValue > 1:
                extendable.append(i18n.makeString('#system_messages:customization/added/%sValue' % custType, custValue))
            extendable.append(i18n.makeString('#system_messages:customization/added/%s' % custType))

        return


@async
def _getRareTitle(rareID, callback):
    rare_achievements.getRareAchievementText(getClientLanguage(), rareID, lambda rID, text: callback(text.get('title')))


@async
@process
def _processRareAchievements(rares, callback):
    unknownAchieves = 0
    achievements = []
    for rareID in rares:
        title = yield _getRareTitle(rareID)
        if title is None:
            unknownAchieves += 1
        achievements.append(title)

    if unknownAchieves:
        achievements.append(i18n.makeString('#system_messages:%s/title' % ('actionAchievements' if unknownAchieves > 1 else 'actionAchievement')))
    callback(achievements)
    return


class ServiceChannelFormatter(object):

    def format(self, data, *args):
        return (None, None)

    def isNotify(self):
        return True

    def isAsync(self):
        return False

    def _getGuiSettings(self, data, key=None, priorityLevel=None):
        try:
            isAlert = data.isHighImportance and data.active
        except AttributeError:
            isAlert = False

        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel, isAlert)


class WaitItemsSyncFormatter(ServiceChannelFormatter):

    def __init__(self):
        self.__callbackQueue = None
        return

    def isAsync(self):
        return True

    @async
    def _waitForSyncItems(self, callback):
        from gui.christmas.christmas_controller import g_christmasCtrl
        if g_itemsCache.isSynced() and g_christmasCtrl.isKnownToysReceived():
            callback(True)
        else:
            self.__registerHandler(callback)

    def __registerHandler(self, callback):
        from gui.christmas.christmas_controller import g_christmasCtrl
        if not self.__callbackQueue:
            self.__callbackQueue = Queue()
        self.__callbackQueue.put(callback)
        g_itemsCache.onSyncCompleted += self.__onSyncCompleted
        g_christmasCtrl.onToysCacheChanged += self.__onSyncCompleted

    def __unregisterHandler(self):
        from gui.christmas.christmas_controller import g_christmasCtrl
        assert self.__callbackQueue.empty()
        self.__callbackQueue = None
        g_christmasCtrl.onToysCacheChanged -= self.__onSyncCompleted
        g_itemsCache.onSyncCompleted -= self.__onSyncCompleted
        return

    def __onSyncCompleted(self, *args):
        while not self.__callbackQueue.empty():
            self.__callbackQueue.get_nowait()(g_itemsCache.isSynced())

        self.__unregisterHandler()


class ServerRebootFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverReboot', ctx={'date': local_dt.strftime('%c')})
            return (formatted, self._getGuiSettings(message, 'serverReboot'))
        else:
            return (None, None)
            return None


class ServerRebootCancelledFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverRebootCancelled', ctx={'date': local_dt.strftime('%c')})
            return (formatted, self._getGuiSettings(message, 'serverRebootCancelled'))
        else:
            return (None, None)
            return None


class BattleResultsFormatter(WaitItemsSyncFormatter):
    __battleResultKeys = {-1: 'battleDefeatResult',
     0: 'battleDrawGameResult',
     1: 'battleVictoryResult'}
    __eventBattleResultKeys = {-1: 'battleEndedGameResult',
     0: 'battleEndedGameResult',
     1: 'battleVictoryResult'}
    __goldTemplateKey = 'battleResultGold'
    __questsTemplateKey = 'battleQuests'
    __i18n_penalty = i18n.makeString('#%s:serviceChannelMessages/battleResults/penaltyForDamageAllies' % MESSENGER_I18N_FILE)
    __i18n_contribution = i18n.makeString('#%s:serviceChannelMessages/battleResults/contributionForDamageAllies' % MESSENGER_I18N_FILE)

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
                 'credits': '0'}
                vehicleNames = {}
                popUpRecords = []
                marksOfMastery = []
                vehs = []
                for vehIntCD, vehBattleResults in battleResults.get('playerVehicles', {}).iteritems():
                    v = g_itemsCache.items.getItemByCD(vehIntCD)
                    vehs.append(v)
                    vehicleNames[vehIntCD] = v.userName
                    popUpRecords.extend(vehBattleResults.get('popUpRecords', []))
                    if 'markOfMastery' in vehBattleResults and vehBattleResults['markOfMastery'] > 0:
                        marksOfMastery.append(vehBattleResults['markOfMastery'])

                ctx['vehicleNames'] = ', '.join(map(operator.attrgetter('userName'), sorted(vehs)))
                xp = battleResults.get('xp')
                if xp:
                    ctx['xp'] = BigWorld.wg_getIntegralFormat(xp)
                battleResKey = battleResults.get('isWinner', 0)
                ctx['xpEx'] = self.__makeXpExString(xp, battleResKey, battleResults.get('xpPenalty', 0), battleResults)
                ctx['gold'] = self.__makeGoldString(battleResults.get('gold', 0))
                accCredits = battleResults.get('credits') - battleResults.get('creditsToDraw', 0)
                if accCredits:
                    ctx['credits'] = BigWorld.wg_getIntegralFormat(accCredits)
                ctx['creditsEx'] = self.__makeCreditsExString(accCredits, battleResults.get('creditsPenalty', 0), battleResults.get('creditsContributionIn', 0), battleResults.get('creditsContributionOut', 0))
                ctx['fortResource'] = self.__makeFortResourceString(battleResults)
                guiType = battleResults.get('guiType', 0)
                ctx['fortResource'] = ''
                if guiType == ARENA_GUI_TYPE.SORTIE:
                    ctx['fortResource'] = self.__makeFortResourceString(battleResults)
                ctx['achieves'] = self.__makeAchievementsString(popUpRecords, marksOfMastery)
                ctx['lock'] = self.__makeVehicleLockString(vehicleNames, battleResults)
                ctx['quests'] = self.__makeQuestsAchieve(message)
                team = battleResults.get('team', 0)
                ctx['fortBuilding'] = ''
                if guiType == ARENA_GUI_TYPE.FORT_BATTLE:
                    fortBuilding = battleResults.get('fortBuilding')
                    if fortBuilding is not None:
                        buildTypeID, buildTeam = fortBuilding.get('buildTypeID'), fortBuilding.get('buildTeam')
                        if buildTypeID:
                            ctx['fortBuilding'] = g_settings.htmlTemplates.format('battleResultFortBuilding', ctx={'fortBuilding': FortBuilding(typeID=buildTypeID).userName,
                             'clanAbbrev': ''})
                        if battleResKey == 0:
                            battleResKey = 1 if buildTeam == team else -1
                ctx['club'] = self.__makeClubString(battleResults)
                if guiType == ARENA_GUI_TYPE.FALLOUT_MULTITEAM:
                    templateName = self.__eventBattleResultKeys[battleResKey]
                else:
                    templateName = self.__battleResultKeys[battleResKey]
                bgIconSource = None
                arenaUniqueID = battleResults.get('arenaUniqueID', 0)
                if guiType == ARENA_GUI_TYPE.FORT_BATTLE:
                    bgIconSource = 'FORT_BATTLE'
                formatted = g_settings.msgTemplates.format(templateName, ctx=ctx, data={'timestamp': arenaCreateTime,
                 'savedData': arenaUniqueID}, bgIconSource=bgIconSource)
                settings = self._getGuiSettings(message, templateName)
                settings.showAt = BigWorld.time()
                callback((formatted, settings))
            else:
                callback((None, None))
        else:
            callback((None, None))
        return

    def __makeFortResourceString(self, battleResult):
        fortResource = battleResult.get('fortResource', None)
        if fortResource is None:
            return ''
        else:
            fortResourceStr = BigWorld.wg_getIntegralFormat(fortResource) if not battleResult['isLegionary'] else '-'
            return g_settings.htmlTemplates.format('battleResultFortResource', ctx={'fortResource': fortResourceStr})

    def __makeQuestsAchieve(self, message):
        fmtMsg = TokenQuestsFormatter(asBattleFormatter=True)._formatQuestAchieves(message)
        return g_settings.htmlTemplates.format('battleQuests', {'achieves': fmtMsg}) if fmtMsg is not None else ''

    def __makeClubString(self, battleResult):
        result = []
        club = battleResult.get('club')
        if club:
            curDiv, prevDiv = club.get('divisions', (0, 0))
            curLeague, prevLeague = getLeagueByDivision(curDiv), getLeagueByDivision(prevDiv)
            curRating, prevRating = map(ladderRating, club.get('ratings', ((0, 0), (0, 0))))
            if curRating != prevRating:
                if curRating > prevRating:
                    tplKey = 'battleResultClubRatingUp'
                else:
                    tplKey = 'battleResultClubRatingDown'
                result.append(g_settings.htmlTemplates.format(tplKey, ctx={'rating': abs(curRating - prevRating)}))
            if curDiv != prevDiv:
                result.append(g_settings.htmlTemplates.format('battleResultClubNewDivision', ctx={'division': getDivisionString(curDiv)}))
            if curLeague != prevLeague:
                result.append(g_settings.htmlTemplates.format('battleResultClubNewLeague', ctx={'league': getLeagueString(curLeague)}))
        return ''.join(result)

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
            exStrings.append(self.__i18n_penalty % BigWorld.wg_getIntegralFormat(xpPenalty))
        if battleResKey == 1:
            xpFactorStrings = []
            xpFactor = battleResults.get('dailyXPFactor', 1)
            if xpFactor > 1:
                xpFactorStrings.append(i18n.makeString('#%s:serviceChannelMessages/battleResults/doubleXpFactor' % MESSENGER_I18N_FILE) % xpFactor)
            if xpFactorStrings:
                exStrings.append(', '.join(xpFactorStrings))
        return ' ({0:s})'.format('; '.join(exStrings)) if len(exStrings) else ''

    def __makeCreditsExString(self, accCredits, creditsPenalty, creditsContributionIn, creditsContributionOut):
        if not accCredits:
            return ''
        exStrings = []
        penalty = sum([creditsPenalty, creditsContributionOut])
        if penalty > 0:
            exStrings.append(self.__i18n_penalty % BigWorld.wg_getIntegralFormat(penalty))
        if creditsContributionIn > 0:
            exStrings.append(self.__i18n_contribution % BigWorld.wg_getIntegralFormat(creditsContributionIn))
        return ' ({0:s})'.format('; '.join(exStrings)) if len(exStrings) else ''

    def __makeGoldString(self, gold):
        return '' if not gold else g_settings.htmlTemplates.format(self.__goldTemplateKey, {'gold': BigWorld.wg_getGoldFormat(gold)})

    @classmethod
    def __makeAchievementsString(cls, popUpRecords, marksOfMastery):
        result = []
        for recordIdx, value in popUpRecords:
            recordName = DB_ID_TO_RECORD[recordIdx]
            if recordName in IGNORED_BY_BATTLE_RESULTS:
                continue
            achieve = getAchievementFactory(recordName).create(value=value)
            if achieve is not None and not achieve.isApproachable() and achieve not in result:
                result.append(achieve)

        for markOfMastery in marksOfMastery:
            achieve = getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, 'markOfMastery')).create(value=markOfMastery)
            if achieve is not None:
                result.append(achieve)

        res = ''
        if len(result):
            res = g_settings.htmlTemplates.format('battleResultAchieves', {'achieves': ', '.join(map(lambda a: a.getUserName(), sorted(result)))})
        return res


class AutoMaintenanceFormatter(ServiceChannelFormatter):
    __messages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairError',
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadError',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipError'},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSuccess',
                                  AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSuccess',
                                  AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSuccess'},
     AUTO_MAINTENANCE_RESULT.NOT_PERFORMED: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairSkipped',
                                             AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadSkipped',
                                             AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipSkipped'},
     AUTO_MAINTENANCE_RESULT.DISABLED_OPTION: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadDisabledOption',
                                               AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipDisabledOption'},
     AUTO_MAINTENANCE_RESULT.NO_WALLET_SESSION: {AUTO_MAINTENANCE_TYPE.REPAIR: '#messenger:serviceChannelMessages/autoRepairErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: '#messenger:serviceChannelMessages/autoLoadErrorNoWallet',
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: '#messenger:serviceChannelMessages/autoEquipErrorNoWallet'}}
    __currencyTemplates = {Currency.CREDITS: 'PurchaseForCreditsSysMessage',
     Currency.GOLD: 'PurchaseForGoldSysMessage'}

    def isNotify(self):
        return True

    def format(self, message, *args):
        vehicleCompDescr = message.data.get('vehTypeCD', None)
        result = message.data.get('result', None)
        typeID = message.data.get('typeID', None)
        cost = Money(*message.data.get('cost', ()))
        if vehicleCompDescr is not None and result is not None and typeID is not None:
            vt = vehicles_core.getVehicleType(vehicleCompDescr)
            if typeID == AUTO_MAINTENANCE_TYPE.REPAIR:
                formatMsgType = 'RepairSysMessage'
            else:
                formatMsgType = self._getTemplateByCurrency(cost.getCurrency())
            msg = i18n.makeString(self.__messages[result][typeID]) % getUserName(vt)
            priorityLevel = NotificationPriorityLevel.MEDIUM
            if result == AUTO_MAINTENANCE_RESULT.OK:
                priorityLevel = NotificationPriorityLevel.LOW
                templateName = formatMsgType
            elif result == AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS:
                templateName = 'ErrorSysMessage'
            else:
                templateName = 'WarningSysMessage'
            if result == AUTO_MAINTENANCE_RESULT.OK:
                msg += shared_fmts.formatPrice(cost.toAbs())
            formatted = g_settings.msgTemplates.format(templateName, {'text': msg})
            return (formatted, self._getGuiSettings(message, priorityLevel=priorityLevel))
        else:
            return (None, None)
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
        achievesList = list()
        achieves = message.data.get('popUpRecords')
        if achieves is not None:
            achievesList.extend([ i18n.makeString('#achievements:{0[1]:s}'.format(name)) for name in achieves ])
        rares = [ rareID for rareID in message.data.get('rareAchievements', []) if rareID > 0 ]
        raresList = yield _processRareAchievements(rares)
        achievesList.extend(raresList)
        if not len(achievesList):
            callback((None, None))
            return
        else:
            formatted = g_settings.msgTemplates.format('achievementReceived', {'achieves': ', '.join(achievesList)})
            callback((formatted, self._getGuiSettings(message, 'achievementReceived')))
            return


class GoldReceivedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        gold = data.get('gold', None)
        transactionTime = data.get('date', None)
        if gold and transactionTime:
            formatted = g_settings.msgTemplates.format('goldReceived', {'date': TimeFormatter.getLongDatetimeFormat(transactionTime),
             'gold': BigWorld.wg_getGoldFormat(account_helpers.convertGold(gold))})
            return (formatted, self._getGuiSettings(message, 'goldReceived'))
        else:
            return (None, None)
            return


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
                return (formatted, self._getGuiSettings(message, templateKey))
        return (None, None)

    def __formatMoneyGiftMsg(self, keys, data):
        accCredits = data.get('credits', 0)
        gold = data.get('gold', 0)
        result = (None, '')
        ctx = {}
        idx = 0
        if accCredits > 0:
            idx |= 1
            ctx['credits'] = BigWorld.wg_getIntegralFormat(accCredits)
        if gold > 0:
            idx |= 2
            ctx['gold'] = BigWorld.wg_getGoldFormat(gold)
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
             'itemName': vehicles_core.getDictDescr(itemCompactDesc)['userString'],
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
     INVOICE_ASSET.PREMIUM: '_formatAmount',
     INVOICE_ASSET.FREE_XP: '_formatAmount',
     INVOICE_ASSET.DATA: '_formatData'}
    __operationTemplateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpAccruedInvoiceReceived',
     INVOICE_ASSET.GOLD | 16: 'goldDebitedInvoiceReceived',
     INVOICE_ASSET.CREDITS | 16: 'creditsDebitedInvoiceReceived',
     INVOICE_ASSET.PREMIUM | 16: 'premiumDebitedInvoiceReceived',
     INVOICE_ASSET.FREE_XP | 16: 'freeXpDebitedInvoiceReceived'}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: 'goldInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: 'dataInvoiceReceived'}
    __i18nPiecesString = i18n.makeString('#{0:s}:serviceChannelMessages/invoiceReceived/pieces'.format(MESSENGER_I18N_FILE))
    __i18nCrewString = i18n.makeString('#{0:s}:serviceChannelMessages/invoiceReceived/crewOnVehicle'.format(MESSENGER_I18N_FILE))
    __i18nCrewWithLvlDroppedString = i18n.makeString('#{0:s}:serviceChannelMessages/invoiceReceived/crewWithLvlDroppedToBarracks'.format(MESSENGER_I18N_FILE))
    __i18nCrewDroppedString = i18n.makeString('#{0:s}:serviceChannelMessages/invoiceReceived/crewDroppedToBarracks'.format(MESSENGER_I18N_FILE))
    __i18nCrewWithdrawnString = i18n.makeString('#{0:s}:serviceChannelMessages/invoiceReceived/crewWithdrawn'.format(MESSENGER_I18N_FILE))

    def _getMessageTemplateKey(self, assetType):
        return self.__messageTemplateKeys[assetType]

    def _getOperationTimeString(self, data):
        operationTime = data.get('at', None)
        if operationTime:
            fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
        else:
            fDatetime = 'N/A'
        return fDatetime

    def __getFinOperationString(self, assetType, amount):
        templateKey = 0 if amount > 0 else 16
        templateKey |= assetType
        ctx = {}
        if assetType == INVOICE_ASSET.GOLD:
            ctx['amount'] = BigWorld.wg_getGoldFormat(abs(amount))
        else:
            ctx['amount'] = BigWorld.wg_getIntegralFormat(abs(amount))
        return g_settings.htmlTemplates.format(self.__operationTemplateKeys[templateKey], ctx=ctx)

    def __getItemsString(self, items):
        accrued = []
        debited = []
        for itemCompactDescr, count in items.iteritems():
            if count:
                try:
                    item = vehicles_core.getDictDescr(itemCompactDescr)
                    itemString = '{0:s} "{1:s}" - {2:d} {3:s}'.format(getTypeInfoByName(item['itemTypeName'])['userString'], item['userString'], abs(count), self.__i18nPiecesString)
                    if count > 0:
                        accrued.append(itemString)
                    else:
                        debited.append(itemString)
                except:
                    LOG_ERROR('itemCompactDescr can not parse ', itemCompactDescr)
                    LOG_CURRENT_EXCEPTION()

        result = ''
        if len(accrued):
            result = g_settings.htmlTemplates.format('itemsAccruedInvoiceReceived', ctx={'items': ', '.join(accrued)})
        if len(debited):
            if len(result):
                result += '<br/>'
            result += g_settings.htmlTemplates.format('itemsDebitedInvoiceReceived', ctx={'items': ', '.join(debited)})
        return result

    @classmethod
    def __getVehicleInfo(cls, vehData, isWithdrawn):
        vInfo = []
        if isWithdrawn:
            toBarracks = not vehData.get('dismissCrew', False)
            action = cls.__i18nCrewDroppedString if toBarracks else cls.__i18nCrewWithdrawnString
            vInfo.append(action)
        else:
            if 'rent' in vehData:
                time = vehData['rent'].get('time', None)
                rentDays = None
                if time:
                    if time == float('inf'):
                        pass
                    elif time <= time_utils.DAYS_IN_YEAR:
                        rentDays = time
                if rentDays:
                    rentDays = g_settings.htmlTemplates.format('rentDays', {'value': str(rentDays)})
                    vInfo.append(rentDays)
            crewLevel = calculateRoleLevel(vehData.get('crewLvl', 50), vehData.get('crewFreeXP', 0))
            if crewLevel > 50:
                if not vehData.get('dismissCrew', False) and ('crewFreeXP' in vehData or 'crewLvl' in vehData or 'tankmen' in vehData):
                    crewWithLevelString = cls.__i18nCrewWithLvlDroppedString % crewLevel
                else:
                    crewWithLevelString = cls.__i18nCrewString % crewLevel
                vInfo.append(crewWithLevelString)
        return '; '.join(vInfo)

    @classmethod
    def __getVehicleName(cls, vehCompDescr):
        vehicleName = None
        try:
            if vehCompDescr < 0:
                vehCompDescr = abs(vehCompDescr)
            vehicleName = getUserName(vehicles_core.getVehicleType(vehCompDescr))
        except:
            LOG_ERROR('Wrong vehicle compact descriptor', vehCompDescr)
            LOG_CURRENT_EXCEPTION()

        return vehicleName

    @classmethod
    def _getVehicleNames(cls, vehicles):
        addVehNames = []
        removeVehNames = []
        rentedVehNames = []
        for vehCompDescr, vehData in vehicles.iteritems():
            if 'customCompensation' in vehData:
                continue
            isNegative = False
            if type(vehCompDescr) is types.IntType:
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
    def _getVehiclesString(cls, vehicles, htmlTplPostfix='InvoiceReceived'):
        addVehNames, removeVehNames, rentedVehNames = cls._getVehicleNames(vehicles)
        result = []
        if len(addVehNames):
            result.append(g_settings.htmlTemplates.format('vehiclesAccrued' + htmlTplPostfix, ctx={'vehicles': ', '.join(addVehNames)}))
        if len(removeVehNames):
            result.append(g_settings.htmlTemplates.format('vehiclesDebited' + htmlTplPostfix, ctx={'vehicles': ', '.join(removeVehNames)}))
        if len(rentedVehNames):
            result.append(g_settings.htmlTemplates.format('vehiclesRented' + htmlTplPostfix, ctx={'vehicles': ', '.join(rentedVehNames)}))
        return '<br/>'.join(result)

    @classmethod
    def _getComptnString(cls, vehicles, htmlTplPostfix='InvoiceReceived'):
        html = g_settings.htmlTemplates
        result = []
        for vehCompDescr, vehData in vehicles.iteritems():
            vehicleName = cls.__getVehicleName(vehCompDescr)
            if vehicleName is None:
                continue
            if 'rentCompensation' in vehData:
                comp = Money(*vehData['rentCompensation'])
                currency = comp.getCurrency(byWeight=True)
                formatter = getBWFormatter(currency)
                key = '{}RentCompensationReceived'.format(currency)
                ctx = {currency: formatter(comp.get(currency)),
                 'vehicleName': vehicleName}
                result.append(html.format(key, ctx=ctx))
            if 'customCompensation' in vehData:
                itemNames = [vehicleName]
                comp = Money(*vehData['customCompensation'])
                values = []
                currencies = comp.getSetCurrencies(byWeight=True)
                for currency in currencies:
                    formatter = getBWFormatter(currency)
                    key = '{}Compensation'.format(currency)
                    values.append(html.format(key + htmlTplPostfix, ctx={'amount': formatter(comp.get(currency))}))

                if len(values):
                    result.append(html.format('compensationFor' + htmlTplPostfix, ctx={'items': ', '.join(itemNames),
                     'compensation': ', '.join(values)}))

        return '<br/>'.join(result)

    @classmethod
    def _getTankmenString(cls, tmen):
        tmanUserStrings = []
        for tmanData in tmen:
            try:
                if isinstance(tmanData, dict):
                    tankman = Tankman(tmanData['tmanCompDescr'])
                else:
                    tankman = Tankman(tmanData)
                tmanUserStrings.append('{0:s} {1:s} ({2:s}, {3:s}, {4:d}%)'.format(tankman.rankUserName, tankman.lastUserName, tankman.roleUserName, getUserName(tankman.vehicleNativeDescr.type), tankman.roleLevel))
            except:
                LOG_ERROR('Wrong tankman data', tmanData)
                LOG_CURRENT_EXCEPTION()

        result = ''
        if len(tmanUserStrings):
            result = g_settings.htmlTemplates.format('tankmenInvoiceReceived', ctx={'tankman': ', '.join(tmanUserStrings)})
        return result

    @classmethod
    def _getGoodiesString(cls, goodies):
        result = []
        boostersStrings = []
        discountsStrings = []
        for goodieID, ginfo in goodies.iteritems():
            if goodieID in g_itemsCache.items.shop.boosters:
                booster = g_goodiesCache.getBooster(goodieID)
                if booster is not None and booster.enabled:
                    boostersStrings.append(booster.userName)
            discount = g_goodiesCache.getDiscount(goodieID)
            if discount is not None and discount.enabled:
                discountsStrings.append(discount.description)

        if len(boostersStrings):
            result.append(g_settings.htmlTemplates.format('boostersInvoiceReceived', ctx={'boosters': ', '.join(boostersStrings)}))
        if len(discountsStrings):
            result.append(g_settings.htmlTemplates.format('discountsInvoiceReceived', ctx={'discounts': ', '.join(discountsStrings)}))
        return '; '.join(result)

    @classmethod
    def _getChristmasToyString(cls, tokens):
        accuredToys = defaultdict(lambda : 0)
        debitedToys = defaultdict(lambda : 0)
        accruedToysStr = []
        newToys = {}
        debitedToysStr = []
        from gui.christmas.christmas_controller import g_christmasCtrl
        for tokenID, tInfo in tokens.iteritems():
            toyID = g_christmasCtrl.getToyID(tokenID)
            count = tInfo.get('count', 0)
            christmasItemInfo = g_christmasCtrl.getChristmasItemInfo(toyID, count)
            if christmasItemInfo is not None:
                if count > 0:
                    newToys[toyID] = count
                    accuredToys[christmasItemInfo.item.guiType] += count
                else:
                    debitedToys[christmasItemInfo.item.guiType] += abs(count)

        g_christmasCtrl.addNewToysToAccountSettings(newToys)
        for guiType, count in accuredToys.iteritems():
            guiTypeName = i18n.makeString('#christmas:toyType/%s' % guiType)
            if count > 0:
                accruedToysStr.append(i18n.makeString('#christmas:bonus/toy', name=guiTypeName, count=count))

        for guiType, count in debitedToys.iteritems():
            guiTypeName = i18n.makeString('#christmas:toyType/%s' % guiType)
            if count > 0:
                debitedToysStr.append(i18n.makeString('#christmas:bonus/toy', name=guiTypeName, count=count))

        result = []
        if len(accruedToysStr):
            result.append(g_settings.htmlTemplates.format('toysInvoiceReceived', ctx={'toys': ', '.join(accruedToysStr)}))
        if len(debitedToysStr):
            result.append(g_settings.htmlTemplates.format('toysDebitedReceived', ctx={'toys': ', '.join(debitedToysStr)}))
        return '<br/>'.join(result)

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

    @async
    @process
    def __prerocessRareAchievements(self, data, callback):
        yield lambda callback: callback(True)
        dossiers = data.get('data', {}).get('dossier', {})
        if dossiers:
            self.__dossierResult = []
            rares = [ rec['value'] for d in dossiers.itervalues() for (blck, _), rec in d.iteritems() if blck == ACHIEVEMENT_BLOCK.RARE ]
            addDossierStrings = [ i18n.makeString('#achievements:{0:s}'.format(name)) for rec in dossiers.itervalues() for _, name in rec if name != '' ]
            addDossiers = [ rare for rare in rares if rare > 0 ]
            if addDossiers:
                addDossierStrings += (yield _processRareAchievements(addDossiers))
            if addDossierStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersAccruedInvoiceReceived', ctx={'dossiers': ', '.join(addDossierStrings)}))
            delDossiers = [ abs(rare) for rare in rares if rare < 0 ]
            if delDossiers:
                delDossierStrings = yield _processRareAchievements(delDossiers)
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersDebitedInvoiceReceived', ctx={'dossiers': ', '.join(delDossierStrings)}))
        callback(True)

    def __getDossierString(self):
        return '<br/>'.join(self.__dossierResult)

    def __getL10nDescription(self, data):
        descr = ''
        lData = getLocalizedData(data.get('data', {}), 'localized_description', defVal=None)
        if lData:
            descr = i18n.encodeUtf8(html.escape(lData.get('description', u'')))
            if len(descr):
                descr = '<br/>' + descr
        return descr

    @classmethod
    def _processCompensations(cls, data):
        vehicles = data.get('vehicles')
        comp = ZERO_MONEY
        if vehicles is not None:
            for value in vehicles.itervalues():
                if 'rentCompensation' in value:
                    comp += Money(*value['rentCompensation'])
                if 'customCompensation' in value:
                    comp += Money(*value['customCompensation'])

        if 'gold' in data:
            data['gold'] -= comp.gold
            if data['gold'] == 0:
                del data['gold']
        if 'credits' in data:
            data['credits'] -= comp.credits
            if data['credits'] == 0:
                del data['credits']
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
            gold = dataEx.get('gold')
            if gold is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.GOLD, gold))
            accCredtis = dataEx.get('credits')
            if accCredtis is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.CREDITS, accCredtis))
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
            if vehicles:
                result = self._getVehiclesString(vehicles)
                if len(result):
                    operations.append(result)
                comptnStr = self._getComptnString(vehicles)
                if len(comptnStr):
                    operations.append(comptnStr)
                for v in vehicles.itervalues():
                    tmen.extend(v.get('tankmen', []))

            if tmen:
                operations.append(self._getTankmenString(tmen))
            slots = dataEx.get('slots')
            if slots:
                operations.append(self.__getSlotsString(slots))
            berths = dataEx.get('berths')
            if berths:
                operations.append(self.__getBerthsString(berths))
            goodies = dataEx.get('goodies', {})
            if goodies:
                strGoodies = self._getGoodiesString(goodies)
                if strGoodies:
                    operations.append(strGoodies)
            dossier = dataEx.get('dossier', {})
            if dossier:
                operations.append(self.__getDossierString())
            tokens = dataEx.get('tokens', {})
            if tokens is not None and len(tokens) > 0:
                toysString = self._getChristmasToyString(tokens)
                if toysString:
                    operations.append(toysString)
            _extendCustomizationData(dataEx, operations)
            return operations

    def _formatData(self, assetType, data):
        operations = self._composeOperations(data)
        return None if not operations else g_settings.msgTemplates.format(self._getMessageTemplateKey(assetType), ctx={'at': self._getOperationTimeString(data),
         'desc': self.__getL10nDescription(data),
         'op': '<br/>'.join(operations)})

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data
            yield self.__prerocessRareAchievements(data)
            assetType = data.get('assetType', -1)
            handler = self.__assetHandlers.get(assetType)
            if handler is not None:
                formatted = getattr(self, handler)(assetType, data)
            if formatted is not None:
                settings = self._getGuiSettings(message, self._getMessageTemplateKey(assetType))
        callback((formatted, settings))
        return


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
            return (formatted, self._getGuiSettings(message, 'adminMessage'))
        else:
            return (None, None)
            return None


class AccountTypeChangedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        result = (None, None)
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
            result = (formatted, self._getGuiSettings(message, templateKey))
        return result


class PremiumActionFormatter(ServiceChannelFormatter):
    _templateKey = None

    def _getMessage(self, isPremium, expiryTime):
        return None

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        return (self._getMessage(isPremium, expiryTime), self._getGuiSettings(message, self._templateKey)) if isPremium is not None else (None, None)


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
        if data.has_key('localized_data') and len(data['localized_data']):
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
        first = i18n.encodeUtf8(opponents.get('1', {}).get('name', ''))
        second = i18n.encodeUtf8(opponents.get('2', {}).get('name', ''))
        result = ''
        if len(first) > 0 and len(second) > 0:
            result = g_settings.htmlTemplates.format('prebattleOpponents', ctx={'first': html.escape(first),
             'second': html.escape(second)})
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
            return
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
            return (formatted, self._getGuiSettings(message, 'prebattleArenaFinish'))


class PrebattleKickFormatter(PrebattleFormatter):

    def format(self, message, *args):
        data = message.data
        result = (None, None)
        prbType = data.get('type')
        kickReason = data.get('kickReason')
        if prbType > 0 and kickReason > 0:
            ctx = {}
            key = '#system_messages:prebattle/kick/type/unknown'
            if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
                key = '#system_messages:prebattle/kick/type/squad'
            elif prbType == PREBATTLE_TYPE.COMPANY:
                key = '#system_messages:prebattle/kick/type/team'
            ctx['type'] = i18n.makeString(key)
            kickName = KICK_REASON_NAMES[kickReason]
            key = '#system_messages:prebattle/kick/reason/{0:s}'.format(kickName)
            ctx['reason'] = i18n.makeString(key)
            formatted = g_settings.msgTemplates.format('prebattleKick', ctx=ctx)
            result = (formatted, self._getGuiSettings(message, 'prebattleKick'))
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
            return (None, None)
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
            return (formatted, self._getGuiSettings(message, 'prebattleDestruction'))


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
        return (formatted, self._getGuiSettings(message, 'vehCamouflageTimedOut'))


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
        return (formatted, self._getGuiSettings(message, 'vehEmblemTimedOut'))


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
        return (formatted, self._getGuiSettings(message, 'vehInscriptionTimedOut'))


class ConverterFormatter(ServiceChannelFormatter):

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
        vehicles = data.get('vehicles')
        if vehicles:
            vehiclesReceived = [ self.__vehName(cd) for cd in vehicles if cd > 0 and g_itemsCache.items.doesVehicleExist(cd) ]
            if len(vehiclesReceived):
                text.append(self.__i18nValue('vehicles', True, vehicles=', '.join(vehiclesReceived)))
            vehiclesWithdrawn = [ self.__vehName(cd) for cd in vehicles if cd < 0 and g_itemsCache.items.doesVehicleExist(abs(cd)) ]
            if len(vehiclesWithdrawn):
                text.append(self.__i18nValue('vehicles', False, vehicles=', '.join(vehiclesWithdrawn)))
        slots = data.get('slots')
        if slots:
            text.append(self.__i18nValue('slots', slots > 0, slots=BigWorld.wg_getIntegralFormat(abs(slots))))
        gold = data.get('gold')
        if gold:
            text.append(self.__i18nValue('gold', gold > 0, gold=BigWorld.wg_getGoldFormat(abs(gold))))
        accCredits = data.get('credits')
        if accCredits:
            text.append(self.__i18nValue('credits', accCredits > 0, credits=BigWorld.wg_getIntegralFormat(abs(accCredits))))
        freeXP = data.get('freeXP')
        if freeXP:
            text.append(self.__i18nValue('freeXP', freeXP > 0, freeXP=BigWorld.wg_getIntegralFormat(abs(freeXP))))
        formatted = g_settings.msgTemplates.format('ConverterNotify', {'text': '<br/>'.join(text)})
        return (formatted, self._getGuiSettings(message, 'ConverterNotify'))


class ClientSysMessageFormatter(ServiceChannelFormatter):
    __templateKey = '%sSysMessage'

    def format(self, data, *args):
        if len(args):
            msgType = args[0][0]
        else:
            msgType = 'Error'
        templateKey = self.__templateKey % msgType
        formatted = g_settings.msgTemplates.format(templateKey, ctx={'text': data})
        return (formatted, self._getGuiSettings(args, templateKey))

    def _getGuiSettings(self, data, key=None, priorityLevel=None):
        if type(data) is types.TupleType and len(data):
            auxData = data[0][:]
            if len(data[0]) > 1 and priorityLevel is None:
                priorityLevel = data[0][1]
        else:
            auxData = []
        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData)


class PremiumAccountExpiryFormatter(ClientSysMessageFormatter):

    def format(self, data, *args):
        formatted = g_settings.msgTemplates.format('durationOfPremiumAccountExpires', ctx={'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(data))})
        return (formatted, self._getGuiSettings(args, 'durationOfPremiumAccountExpires'))


class AOGASNotifyFormatter(ClientSysMessageFormatter):

    def format(self, data, *args):
        formatted = g_settings.msgTemplates.format('AOGASNotify', {'text': i18n.makeString('#AOGAS:{0:s}'.format(data.name()))})
        return (formatted, self._getGuiSettings(args, 'AOGASNotify'))


class VehicleTypeLockExpired(ServiceChannelFormatter):

    def format(self, message, *args):
        result = (None, None)
        if message.data:
            ctx = {}
            vehTypeCompDescr = message.data.get('vehTypeCompDescr')
            if vehTypeCompDescr is None:
                templateKey = 'vehiclesAllLockExpired'
            else:
                templateKey = 'vehicleLockExpired'
                ctx['vehicleName'] = getUserName(vehicles_core.getVehicleType(vehTypeCompDescr))
            formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
            result = (formatted, self._getGuiSettings(message, 'vehicleLockExpired'))
        return result


class ServerDowntimeCompensation(ServiceChannelFormatter):
    __templateKey = 'serverDowntimeCompensation'

    def format(self, message, *args):
        result = (None, None)
        subjects = ''
        data = message.data
        if data is not None:
            for key, value in data.items():
                if value:
                    if len(subjects) > 0:
                        subjects += ', '
                    subjects += i18n.makeString('#%s:serviceChannelMessages/' % MESSENGER_I18N_FILE + self.__templateKey + '/' + key)

            if len(subjects) > 0:
                formatted = g_settings.msgTemplates.format(self.__templateKey, ctx={'text': i18n.makeString('#%s:serviceChannelMessages/' % MESSENGER_I18N_FILE + self.__templateKey) % subjects})
                result = (formatted, self._getGuiSettings(message, self.__templateKey))
        return result


class ActionNotificationFormatter(ClientSysMessageFormatter):
    __templateKey = 'action%s'

    def format(self, message, *args):
        result = (None, None)
        data = message.get('data')
        if data:
            templateKey = self.__templateKey % message.get('state', '')
            formatted = g_settings.msgTemplates.format(templateKey, ctx={'text': data}, data={'icon': message.get('type', '')})
            result = (formatted, self._getGuiSettings(args, templateKey))
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
             'credits': '0'}
            freeXP = 0
            credits_ = 0
            chapters = data.get('chapters', [])
            for chapter in chapters:
                if chapter.get('received', False):
                    bonus = chapter.get('bonus', {})
                    freeXP += bonus.get('freeXP', 0)
                    credits_ += bonus.get('credits', 0)

            if freeXP:
                ctx['freeXP'] = BigWorld.wg_getIntegralFormat(freeXP)
            if credits_:
                ctx['credits'] = BigWorld.wg_getIntegralFormat(credits_)
            all_ = data.get('areAllBonusesReceived', False)
            if all_ and credits_ <= 0 and freeXP <= 0:
                key = self.__resultKeyWoBonuses
            else:
                key = self.__resultKeyWithBonuses
            startedAtTime = data.get('startedAt', time.time())
            formatted = g_settings.msgTemplates.format(key, ctx=ctx, data={'timestamp': startedAtTime,
             'savedData': data.get('arenaUniqueID', 0)})
            return (formatted, self._getGuiSettings(args, key))
        else:
            return (None, None)
            return


class TokenQuestsFormatter(WaitItemsSyncFormatter):

    def __init__(self, asBattleFormatter=False):
        super(TokenQuestsFormatter, self).__init__()
        self._asBattleFormatter = asBattleFormatter

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data or {}
            completedQuestIDs = data.get('completedQuestIDs', set())
            fmt = self._formatQuestAchieves(message)
            if fmt:
                settings = self._getGuiSettings(message, self._getTemplateName(completedQuestIDs))
                formatted = g_settings.msgTemplates.format(self._getTemplateName(completedQuestIDs), {'achieves': fmt})
        callback((formatted, settings))
        return None

    def _getTemplateName(self, completedQuestIDs=set()):
        if len(completedQuestIDs):
            for qID in completedQuestIDs:
                if potapov_quests.g_cache.isPotapovQuest(qID):
                    return 'potapovQuests'

    def _formatQuestAchieves(self, message):
        data = message.data
        result = []
        if not self._asBattleFormatter:
            gold = data.get('gold', 0)
            if gold:
                result.append(self.__makeQuestsAchieve('battleQuestsGold', gold=BigWorld.wg_getIntegralFormat(gold)))
        premium = data.get('premium', 0)
        if premium:
            result.append(self.__makeQuestsAchieve('battleQuestsPremium', days=premium))
        if not self._asBattleFormatter:
            freeXP = data.get('freeXP', 0)
            if freeXP:
                result.append(self.__makeQuestsAchieve('battleQuestsFreeXP', freeXP=BigWorld.wg_getIntegralFormat(freeXP)))
        tokens = data.get('tokens', {})
        if tokens is not None and len(tokens) > 0:
            result.append(InvoiceReceivedFormatter._getChristmasToyString(tokens))
        vehiclesList = data.get('vehicles', [])
        for vehiclesData in vehiclesList:
            if vehiclesData is not None and len(vehiclesData) > 0:
                msg = InvoiceReceivedFormatter._getVehiclesString(vehiclesData, htmlTplPostfix='QuestsReceived')
                if len(msg):
                    result.append(msg)
                comptnStr = InvoiceReceivedFormatter._getComptnString(vehiclesData, htmlTplPostfix='QuestsReceived')
                if len(comptnStr):
                    result.append('<br/>' + comptnStr)

        if not self._asBattleFormatter:
            creditsVal = data.get('credits', 0)
            if creditsVal:
                result.append(self.__makeQuestsAchieve('battleQuestsCredits', credits=BigWorld.wg_getIntegralFormat(creditsVal)))
        slots = data.get('slots', 0)
        if slots:
            result.append(self.__makeQuestsAchieve('battleQuestsSlots', slots=BigWorld.wg_getIntegralFormat(slots)))
        items = data.get('items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemDescr = vehicles_core.getDictDescr(intCD)
            itemsNames.append(i18n.makeString('#messenger:serviceChannelMessages/battleResults/quests/items/name', name=itemDescr['userString'], count=BigWorld.wg_getIntegralFormat(count)))

        if len(itemsNames):
            result.append(self.__makeQuestsAchieve('battleQuestsItems', names=', '.join(itemsNames)))
        _extendCustomizationData(data, result)
        berths = data.get('berths', 0)
        if berths:
            result.append(self.__makeQuestsAchieve('battleQuestsBerths', berths=BigWorld.wg_getIntegralFormat(berths)))
        tmen = data.get('tankmen', {})
        if tmen is not None and len(tmen) > 0:
            result.append(InvoiceReceivedFormatter._getTankmenString(tmen))
        goodies = data.get('goodies', {})
        if goodies is not None and len(goodies) > 0:
            strGoodies = InvoiceReceivedFormatter._getGoodiesString(goodies)
            if strGoodies:
                result.append(strGoodies)
        if not self._asBattleFormatter:
            achieves = data.get('popUpRecords', [])
            achievesNames = set()
            for recordIdx, value in achieves:
                factory = getAchievementFactory(DB_ID_TO_RECORD[recordIdx])
                if factory is not None:
                    a = factory.create(value=int(value))
                    if a is not None:
                        achievesNames.add(a.getUserName())

            if len(achievesNames):
                result.append(self.__makeQuestsAchieve('battleQuestsPopUps', achievements=', '.join(achievesNames)))
        return '<br/>'.join(result) if len(result) else None

    @classmethod
    def __makeQuestsAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)


class NCMessageFormatter(ServiceChannelFormatter):
    __templateKeyFormat = 'notificationsCenterMessage_{0}'

    def format(self, message, *args):
        LOG_DEBUG('Message has received from notification center', message)
        data = z_loads(message.data)
        if not data:
            return (None, None)
        elif 'body' not in data or not data['body']:
            return (None, None)
        else:
            templateKey = self.__getTemplateKey(data)
            priority = self.__getGuiPriority(data)
            topic = self.__getTopic(data)
            body = self.__getBody(data)
            settings = self._getGuiSettings(message, templateKey, priority)
            msgType = data['type']
            if msgType == NC_MESSAGE_TYPE.POLL:
                if not GUI_SETTINGS.isPollEnabled:
                    return (None, None)
                if not self.__fetchPollData(data, settings):
                    return (None, None)
            formatted = g_settings.msgTemplates.format(templateKey, ctx={'topic': topic,
             'body': body})
            return (formatted, settings)

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
        if len(topic):
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
        if type(ctx) is not types.DictType:
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
            return (formatted, settings)
        else:
            return (None, None)
            return None


class FortMessageFormatter(ServiceChannelFormatter):
    __templates = {SYS_MESSAGE_FORT_EVENT.DEF_HOUR_SHUTDOWN: 'fortHightPriorityMessageWarning',
     SYS_MESSAGE_FORT_EVENT.BASE_DESTROYED: 'fortHightPriorityMessageWarning'}
    DEFAULT_WARNING = 'fortMessageWarning'

    def __init__(self):
        super(FortMessageFormatter, self).__init__()
        self.__messagesFormatters = {SYS_MESSAGE_FORT_EVENT.FORT_READY: BoundMethodWeakref(self._simpleMessage),
         SYS_MESSAGE_FORT_EVENT.DEF_HOUR_SHUTDOWN: BoundMethodWeakref(self._simpleMessage),
         SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED: BoundMethodWeakref(self._reserveActivatedMessage),
         SYS_MESSAGE_FORT_EVENT.RESERVE_EXPIRED: BoundMethodWeakref(self._reserveExpiredMessage),
         SYS_MESSAGE_FORT_EVENT.RESERVE_PRODUCED: BoundMethodWeakref(self._reserveProducedMessage),
         SYS_MESSAGE_FORT_EVENT.STORAGE_OVERFLOW: BoundMethodWeakref(self._storageOverflowMessage),
         SYS_MESSAGE_FORT_EVENT.ORDER_CANCELED: BoundMethodWeakref(self._orderCanceledMessage),
         SYS_MESSAGE_FORT_EVENT.REATTACHED_TO_BASE: BoundMethodWeakref(self._reattachedToBaseMessage),
         SYS_MESSAGE_FORT_EVENT.DEF_HOUR_ACTIVATED: BoundMethodWeakref(self._defHourManipulationMessage),
         SYS_MESSAGE_FORT_EVENT.DEF_HOUR_CHANGED: BoundMethodWeakref(self._defHourManipulationMessage),
         SYS_MESSAGE_FORT_EVENT.OFF_DAY_ACTIVATED: BoundMethodWeakref(self._offDayActivatedMessage),
         SYS_MESSAGE_FORT_EVENT.VACATION_STARTED: BoundMethodWeakref(self._vacationActivatedMessage),
         SYS_MESSAGE_FORT_EVENT.VACATION_FINISHED: BoundMethodWeakref(self._vacationFinishedMessage),
         SYS_MESSAGE_FORT_EVENT.PERIPHERY_CHANGED: BoundMethodWeakref(self._peripheryChangedMessage),
         SYS_MESSAGE_FORT_EVENT.BUILDING_DAMAGED: BoundMethodWeakref(self._buildingDamagedMessage),
         SYS_MESSAGE_FORT_EVENT.BASE_DESTROYED: BoundMethodWeakref(self._simpleMessage),
         SYS_MESSAGE_FORT_EVENT.ORDER_COMPENSATED: BoundMethodWeakref(self._orderCompensationMessage),
         SYS_MESSAGE_FORT_EVENT.ATTACK_PLANNED: BoundMethodWeakref(self._attackPlannedMessage),
         SYS_MESSAGE_FORT_EVENT.DEFENCE_PLANNED: BoundMethodWeakref(self._defencePlannedMessage),
         SYS_MESSAGE_FORT_EVENT.BATTLE_DELETED: BoundMethodWeakref(self._battleDeletedMessage),
         SYS_MESSAGE_FORT_EVENT.SPECIAL_ORDER_EXPIRED: BoundMethodWeakref(self._specialReserveExpiredMessage),
         SYS_MESSAGE_FORT_EVENT.RESOURCE_SET: BoundMethodWeakref(self._resourceSetMessage),
         SYS_MESSAGE_FORT_EVENT.RESERVE_SET: BoundMethodWeakref(self._reserveSetMessage),
         SYS_MESSAGE_FORT_EVENT.FORT_GOT_8_LEVEL: BoundMethodWeakref(self._fortGotLvlMessage),
         SYS_MESSAGE_FORT_EVENT.BATTLE_DELETED_LEVEL: BoundMethodWeakref(self._battleDeletedLevelMessage)}

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
                return (formatted, settings)
            LOG_WARNING('FortMessageFormatter has no available formatters for given message type: ', event)
        return (None, None)

    def _buildMessage(self, event, ctx=None):
        if ctx is None:
            ctx = {}
        return i18n.makeString(('#messenger:serviceChannelMessages/fort/%s' % SYS_MESSAGE_FORT_EVENT_NAMES[event]), **ctx)

    def _simpleMessage(self, data):
        return self._buildMessage(data['event'])

    def _peripheryChangedMessage(self, data):
        return self._buildMessage(data['event'], {'peripheryName': g_preDefinedHosts.periphery(data['peripheryID']).name})

    def _reserveActivatedMessage(self, data):
        event = data['event']
        orderTypeID = data['orderTypeID']
        order = fort_fmts.getOrderUserString(data['orderTypeID'])
        if event == SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED and FORT_ORDER_TYPE.isOrderPermanent(orderTypeID):
            return i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_FORT_PERMANENT_RESERVE_ACTIVATED, order=order)
        timeExpiration = shared_fmts.time_formatters.getTimeDurationStr(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(data['timeExpiration'])))
        return self._buildMessage(event, {'order': order,
         'time': timeExpiration})

    def _reserveExpiredMessage(self, data):
        return self._buildMessage(data['event'], {'order': fort_fmts.getOrderUserString(data['orderTypeID'])})

    def _reserveProducedMessage(self, data):
        return self._buildMessage(data['event'], {'order': fort_fmts.getOrderUserString(data['orderTypeID']),
         'count': data['count']})

    def _storageOverflowMessage(self, data):
        return self._buildMessage(data['event'], {'building': fort_fmts.getBuildingUserString(data['buildTypeID'])})

    def _orderCanceledMessage(self, data):
        import fortified_regions
        buildTypeID = data['buildTypeID']
        orderTypeID = fortified_regions.g_cache.buildings[buildTypeID].orderType
        return self._buildMessage(data['event'], {'building': fort_fmts.getBuildingUserString(buildTypeID),
         'order': fort_fmts.getOrderUserString(orderTypeID)})

    def _reattachedToBaseMessage(self, data):
        return self._buildMessage(data['event'], {'building': fort_fmts.getBuildingUserString(FORT_BUILDING_TYPE.MILITARY_BASE)})

    def _defHourManipulationMessage(self, data):
        if data.get('event') == SYS_MESSAGE_FORT_EVENT.DEF_HOUR_ACTIVATED:
            from gui.shared.fortifications.settings import MUST_SHOW_DEFENCE_START
            from gui.shared.fortifications.fort_helpers import setRosterIntroWindowSetting
            setRosterIntroWindowSetting(MUST_SHOW_DEFENCE_START)
        return self._buildMessage(data['event'], {'defenceHour': fort_fmts.getDefencePeriodString(time_utils.getTimeTodayForUTC(data['defenceHour']))})

    def _fortGotLvlMessage(self, data):
        if data.get('event') == SYS_MESSAGE_FORT_EVENT.FORT_GOT_8_LEVEL:
            from gui.shared.fortifications.settings import MUST_SHOW_FORT_UPGRADE
            from gui.shared.fortifications.fort_helpers import setRosterIntroWindowSetting
            setRosterIntroWindowSetting(MUST_SHOW_FORT_UPGRADE)
        return self._simpleMessage(data)

    def _offDayActivatedMessage(self, data):
        offDay = data['offDay']
        if offDay == NOT_ACTIVATED:
            return i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_FORT_NO_OFF_DAY_ACTIVATED)
        if 'defenceHour' in data:
            from gui.shared.fortifications.fort_helpers import adjustOffDayToLocal, adjustDefenceHourToLocal
            offDayLocal = adjustOffDayToLocal(offDay, adjustDefenceHourToLocal(data['defenceHour'])[0])
        else:
            LOG_WARNING('_offDayActivatedMessage: received incorrect data, using offDay without adjustment... ', data)
            offDayLocal = offDay
        return self._buildMessage(data['event'], {'offDay': fort_fmts.getDayOffString(offDayLocal)})

    def _vacationActivatedMessage(self, data):
        return self._buildMessage(data['event'], {'finish': BigWorld.wg_getShortDateFormat(data['timeEnd'])})

    def _vacationFinishedMessage(self, data):
        return self._buildMessage(data['event'])

    def _buildingDamagedMessage(self, data):
        buildTypeID = data['buildTypeID']
        return i18n.makeString('#messenger:serviceChannelMessages/fort/{0}_{1}'.format(SYS_MESSAGE_FORT_EVENT_NAMES[data['event']], FORT_BUILDING_TYPE_NAMES[FORT_BUILDING_TYPE.MILITARY_BASE])) if buildTypeID == FORT_BUILDING_TYPE.MILITARY_BASE else self._buildMessage(data['event'], {'building': fort_fmts.getBuildingUserString(buildTypeID)})

    def _orderCompensationMessage(self, data):
        return self._buildMessage(data['event'], {'orderTypeName': fort_fmts.getOrderUserString(data['orderTypeID'])})

    def _attackPlannedMessage(self, data):
        return self._buildMessage(data['event'], {'clan': getClanAbbrevString(data['defenderClanAbbrev']),
         'date': BigWorld.wg_getShortDateFormat(data['timeAttack']),
         'time': BigWorld.wg_getShortTimeFormat(data['timeAttack'])})

    def _defencePlannedMessage(self, data):
        return self._buildMessage(data['event'], {'clan': getClanAbbrevString(data['attackerClanAbbrev']),
         'date': BigWorld.wg_getShortDateFormat(data['timeAttack']),
         'time': BigWorld.wg_getShortTimeFormat(data['timeAttack'])})

    def _battleDeletedMessage(self, data):
        return self._buildMessage(data['event'], {'clan': getClanAbbrevString(data['enemyClanAbbrev'])})

    def _battleDeletedLevelMessage(self, data):
        return self._buildMessage(data['event'], {'clan': getClanAbbrevString(data['enemyClanAbbrev']),
         'date': BigWorld.wg_getShortDateFormat(data['timeAttack']),
         'time': BigWorld.wg_getShortTimeFormat(data['timeAttack'])})

    def _specialReserveExpiredMessage(self, data):
        resInc, resDec = data['resBonus']
        resTotal = resInc - resDec
        orderTypeID = data['orderTypeID']
        messageKey = '#messenger:serviceChannelMessages/fort/SPECIAL_ORDER_EXPIRED_%s' % constants.FORT_ORDER_TYPE_NAMES[orderTypeID]
        additional = ''
        if resDec:
            additional = i18n.makeString('%s_ADDITIONAL' % messageKey, resInc=BigWorld.wg_getIntegralFormat(resInc), resDec=BigWorld.wg_getIntegralFormat(resDec))
        return i18n.makeString(messageKey, additional=additional, resTotal=BigWorld.wg_getIntegralFormat(resTotal))

    def _resourceSetMessage(self, data):
        try:
            resourceDelta = data['resourceDelta']
            if resourceDelta > 0:
                messageKey = MESSENGER.SERVICECHANNELMESSAGES_FORT_PROM_RESOURCE_EARNED
            else:
                messageKey = MESSENGER.SERVICECHANNELMESSAGES_FORT_PROM_RESOURCE_WITHDRAWN
            return i18n.makeString(messageKey, promresource=abs(resourceDelta))
        except:
            LOG_CURRENT_EXCEPTION()

    def _reserveSetMessage(self, data):
        try:
            reserveDelta = data['reserveDelta']
            if reserveDelta > 0:
                messageKey = MESSENGER.SERVICECHANNELMESSAGES_FORT_RESERVES_EARNED
            else:
                messageKey = MESSENGER.SERVICECHANNELMESSAGES_FORT_RESERVES_WITHDRAWN
            return i18n.makeString(messageKey, reserves=abs(reserveDelta))
        except:
            LOG_CURRENT_EXCEPTION()


class FortBattleResultsFormatter(ServiceChannelFormatter):
    __battleResultKeys = {-1: 'battleFortDefeatResult',
     0: 'battleFortDrawGameResult',
     1: 'battleFortVictoryResult'}

    def isNotify(self):
        return True

    def format(self, message, *args):
        battleResult = message.data
        if battleResult:
            enemyClanAbbrev = battleResult.get('enemyClanName', '')
            winnerCode = battleResult['isWinner']
            if winnerCode == 0 and battleResult['attackResult'] == FORT_ATTACK_RESULT.TECHNICAL_DRAW:
                winnerCode = -1
                battleResult['isWinner'] = winnerCode
            resourceKey = 'fortResourceCaptureByClan' if winnerCode > 0 else 'fortResourceLostByClan'
            ctx = {'enemyClanAbbrev': getClanAbbrevString(enemyClanAbbrev),
             'resourceClan': BigWorld.wg_getIntegralFormat(battleResult.get(resourceKey, 0)),
             'resourcePlayer': BigWorld.wg_getIntegralFormat(battleResult.get('fortResource', 0))}
            ctx['achieves'] = self._makeAchievementsString(battleResult)
            templateName = self.__battleResultKeys[winnerCode]
            settings = self._getGuiSettings(message, templateName)
            settings.setCustomEvent(MsgCustomEvents.FORT_BATTLE_FINISHED, battleResult.get('battleID'))
            formatted = g_settings.msgTemplates.format(templateName, ctx=ctx, data={'savedData': {'battleResult': battleResult}})
            return (formatted, settings)
        else:
            return (None, None)

    @classmethod
    def _makeAchievementsString(cls, battleResult):
        result = []
        for recordIdx, value in battleResult.get('popUpRecords', []):
            recordName = DB_ID_TO_RECORD[recordIdx]
            if recordName in IGNORED_BY_BATTLE_RESULTS:
                continue
            achieve = getAchievementFactory(recordName).create(value=value)
            if achieve is not None and not achieve.isApproachable():
                result.append(achieve)

        if 'markOfMastery' in battleResult and battleResult['markOfMastery'] > 0:
            achieve = getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, 'markOfMastery')).create(value=battleResult['markOfMastery'])
            if achieve is not None:
                result.append(achieve)
        res = ''
        if len(result):
            res = g_settings.htmlTemplates.format('battleResultAchieves', {'achieves': ', '.join(map(lambda a: a.getUserName(), sorted(result)))})
        return res


class FortBattleRoundEndFormatter(ServiceChannelFormatter):
    __battleResultKeys = {-1: 'combatFortTechDefeatResult',
     1: 'combatFortTechVictoryResult'}

    def isNotify(self):
        return True

    def format(self, message, *args):
        battleResult = message.data
        if battleResult is not None:
            ctx = {}
            winnerCode = battleResult['isWinner']
            if winnerCode == 0:
                winnerCode = -1
            templateName = self.__battleResultKeys[winnerCode]
            settings = self._getGuiSettings(message, templateName)
            if 'combats' in battleResult:
                _, _, _, isDefendersBuilding, buildTypeID = battleResult['combats']
                if battleResult['isDefence'] is isDefendersBuilding:
                    buildOwnerClanAbbrev = battleResult['ownClanName']
                else:
                    buildOwnerClanAbbrev = battleResult['enemyClanName']
                ctx['fortBuilding'] = g_settings.htmlTemplates.format('battleResultFortBuilding', ctx={'fortBuilding': FortBuilding(typeID=buildTypeID).userName,
                 'clanAbbrev': '[%s]' % buildOwnerClanAbbrev})
            else:
                ctx['fortBuilding'] = ''
            formatted = g_settings.msgTemplates.format(templateName, ctx=ctx)
            return (formatted, settings)
        else:
            return (None, None)


class FortBattleInviteFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def format(self, message, *args):
        from notification.settings import NOTIFICATION_BUTTON_STATE
        from gui.prb_control.formatters.invites import PrbFortBattleInviteHtmlTextFormatter
        battleData = message.data
        if battleData and g_lobbyContext.getServerSettings().isFortsEnabled():
            inviteWrapper = self.__toFakeInvite(battleData)
            formatter = PrbFortBattleInviteHtmlTextFormatter()
            if message.createdAt is not None:
                timestamp = time_utils.getTimestampFromUTC(message.createdAt.timetuple())
            else:
                timestamp = time_utils.getCurrentTimestamp()
            submitState = NOTIFICATION_BUTTON_STATE.VISIBLE
            if self.prbInvites.canAcceptInvite(inviteWrapper):
                submitState |= NOTIFICATION_BUTTON_STATE.ENABLED
            msgType = 'fortBattleInvite'
            battleID = battleData.get('battleID')
            formatted = g_settings.msgTemplates.format(msgType, ctx={'text': formatter.getText(inviteWrapper)}, data={'timestamp': timestamp,
             'buttonsStates': {'submit': submitState},
             'savedData': {'battleID': battleID,
                           'peripheryID': battleData.get('peripheryID'),
                           'battleFinishTime': time_utils.getTimestampFromUTC(message.finishedAt.timetuple())},
             'icon': formatter.getIconName(inviteWrapper)})
            guiSettings = self._getGuiSettings(message, msgType)
            guiSettings.setCustomEvent(MsgCustomEvents.FORT_BATTLE_INVITE, battleID)
            return (formatted, guiSettings)
        else:
            return (None, None)

    @classmethod
    def __toFakeInvite(cls, battleData):
        from gui.shared.ClanCache import g_clanCache
        from gui.prb_control.invites import PrbInviteWrapper
        return PrbInviteWrapper(clientID=-1, receiver=getPlayerName(), state=PREBATTLE_INVITE_STATE.ACTIVE, receiverDBID=getPlayerDatabaseID(), prebattleID=-1, receiverClanAbbrev=g_lobbyContext.getClanAbbrev(g_clanCache.clanInfo), peripheryID=battleData.get('peripheryID'), extraData=battleData, type=PREBATTLE_TYPE.FORT_BATTLE, alwaysAvailable=True)


class VehicleRentedFormatter(ServiceChannelFormatter):
    _templateKey = 'vehicleRented'

    def format(self, message, *args):
        data = message.data
        vehTypeCD = data.get('vehTypeCD', None)
        expiryTime = data.get('time', None)
        return (self._getMessage(vehTypeCD, expiryTime), self._getGuiSettings(message, self._templateKey)) if vehTypeCD is not None else (None, None)

    def _getMessage(self, vehTypeCD, expiryTime):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {'vehicleName': vehicleName,
         'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class RentalsExpiredFormatter(ServiceChannelFormatter):
    _templateKey = 'rentalsExpired'

    def format(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD', None)
        return (self._getMessage(vehTypeCD), self._getGuiSettings(message, self._templateKey)) if vehTypeCD is not None else (None, None)

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
        return (formatted, settings)


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
                callback((formatted, settings))
            else:
                callback((None, None))
        else:
            callback((None, None))
        return None


class RefSystemQuestsFormatter(TokenQuestsFormatter):

    def _getTemplateName(self, completedQuestIDs=set()):
        pass


class PotapovQuestsFormatter(TokenQuestsFormatter):

    def _getTemplateName(self, completedQuestIDs=set()):
        pass


class GoodieFormatter(WaitItemsSyncFormatter):

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            goodieID = message.data.get('gid', None)
            if goodieID is not None:
                booster = g_goodiesCache.getBooster(goodieID)
                if booster is not None:
                    formatted = g_settings.msgTemplates.format(self._getTemplateName(), ctx={'boosterName': booster.userName})
                    callback((formatted, self._getGuiSettings(message, self._getTemplateName())))
                    return
            callback((None, None))
        else:
            callback((None, None))
        return

    def _getTemplateName(self):
        raise NotImplementedError


class GoodieRemovedFormatter(GoodieFormatter):

    def _getTemplateName(self):
        pass


class GoodieDisabledFormatter(GoodieFormatter):

    def _getTemplateName(self):
        pass


class TelecomStatusFormatter(ServiceChannelFormatter):

    @staticmethod
    def __getVehicleNames(vehTypeCompDescrs):
        itemGetter = g_itemsCache.items.getItemByCD
        return ', '.join((itemGetter(vehicleCD).userName for vehicleCD in vehTypeCompDescrs))

    def format(self, message, *args):
        formatted, settings = (None, None)
        try:
            template = 'telecomVehicleStatus'
            ctx = self.__getMessageContext(message.data)
            settings = self._getGuiSettings(message, template)
            formatted = g_settings.msgTemplates.format(template, ctx, data={'timestamp': time.time()})
        except:
            LOG_ERROR("Can't format telecom status message ", message)
            LOG_CURRENT_EXCEPTION()

        return (formatted, settings)

    def __getMessageContext(self, data):
        key = 'vehicleUnblocked' if data['orderStatus'] else 'vehicleBlocked'
        msgctx = {'vehicles': self.__getVehicleNames(data['vehTypeCompDescrs'])}
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
            if tankmens:
                for tankmen in tankmens:
                    skills = tankmen.get('freeSkills', [])
                    if 'brotherhood' in skills:
                        hasBrotherhood = True

        return hasBrotherhood

    def _getVehicles(self, data):
        dataEx = data.get('data', {})
        if not dataEx:
            return
        else:
            vehicles = dataEx.get('vehicles', {})
            rentedVehNames = None
            if vehicles is not None and len(vehicles) > 0:
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
        return {'vehicles': ', '.join(vehicleNames),
         'datetime': self._getOperationTimeString(data)}


class PrbVehicleKickFormatter(ServiceChannelFormatter):
    """
    Message coming from the server when the user is kicked from the squad due to the vehicle
    level doesn't correspond to commander's vehicle level rules.
    """

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        g_itemsCache.items.getVehicle(vehInvID)
        if vehInvID:
            vehicle = g_itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format('prbVehicleKick', ctx={'vehName': vehicle.userName})
        return (formatted, self._getGuiSettings(message, 'prbVehicleKick'))
