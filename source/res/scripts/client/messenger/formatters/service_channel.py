# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel.py
import operator
import re
import time
import types
from Queue import Queue
from collections import namedtuple
import logging
import ArenaType
import BigWorld
import constants
import personal_missions
from adisp import async, process
from chat_shared import decompressSysMessage, SYS_MESSAGE_TYPE, MapRemovedFromBLReason
from constants import INVOICE_ASSET, AUTO_MAINTENANCE_TYPE, AUTO_MAINTENANCE_RESULT, PREBATTLE_TYPE, FINISH_REASON, KICK_REASON_NAMES, KICK_REASON, NC_MESSAGE_TYPE, NC_MESSAGE_PRIORITY, SYS_MESSAGE_CLAN_EVENT, SYS_MESSAGE_CLAN_EVENT_NAMES, ARENA_GUI_TYPE, SYS_MESSAGE_FORT_EVENT_NAMES, PREMIUM_ENTITLEMENTS, PREMIUM_TYPE
from blueprints.BlueprintTypes import BlueprintTypes
from nations import NAMES
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from gui import GUI_SETTINGS, makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.SystemMessages import SM_TYPE
from gui.clans.formatters import getClanFullName
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.ranked_helpers.league_provider import UNDEFINED_LEAGUE_ID, TOP_LEAGUE_ID
from gui.ranked_battles.constants import YEAR_POINTS_TOKEN
from gui.ranked_battles.ranked_models import PostBattleRankInfo, RankChangeStates
from gui.server_events.awards_formatters import CompletionTokensBonusFormatter
from gui.server_events.bonuses import VehiclesBonus, DEFAULT_CREW_LVL
from gui.server_events.recruit_helper import getSourceIdFromQuest
from gui.server_events.finders import PERSONAL_MISSION_TOKEN
from gui.shared import formatters as shared_fmts
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import getBWFormatter, getStyle, applyAll
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import getUserName, getShortUserName
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.money import Money, MONEY_UNDEFINED, Currency, ZERO_MONEY
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings, NotificationGroup
from gui.shared.utils.transport import z_loads
from gui.shared.utils.requesters.blueprints_requester import getUniqueBlueprints
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from helpers import dependency
from helpers import i18n, html, getLocalizedData
from helpers import time_utils
from items import getTypeInfoByIndex, getTypeInfoByName, vehicles as vehicles_core, tankmen, ITEM_TYPES as I_T
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationNamesToTypes
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.crew_books_constants import CREW_BOOK_RARITY
from messenger import g_settings
from messenger.ext import passCensor
from messenger.formatters import TimeFormatter, NCContextItemFormatter
from shared_utils import BoundMethodWeakref, findFirst, first
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.loot_box.loot_box_helper import getMergedLootBoxBonuses
_logger = logging.getLogger(__name__)
_EOL = '\n'
_DEFAULT_MESSAGE = 'defaultMessage'
_TEMPLATE = 'template'
_RENT_TYPES = {'time': 'rentDays',
 'battles': 'rentBattles',
 'wins': 'rentWins'}
_logger = logging.getLogger(__name__)
_PREMIUM_MESSAGES = {PREMIUM_TYPE.BASIC: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumBought(),
                      str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumExtended(),
                      str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumExpired()},
 PREMIUM_TYPE.PLUS: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumPlusBought(),
                     str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumPlusExtended(),
                     str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumPlusExpired()}}
_PREMIUM_TEMPLATES = {PREMIUM_ENTITLEMENTS.BASIC: 'battleQuestsPremium',
 PREMIUM_ENTITLEMENTS.PLUS: 'battleQuestsPremiumPlus'}

def _getTimeStamp(message):
    if message.createdAt is not None:
        result = time_utils.getTimestampFromUTC(message.createdAt.timetuple())
    else:
        result = time_utils.getCurrentTimestamp()
    return result


_CustomizationItemData = namedtuple('_CustomizationItemData', ('guiItemType', 'userName'))

def _getCustomizationItemData(itemId, customizationName):
    itemsCache = dependency.instance(IItemsCache)
    customizationType = CustomizationNamesToTypes.get(customizationName.upper())
    if customizationType is None:
        _logger.warning('Wrong customization name: %s', customizationName)
    compactDescr = makeIntCompactDescrByID('customizationItem', customizationType, itemId)
    item = itemsCache.items.getItemByCD(compactDescr)
    itemName = item.userName
    itemTypeName = item.itemFullTypeName
    return _CustomizationItemData(itemTypeName, itemName)


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
                guiItemType, itemUserName = _getCustomizationItemData(customizationItem['id'], custType)
                custValue = abs(custValue)
                if custValue > 1:
                    extendable.append(backport.text(R.strings.system_messages.customization.dyn(operation).dyn('{}Value'.format(guiItemType))(), itemUserName, custValue))
                else:
                    extendable.append(backport.text(R.strings.system_messages.customization.dyn(operation).dyn(guiItemType)(), itemUserName))
            if 'compensatedNumber' in customizationItem:
                compStr = InvoiceReceivedFormatter.getCustomizationCompensationString(customizationItem, htmlTplPostfix=htmlTplPostfix)
                if compStr:
                    extendable.append(compStr)

        return


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def _extendCrewSkinsData(newData, extendable, lobbyContext=None, itemsCache=None):
    if extendable is None or not lobbyContext.getServerSettings().isCrewSkinsEnabled():
        return
    else:
        crewSkinsData = newData.get('crewSkins', None)
        if crewSkinsData is None:
            return
        totalCompensation = ZERO_MONEY
        accrued = []
        debited = []
        for crewSkinData in crewSkinsData:
            crewSkinID = crewSkinData.get('id', NO_CREW_SKIN_ID)
            count = crewSkinData.get('count', 0)
            if crewSkinID != NO_CREW_SKIN_ID:
                totalCompensation += Money(credits=crewSkinData.get('customCompensation', 0))
                if count:
                    crewSkinItem = itemsCache.items.getCrewSkin(crewSkinID)
                    if crewSkinItem is not None:
                        crewSkinUserStrings = accrued if count > 0 else debited
                        if abs(count) > 1:
                            crewSkinUserStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.crewSkinsCount(), label=localizedFullName(crewSkinItem), count=str(abs(count))))
                        else:
                            crewSkinUserStrings.append(localizedFullName(crewSkinItem))

        if accrued:
            resultStr = g_settings.htmlTemplates.format('crewSkinsAccruedReceived', ctx={'crewSkins': ', '.join(accrued)})
            extendable.append(resultStr)
        if debited:
            resultStr = g_settings.htmlTemplates.format('crewSkinsDebitedReceived', ctx={'crewSkins': ', '.join(debited)})
            extendable.append(resultStr)
        formattedCurrencies = []
        currencies = totalCompensation.getSetCurrencies(byWeight=True)
        for currency in currencies:
            formattedCurrencies.append(applyAll(currency, totalCompensation.get(currency=currency)))

        if formattedCurrencies:
            extendable.append(backport.text(R.strings.system_messages.crewSkinsCompensation.success(), compensation=', '.join(formattedCurrencies)))
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
        shortcut = R.strings.system_messages.actionAchievement
        if unknownAchieves > 1:
            shortcut = R.strings.system_messages.actionAchievements
        achievements.append(backport.text(shortcut.title()))
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


def _getCrewBookUserString(itemDescr):
    params = {}
    if itemDescr.type != CREW_BOOK_RARITY.PERSONAL:
        params['nation'] = i18n.makeString('#nations:{}'.format(itemDescr.nation))
    return i18n.makeString(itemDescr.name, **params)


_MessageData = namedtuple('MessageData', 'data, settings')

class ServiceChannelFormatter(object):

    def format(self, data, *args):
        return []

    def isNotify(self):
        return True

    def isAsync(self):
        return False

    def _getGuiSettings(self, data, key=None, priorityLevel=None, messageType=None, messageSubtype=None):
        try:
            isAlert = data.isHighImportance and data.active
        except AttributeError:
            isAlert = False

        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel, isAlert, messageType=messageType, messageSubtype=messageSubtype)

    def canBeEmpty(self):
        return False


class WaitItemsSyncFormatter(ServiceChannelFormatter):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__callbackQueue = None
        return

    def isAsync(self):
        return True

    @async
    def _waitForSyncItems(self, callback):
        if self._itemsCache.isSynced():
            callback(True)
        else:
            self.__registerHandler(callback)

    def __registerHandler(self, callback):
        if not self.__callbackQueue:
            self.__callbackQueue = Queue()
        self.__callbackQueue.put(callback)
        self._itemsCache.onSyncCompleted += self.__onSyncCompleted

    def __unregisterHandler(self):
        self.__callbackQueue = None
        self._itemsCache.onSyncCompleted -= self.__onSyncCompleted
        return

    def __onSyncCompleted(self, *_):
        while not self.__callbackQueue.empty():
            self.__callbackQueue.get_nowait()(self._itemsCache.isSynced())

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
                vehicleNames = {intCD:self._itemsCache.items.getItemByCD(intCD) for intCD in battleResults.get('playerVehicles', {}).keys()}
                ctx['vehicleNames'] = ', '.join(map(operator.attrgetter('userName'), sorted(vehicleNames.values())))
                xp = battleResults.get('xp')
                if xp:
                    ctx['xp'] = backport.getIntegralFormat(xp)
                battleResKey = battleResults.get('isWinner', 0)
                ctx['xpEx'] = self.__makeXpExString(xp, battleResKey, battleResults.get('xpPenalty', 0), battleResults)
                ctx[Currency.GOLD] = self.__makeGoldString(battleResults.get(Currency.GOLD, 0))
                accCredits = battleResults.get(Currency.CREDITS) - battleResults.get('creditsToDraw', 0)
                if accCredits:
                    ctx[Currency.CREDITS] = self.__makeCurrencyString(Currency.CREDITS, accCredits)
                ctx['piggyBank'] = self.__makePiggyBankString(battleResults.get('piggyBank'))
                accCrystal = battleResults.get(Currency.CRYSTAL)
                ctx['crystalStr'] = ''
                if accCrystal:
                    ctx[Currency.CRYSTAL] = self.__makeCurrencyString(Currency.CRYSTAL, accCrystal)
                    ctx['crystalStr'] = g_settings.htmlTemplates.format('battleResultCrystal', {Currency.CRYSTAL: ctx[Currency.CRYSTAL]})
                ctx['creditsEx'] = self.__makeCreditsExString(accCredits, battleResults.get('creditsPenalty', 0), battleResults.get('creditsContributionIn', 0), battleResults.get('creditsContributionOut', 0))
                guiType = battleResults.get('guiType', 0)
                ctx['achieves'], ctx['badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
                ctx['rankedProgress'] = self.__makeRankedFlowStrings(battleResults)
                ctx['rankedBonusBattles'] = self.__makeRankedBonusString(battleResults)
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
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.penaltyForDamageAllies(), backport.getIntegralFormat(xpPenalty)))
        if battleResKey == 1:
            xpFactorStrings = []
            xpFactor = battleResults.get('dailyXPFactor', 1)
            if xpFactor > 1:
                xpFactorStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.doubleXpFactor()) % xpFactor)
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
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.penaltyForDamageAllies(), formatter(penalty)))
        if creditsContributionIn > 0:
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.contributionForDamageAllies(), formatter(creditsContributionIn)))
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
        achievementsBlock = ''
        if achievementsStrings:
            achievementsBlock = g_settings.htmlTemplates.format('battleResultAchieves', {'achieves': ', '.join(achievementsStrings)})
        badgesBlock = ''
        if badges:
            badgesStr = ', '.join([ backport.text(R.strings.badge.dyn('badge_{}'.format(badgeID))()) for badgeID in badges ])
            badgesBlock = '<br/>' + g_settings.htmlTemplates.format('badgeAchievement', {'badges': badgesStr})
        return (achievementsBlock, badgesBlock)

    def __makeRankedFlowStrings(self, battleResults):
        rankedProgressStrings = []
        if battleResults.get('guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankedController = dependency.instance(IRankedBattlesController)
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            stateChange = rankedController.getRankChangeStatus(rankInfo)
            if stateChange in (RankChangeStates.QUAL_EARNED, RankChangeStates.QUAL_UNBURN_EARNED):
                stateChange = RankChangeStates.DIVISION_EARNED
            shortcut = R.strings.messenger.serviceChannelMessages.battleResults
            stateChangeResID = shortcut.rankedState.dyn(stateChange)()
            if stateChange == RankChangeStates.DIVISION_EARNED:
                divisionNumber = backport.text(shortcut.divisions.dyn(rankedController.getDivision(rankInfo.accRank + 1).getUserID())())
                stateChangeStr = backport.text(stateChangeResID, divisionNumber=divisionNumber)
            elif stateChange in (RankChangeStates.RANK_LOST, RankChangeStates.RANK_EARNED):
                rankID = rankInfo.prevAccRank
                if stateChange == RankChangeStates.RANK_EARNED:
                    rankID = rankInfo.accRank
                division = rankedController.getDivision(rankID)
                rankName = division.getRankUserName(rankID)
                divisionName = division.getUserName()
                stateChangeStr = backport.text(stateChangeResID, rankName=rankName, divisionName=divisionName)
            else:
                stateChangeStr = backport.text(stateChangeResID)
                isWin = True if battleResults.get('isWinner', 0) > 0 else False
                if stateChange == RankChangeStates.NOTHING_CHANGED and isWin:
                    stateChangeStr = backport.text(shortcut.rankedState.stageNotEarned())
                shieldState = rankInfo.shieldState
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
                    stateChangeStr = backport.text(shortcut.rankedState.shieldLose())
            rankedProgressStrings.append(stateChangeStr)
        rankedProgressBlock = ''
        if rankedProgressStrings:
            rankedProgressBlock = g_settings.htmlTemplates.format('battleResultRankedProgress', {'rankedProgress': ', '.join(rankedProgressStrings)})
        return rankedProgressBlock

    def __makeRankedBonusString(self, battleResults):
        rankedBonusBattlesString = ''
        if battleResults.get('guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            if rankInfo.additionalBonusBattles > 0 or rankInfo.qualificationBonusBattles > 0:
                rankedBonusBattlesString = text_styles.concatStylesToMultiLine(rankedBonusBattlesString, backport.text(R.strings.messenger.serviceChannelMessages.battleResults.rankedBonusBattles.text(), divisionAmount=text_styles.neutral(rankInfo.additionalBonusBattles), qualificationAmount=text_styles.neutral(rankInfo.qualificationBonusBattles)))
        rankedBonusBattlesBlock = ''
        if rankedBonusBattlesString:
            rankedBonusBattlesBlock = g_settings.htmlTemplates.format('battleResultRankedBonusBattles', {'rankedBonusBattles': rankedBonusBattlesString})
        return rankedBonusBattlesBlock

    def __makePiggyBankString(self, credits_):
        return '' if not credits_ else g_settings.htmlTemplates.format('piggyBank', ctx={'credits': self.__makeCurrencyString(Currency.CREDITS, credits_)})


class AutoMaintenanceFormatter(WaitItemsSyncFormatter):
    itemsCache = dependency.descriptor(IItemsCache)
    __serviceChannelMessages = R.strings.messenger.serviceChannelMessages
    __messages = {AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS: {AUTO_MAINTENANCE_TYPE.REPAIR: R.strings.messenger.serviceChannelMessages.autoRepairError(),
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: R.strings.messenger.serviceChannelMessages.autoLoadError(),
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.messenger.serviceChannelMessages.autoEquipError(),
                                                 AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: R.strings.messenger.serviceChannelMessages.autoEquipBoosterError(),
                                                 AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleError()},
     AUTO_MAINTENANCE_RESULT.OK: {AUTO_MAINTENANCE_TYPE.REPAIR: R.strings.messenger.serviceChannelMessages.autoRepairSuccess(),
                                  AUTO_MAINTENANCE_TYPE.LOAD_AMMO: R.strings.messenger.serviceChannelMessages.autoLoadSuccess(),
                                  AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.messenger.serviceChannelMessages.autoEquipSuccess(),
                                  AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: R.strings.messenger.serviceChannelMessages.autoEquipBoosterSuccess(),
                                  AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleSuccess()},
     AUTO_MAINTENANCE_RESULT.NOT_PERFORMED: {AUTO_MAINTENANCE_TYPE.REPAIR: R.strings.messenger.serviceChannelMessages.autoRepairSkipped(),
                                             AUTO_MAINTENANCE_TYPE.LOAD_AMMO: R.strings.messenger.serviceChannelMessages.autoLoadSkipped(),
                                             AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.messenger.serviceChannelMessages.autoEquipSkipped(),
                                             AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: R.strings.messenger.serviceChannelMessages.autoEquipBoosterSkipped(),
                                             AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleSkipped()},
     AUTO_MAINTENANCE_RESULT.DISABLED_OPTION: {AUTO_MAINTENANCE_TYPE.REPAIR: R.strings.messenger.serviceChannelMessages.autoRepairDisabledOption(),
                                               AUTO_MAINTENANCE_TYPE.LOAD_AMMO: R.strings.messenger.serviceChannelMessages.autoLoadDisabledOption(),
                                               AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.messenger.serviceChannelMessages.autoEquipDisabledOption(),
                                               AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: R.strings.messenger.serviceChannelMessages.autoEquipBoosterDisabledOption(),
                                               AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleDisabledOption()},
     AUTO_MAINTENANCE_RESULT.NO_WALLET_SESSION: {AUTO_MAINTENANCE_TYPE.REPAIR: R.strings.messenger.serviceChannelMessages.autoRepairErrorNoWallet(),
                                                 AUTO_MAINTENANCE_TYPE.LOAD_AMMO: R.strings.messenger.serviceChannelMessages.autoLoadErrorNoWallet(),
                                                 AUTO_MAINTENANCE_TYPE.EQUIP: R.strings.messenger.serviceChannelMessages.autoEquipErrorNoWallet(),
                                                 AUTO_MAINTENANCE_TYPE.EQUIP_BOOSTER: R.strings.messenger.serviceChannelMessages.autoBoosterErrorNoWallet(),
                                                 AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleErrorNoWallet()},
     AUTO_MAINTENANCE_RESULT.RENT_IS_OVER: {AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleRentIsOver.text()},
     AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER: {AUTO_MAINTENANCE_TYPE.CUSTOMIZATION: R.strings.messenger.serviceChannelMessages.autoRentStyleRentIsAlmostOverAutoprolongationOFF.text()}}
    __currencyTemplates = {Currency.CREDITS: 'PurchaseForCreditsSysMessage',
     Currency.GOLD: 'PurchaseForGoldSysMessage',
     Currency.CRYSTAL: 'PurchaseForCrystalSysMessage'}

    def isNotify(self):
        return True

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            vehicleCompDescr = message.data.get('vehTypeCD', None)
            styleId = message.data.get('styleID', None)
            result = message.data.get('result', None)
            typeID = message.data.get('typeID', None)
            cost = Money(*message.data.get('cost', ()))
            if vehicleCompDescr is not None and result is not None and typeID is not None:
                vehicle = self.itemsCache.items.getItemByCD(vehicleCompDescr)
                if typeID == AUTO_MAINTENANCE_TYPE.REPAIR:
                    formatMsgType = 'RepairSysMessage'
                else:
                    formatMsgType = self._getTemplateByCurrency(cost.getCurrency(byWeight=False))
                msgTmplKey = self.__messages[result].get(typeID, None)
                msgArgs = None
                data = None
                if result in (AUTO_MAINTENANCE_RESULT.RENT_IS_OVER, AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER):
                    cc = vehicles_core.g_cache.customization20()
                    style = cc.styles.get(styleId, None)
                    if style:
                        styleName = style.userString
                        vehName = vehicle.shortUserName
                        data = {'savedData': {'styleIntCD': style.compactDescr,
                                       'vehicleIntCD': vehicleCompDescr,
                                       'toStyle': True}}
                        if result == AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER and vehicle.isAutoRentStyle:
                            msgTmplKey = R.strings.messenger.serviceChannelMessages.autoRentStyleRentIsAlmostOverAutoprolongationON.text()
                            msgArgs = (styleName, vehName, style.rentCount)
                        else:
                            msgArgs = (styleName, vehName)
                else:
                    vehName = vehicle.userName
                    msgArgs = (vehName,)
                if msgArgs is not None:
                    msgTmpl = backport.text(msgTmplKey)
                    if not msgTmpl:
                        _logger.warning('Invalid typeID field in message: %s', message)
                        callback([_MessageData(None, None)])
                    else:
                        msg = msgTmpl % msgArgs
                else:
                    msg = ''
                priorityLevel = NotificationPriorityLevel.MEDIUM
                if result == AUTO_MAINTENANCE_RESULT.OK:
                    priorityLevel = NotificationPriorityLevel.LOW
                    templateName = formatMsgType
                elif result == AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS:
                    templateName = 'ErrorSysMessage'
                elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_OVER:
                    templateName = 'RentOfStyleIsExpiredSysMessage'
                elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER:
                    if vehicle.isAutoRentStyle:
                        templateName = 'RentOfStyleIsAlmostExpiredAutoprolongationONSysMessage'
                    else:
                        templateName = 'RentOfStyleIsAlmostExpiredAutoprolongationOFFSysMessage'
                else:
                    templateName = 'WarningSysMessage'
                if result == AUTO_MAINTENANCE_RESULT.OK:
                    msg += shared_fmts.formatPrice(cost.toAbs(), ignoreZeros=True)
                formatted = g_settings.msgTemplates.format(templateName, {'text': msg}, data=data)
                settings = self._getGuiSettings(message, priorityLevel=priorityLevel, messageType=message.type, messageSubtype=result)
                callback([_MessageData(formatted, settings)])
            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
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
                    badgesList.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                achieve = getAchievementFactory((block, name)).create(value)
                if achieve is not None:
                    achievesList.append(achieve.getUserName())
                achievesList.append(backport.text(R.strings.achievements.dyn(name)()))

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
            xmlKey = 'currencyUpdate'
            formatted = g_settings.msgTemplates.format(xmlKey, ctx={'date': TimeFormatter.getLongDatetimeFormat(transactionTime),
             'currency': backport.text(R.strings.messenger.serviceChannelMessages.currencyUpdate.dyn('debited' if amountDelta < 0 else 'received').dyn(currencyCode)()),
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
     'premium_plus': ('_GiftReceivedFormatter__formatPremiumGiftMsg', 'tankPremiumReceivedAsGift'),
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
            result = g_settings.msgTemplates.format(key, ctx={'freeXP': backport.getIntegralFormat(xp)})
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
    __blueprintsTemplateKeys = {BlueprintTypes.VEHICLE: ('vehicleBlueprintsAccruedInvoiceReceived', 'vehicleBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.NATIONAL: ('nationalBlueprintsAccruedInvoiceReceived', 'nationalBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.INTELLIGENCE_DATA: ('intelligenceBlueprintsAccruedInvoiceReceived', 'intelligenceBlueprintsDebitedInvoiceReceived')}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: 'goldInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: 'crystalInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: 'dataInvoiceReceived'}
    __goodiesCache = dependency.descriptor(IGoodiesCache)

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

    @classmethod
    def getBlueprintString(cls, blueprints):
        vehicleFragments, nationFragments, universalFragments = getUniqueBlueprints(blueprints)
        blueprintsString = []
        for fragmentCD, count in vehicleFragments.iteritems():
            ctx = cls.__getBlueprintContext(count)
            vehicleName = cls.__getVehicleName(fragmentCD)
            ctx['vehicleName'] = vehicleName
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.VEHICLE, count, ctx))

        for nationID, count in nationFragments.iteritems():
            ctx = cls.__getBlueprintContext(count)
            localizedNationName = backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase())
            ctx['nationName'] = localizedNationName
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.NATIONAL, count, ctx))

        if universalFragments:
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.INTELLIGENCE_DATA, universalFragments, cls.__getBlueprintContext(universalFragments)))
        return '<br>'.join(blueprintsString)

    @classmethod
    def hasRenewBonus(cls, vehicles):
        for vehInfo in vehicles.itervalues():
            rent = vehInfo.get('rent')
            if rent:
                cycles = rent.get('cycle')
                renew = rent.get('renew')
                if cycles and not renew:
                    return True

        return False

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
            if cls.hasRenewBonus(vehicles):
                result.append(backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.vehiclesRented.bonus()))
        return '<br/>'.join(result)

    @classmethod
    def _getCustomizationCompensationString(cls, compensationMoney, strItemType, strItemName, amount, htmlTplPostfix):
        htmlTemplates = g_settings.htmlTemplates
        values = []
        result = ''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            key = '{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={'amount': applyAll(currency, compensationMoney.get(currency))}))

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
        strItemType = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.compensation.dyn(customItemData.guiItemType)())
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
                _logger.error('Wrong tankman data: %s', tmanData)
                _logger.exception('getTankmenString catch exception')

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
            if goodieID in cls._itemsCache.items.shop.boosters:
                booster = cls.__goodiesCache.getBooster(goodieID)
                if booster is not None and booster.enabled:
                    if ginfo.get('count'):
                        boostersStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=booster.userName, count=ginfo.get('count')))
                    else:
                        boostersStrings.append(booster.userName)
            discount = cls.__goodiesCache.getDiscount(goodieID)
            if discount is not None and discount.enabled:
                discountsStrings.append(discount.description)

        if boostersStrings:
            result.append(g_settings.htmlTemplates.format('boostersInvoiceReceived', ctx={'boosters': ', '.join(boostersStrings)}))
        if discountsStrings:
            result.append(g_settings.htmlTemplates.format('discountsInvoiceReceived', ctx={'discounts': ', '.join(discountsStrings)}))
        return '; '.join(result)

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
            premium = dataEx.get(PREMIUM_ENTITLEMENTS.BASIC)
            if premium is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.PREMIUM, premium))
            tankPremium = dataEx.get(PREMIUM_ENTITLEMENTS.PLUS)
            if tankPremium is not None:
                operations.append(self.__getTankPremiumString(tankPremium))
            items = dataEx.get('items', {})
            items = self.__composeItems(items)
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
            blueprints = dataEx.get('blueprints')
            if blueprints:
                operations.append(self.getBlueprintString(blueprints))
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
            _extendCrewSkinsData(dataEx, operations)
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

    def _formatAmount(self, assetType, data):
        amount = data.get('amount', None)
        return None if amount is None else g_settings.msgTemplates.format(self._getMessageTemplateKey(assetType), ctx={'at': self._getOperationTimeString(data),
         'desc': self.__getL10nDescription(data),
         'op': self.__getFinOperationString(assetType, amount)})

    def _getMessageTemplateKey(self, assetType):
        return self.__messageTemplateKeys[assetType]

    @classmethod
    def _getOperationTimeString(cls, data):
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
    def _getCompensationString(cls, compensationMoney, strItemNames, htmlTplPostfix):
        htmlTemplates = g_settings.htmlTemplates
        values = []
        result = ''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            key = '{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={'amount': applyAll(currency, compensationMoney.get(currency))}))

        if values:
            result = htmlTemplates.format('compensationFor' + htmlTplPostfix, ctx={'items': ', '.join(strItemNames),
             'compensation': ', '.join(values)})
        return result

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

    @classmethod
    def __getBlueprintContext(cls, count):
        return {'amount': backport.getIntegralFormat(abs(count))}

    @classmethod
    def __formatBlueprintsString(cls, fragmentType, count, ctx):
        if count > 0:
            template = cls.__blueprintsTemplateKeys[fragmentType][0]
        else:
            template = cls.__blueprintsTemplateKeys[fragmentType][1]
        return g_settings.htmlTemplates.format(template, ctx)

    def __prerocessRareAchievements(self, data):
        dossiers = data.get('data', {}).get('dossier', {})
        if dossiers:
            self.__dossierResult = []
            rares = [ rec['value'] for d in dossiers.itervalues() for (blck, _), rec in d.iteritems() if blck == ACHIEVEMENT_BLOCK.RARE ]
            addDossierStrings, delDossierStrings, addBadgesStrings, removedBadgesStrings = ([],
             [],
             [],
             [])
            for rec in dossiers.itervalues():
                for (block, name), recData in rec.iteritems():
                    if name != '':
                        isRemoving = recData['value'] < 0
                        if block == BADGES_BLOCK:
                            if isRemoving:
                                removedBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                            else:
                                addBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                        elif block != ACHIEVEMENT_BLOCK.RARE:
                            achieve = getAchievementFactory((block, name)).create(recData['actualValue'])
                            if achieve is not None:
                                achieveName = achieve.getUserName()
                            else:
                                achieveName = backport.text(R.strings.achievements.dyn(name))
                            if isRemoving:
                                delDossierStrings.append(achieveName)
                            else:
                                addDossierStrings.append(achieveName)

            addDossiers = [ rare for rare in rares if rare > 0 ]
            if addDossiers:
                addDossierStrings += _processRareAchievements(addDossiers)
            if addDossierStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersAccruedInvoiceReceived', ctx={'dossiers': ', '.join(addDossierStrings)}))
            delDossiers = [ abs(rare) for rare in rares if rare < 0 ]
            if delDossiers:
                delDossierStrings += _processRareAchievements(delDossiers)
            if delDossierStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('dossiersDebitedInvoiceReceived', ctx={'dossiers': ', '.join(delDossierStrings)}))
            if addBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('badgeAchievement', ctx={'badges': ', '.join(addBadgesStrings)}))
            if removedBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format('removedBadgeAchievement', ctx={'badges': ', '.join(removedBadgesStrings)}))
        return

    def __getDossierString(self):
        return '<br/>'.join(self.__dossierResult)

    def __getFinOperationString(self, assetType, amount, formatter=None):
        templateKey = 0 if amount > 0 else 16
        templateKey |= assetType
        ctx = {}
        if formatter is not None:
            ctx['amount'] = formatter(abs(amount))
        else:
            ctx['amount'] = backport.getIntegralFormat(abs(amount))
        return g_settings.htmlTemplates.format(self.__operationTemplateKeys[templateKey], ctx=ctx)

    def __composeItems(self, items):

        def validateItem(item):
            itemCompactDescr, _ = item
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(itemCompactDescr)
            if itemTypeID == I_T.crewBook:
                lobbyContext = dependency.instance(ILobbyContext)
                if not lobbyContext.getServerSettings().isCrewBooksEnabled():
                    return False
            return True

        return dict(filter(validateItem, items.iteritems()))

    def __getItemsString(self, items, installed=False):
        accrued = []
        debited = []
        for itemCompactDescr, count in items.iteritems():
            if count:
                try:
                    itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(itemCompactDescr)
                    if itemTypeID == I_T.crewBook:
                        item = tankmen.getItemByCompactDescr(itemCompactDescr)
                        userString = _getCrewBookUserString(item)
                    else:
                        item = vehicles_core.getItemByCompactDescr(itemCompactDescr)
                        userString = item.i18n.userString
                    itemString = '{0:s} "{1:s}" - {2:d} {3:s}'.format(getTypeInfoByName(item.itemTypeName)['userString'], userString, abs(count), backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.pieces()))
                    if count > 0:
                        accrued.append(itemString)
                    else:
                        debited.append(itemString)
                except Exception:
                    _logger.error('itemCompactDescr can not parse: %s ', itemCompactDescr)
                    _logger.exception('getItemsString catch exception')

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
    def __getSlotsString(cls, slots):
        if slots > 0:
            template = 'slotsAccruedInvoiceReceived'
        else:
            template = 'slotsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': backport.getIntegralFormat(abs(slots))})

    @classmethod
    def __getTankPremiumString(cls, expireTime):
        if expireTime > 0:
            template = 'tankPremiumAccruedInvoiceReceived'
        else:
            template = 'tankPremiumDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': backport.getIntegralFormat(abs(expireTime))})

    @classmethod
    def __getBerthsString(cls, berths):
        if berths > 0:
            template = 'berthsAccruedInvoiceReceived'
        else:
            template = 'berthsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {'amount': backport.getIntegralFormat(abs(berths))})

    @classmethod
    def __getTankmenFreeXPString(cls, data):
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
        return g_settings.htmlTemplates.format(template, {'tankmenFreeXp': backport.getIntegralFormat(abs(freeXP)),
         'spec': specStr})

    @classmethod
    def __getL10nDescription(cls, data):
        descr = ''
        lData = getLocalizedData(data.get('data', {}), 'localized_description', defVal=None)
        if lData:
            descr = i18n.encodeUtf8(html.escape(lData.get('description', u'')))
            if descr:
                descr = '<br/>' + descr
        return descr

    @classmethod
    def __getVehicleInfo(cls, vehData, isWithdrawn):
        vInfo = []
        if isWithdrawn:
            toBarracks = not vehData.get('dismissCrew', False)
            action = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewWithdrawn())
            if toBarracks:
                action = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewDroppedToBarracks())
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
                    rentLeftStr = backport.text(R.strings.tooltips.quests.awards.vehicleRent.rentLeft.dyn(rentTypeName)(), count=rentLeftCount)
                    vInfo.append(rentLeftStr)
            crewLevel = VehiclesBonus.getTmanRoleLevel(vehData)
            if crewLevel is not None and crewLevel > DEFAULT_CREW_LVL:
                if 'crewInBarracks' in vehData and vehData['crewInBarracks']:
                    crewWithLevelString = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewWithLvlDroppedToBarracks(), crewLevel)
                else:
                    crewWithLevelString = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewOnVehicle(), crewLevel)
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
            _logger.error('Wrong vehicle compact descriptor: %s', vehCompDescr)
            _logger.exception('getVehicleName catch exception')

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
            elif isinstance(dataType, types.DictType):
                text = getLocalizedData({'value': data}, 'value')
            if not text:
                _logger.error('Text of message not found: %s', message)
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
            accountTypeName = backport.text(R.strings.menu.accountTypes.base())
            if isPremium:
                accountTypeName = backport.text(R.strings.menu.accountTypes.premium())
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


class _PremiumActionFormatter(ServiceChannelFormatter):
    _templateKey = None

    def _getMessage(self, isPremium, premiumType, expiryTime):
        return None

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium')
        expiryTime = data.get('expiryTime', 0)
        premiumType = data.get('premType')
        return [_MessageData(self._getMessage(isPremium, premiumType, expiryTime), self._getGuiSettings(message, self._templateKey))] if isPremium is not None and premiumType is not None else [_MessageData(None, None)]


class PremiumBoughtFormatter(_PremiumActionFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumBought)

    def _getMessage(self, isPremium, premiumType, expiryTime):
        result = None
        if isPremium is True and expiryTime > 0:
            formattedText = backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey], expiryTime=text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime)))
            result = g_settings.msgTemplates.format(self._templateKey, ctx={'text': formattedText})
        return result


class PremiumExtendedFormatter(PremiumBoughtFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumExtended)


class PremiumExpiredFormatter(_PremiumActionFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumExpired)

    def _getMessage(self, isPremium, premiumType, expiryTime):
        result = None
        if isPremium is False:
            result = g_settings.msgTemplates.format(self._templateKey, ctx={'text': backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey])})
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
        return backport.text(R.strings.messenger.serviceChannelMessages.prebattle.battleType.dyn(typeString)())

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
                numberOfBattleString = backport.text(R.strings.messenger.serviceChannelMessages.prebattle.numberOfBattle(), battlesCount)
                description = '{0:s} {1:s}'.format(description, numberOfBattleString)
            else:
                _logger.warning('Invalid value of battlesCount: %s', battlesCount)
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
            resID = R.strings.messenger.serviceChannelMessages.prebattle.finish.dyn(finishString).dyn(resultString)()
        else:
            resID = R.strings.messenger.serviceChannelMessages.prebattle.finish.dyn(finishString)()
        return backport.text(resID)


class PrebattleArenaFinishFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {FINISH_REASON.TECHNICAL: ('technical', True),
     FINISH_REASON.FAILURE: ('failure', False),
     FINISH_REASON.UNKNOWN: ('failure', False)}

    def format(self, message, *args):
        _logger.debug('prbArenaFinish %s', message)
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
            resID = R.strings.system_messages.prebattle.kick.type.unknown()
            if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
                resID = R.strings.system_messages.prebattle.kick.type.squad()
            ctx['type'] = backport.text(resID)
            kickName = KICK_REASON_NAMES[kickReason]
            resID = R.strings.system_messages.prebattle.kick.reason.dyn(kickName)()
            ctx['reason'] = backport.text(resID)
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
        _logger.debug('prbDestruction %s', message)
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
    __itemsCache = dependency.descriptor(IItemsCache)

    def __i18nValue(self, key, isReceived, **kwargs):
        key = ('%sReceived' if isReceived else '%sWithdrawn') % key
        resID = R.strings.messenger.serviceChannelMessages.sysMsg.converter.dyn(key)()
        return backport.text(resID) % kwargs

    def __vehName(self, vehCompDescr):
        return getUserName(vehicles_core.getVehicleType(abs(vehCompDescr)))

    def format(self, message, *args):
        data = message.data
        text = []
        if data.get('inscriptions'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.inscriptions()))
        if data.get('emblems'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.emblems()))
        if data.get('camouflages'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.camouflages()))
        if data.get('customizations'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.customizations()))
        vehicles = data.get('vehicles')
        if vehicles:
            vehiclesReceived = [ self.__vehName(cd) for cd in vehicles if cd > 0 and self.__itemsCache.items.doesVehicleExist(cd) ]
            if vehiclesReceived:
                text.append(self.__i18nValue('vehicles', True, vehicles=', '.join(vehiclesReceived)))
            vehiclesWithdrawn = [ self.__vehName(cd) for cd in vehicles if cd < 0 and self.__itemsCache.items.doesVehicleExist(abs(cd)) ]
            if vehiclesWithdrawn:
                text.append(self.__i18nValue('vehicles', False, vehicles=', '.join(vehiclesWithdrawn)))
        slots = data.get('slots')
        if slots:
            text.append(self.__i18nValue('slots', slots > 0, slots=backport.getIntegralFormat(abs(slots))))
        for currency in Currency.ALL:
            value = data.get(currency)
            if value:
                formatter = getBWFormatter(currency)
                kwargs = {currency: formatter(abs(value))}
                text.append(self.__i18nValue(currency, (value > 0), **kwargs))

        freeXP = data.get('freeXP')
        if freeXP:
            text.append(self.__i18nValue('freeXP', freeXP > 0, freeXP=backport.getIntegralFormat(abs(freeXP))))
        messagesListData = []
        if text:
            formatted = g_settings.msgTemplates.format('ConverterNotify', {'text': '<br/>'.join(text)})
            messagesListData.append(_MessageData(formatted, self._getGuiSettings(message, 'ConverterNotify')))
        if data.get('projectionDecalsDemounted'):
            messageKey = R.strings.messenger.serviceChannelMessages.sysMsg.converter.projectionDecalsDemounted()
            messageText = backport.text(messageKey)
            templateName = 'ProjectionDecalsDemountedSysMessage'
            formatted = g_settings.msgTemplates.format(templateName, {'text': messageText})
            messagesListData.append(_MessageData(formatted, self._getGuiSettings(message, 'ProjectionDecalsDemountedSysMessage')))
        return messagesListData


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
        return self._doFormat(backport.text(R.strings.aogas.dyn(data.name())()), 'AOGASNotify', *args)


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
                    subjects += backport.text(R.strings.messenger.serviceChannelMessages.serverDowntimeCompensation.dyn(key)())

            if subjects:
                formatted = g_settings.msgTemplates.format(self.__templateKey, ctx={'text': backport.text(R.strings.messenger.serviceChannelMessages.serverDowntimeCompensation.message()) % subjects})
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
        _logger.debug('message data: %s', data)
        finishReason = data.get('finishReason', -1)
        resultKey = data.get('resultKey', None)
        finishKey = data.get('finishKey', None)
        if finishReason > -1 and resultKey and finishKey:
            resultString = backport.text(R.strings.messenger.serviceChannelMessages.battleTutorial.results.dyn(resultKey)())
            reasonString = backport.text(R.strings.messenger.serviceChannelMessages.battleTutorial.reasons.dyn(finishKey)())
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
                ctx['freeXP'] = backport.getIntegralFormat(freeXP)
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
        _logger.debug('message data: %s', message)
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            text = []
            results = message.data
            if results:
                text.append(self.__formatAwards(results))
            else:
                text.append(backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.no_awards()))
            settings = self._getGuiSettings(message, 'bootcampResults')
            formatted = g_settings.msgTemplates.format('bootcampResults', {'text': '<br/>'.join(text)}, data={'timestamp': _getTimeStamp(message)})
        callback([_MessageData(formatted, settings)])
        return None

    def __formatAwards(self, results):
        awards = backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.awards()) + '<br/>'
        awards += self.__getAssetString(results, INVOICE_ASSET.GOLD, 'gold')
        awards += self.__getAssetString(results, INVOICE_ASSET.PREMIUM, 'premium')
        awards += self.__getAssetString(results, INVOICE_ASSET.CREDITS, 'credits')
        tankPremiumDays = results.get(PREMIUM_ENTITLEMENTS.PLUS, 0)
        if tankPremiumDays:
            awards += '<br/>' + g_settings.htmlTemplates.format('tankPremiumAccruedInvoiceReceived', {'amount': backport.getIntegralFormat(abs(tankPremiumDays))})
        vehicles = results.get('vehicles', {})
        vehiclesNames = []
        devicesAndCrew = ''
        for vehID, vehData in vehicles.iteritems():
            vehicle = self._itemsCache.items.getItemByCD(vehID)
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
            awards += '<br/>' + g_settings.htmlTemplates.format('slotsAccruedInvoiceReceived', {'amount': backport.getIntegralFormat(abs(slots))})
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
            message += backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.devices())
            itemsNames = []
            for intCD, count in devices:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                if itemDescr.i18n.userString != '':
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=itemDescr.i18n.userString, count=backport.getIntegralFormat(count)))

            if itemsNames:
                message += '<br/>' + ', '.join(itemsNames) + '<br/>'
        crewInBarracks = vehData.get('crewInBarracks', False)
        if crewInBarracks:
            message += backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.crew())
        return message

    @staticmethod
    def __getAssetString(results, assetType, amountType):
        amount = results.get(amountType, 0)
        if amount:
            templateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
             INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
             INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived'}
            return '<br/>' + g_settings.htmlTemplates.format(templateKeys[assetType], ctx={'amount': backport.getIntegralFormat(abs(amount))})


class TokenQuestsFormatter(WaitItemsSyncFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __PERSONAL_MISSIONS_CUSTOM_TEMPLATE = 'personalMissionsCustom'
    __FRONTLINE_REWARD_QUEST_TEMPLATE = 'bought_frontline_reward_veh_'
    _FRONTLINE_PRESTIGE_POINTS_EXCHANGE_TEMPLATE = 'PrestigePointsExchange'

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
            if self.__FRONTLINE_REWARD_QUEST_TEMPLATE in first(completedQuestIDs, ''):
                callback([_MessageData(None, None)])
                return
            if self.__processPersonalMissionsSpecial(completedQuestIDs, message, callback):
                return
            if self._FRONTLINE_PRESTIGE_POINTS_EXCHANGE_TEMPLATE in first(completedQuestIDs, ''):
                result = yield FrontlineExchangeQuestFormatter().format(message)
                callback(result)
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
        for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
            premium = data.get(premiumType, 0)
            if premium:
                result.append(cls.__makeQuestsAchieve(_PREMIUM_TEMPLATES[premiumType], days=premium))

        if not asBattleFormatter:
            freeXP = data.get('freeXP', 0)
            if freeXP:
                result.append(cls.__makeQuestsAchieve('battleQuestsFreeXP', freeXP=backport.getIntegralFormat(freeXP)))
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
            result.append(cls.__makeQuestsAchieve('battleQuestsSlots', slots=backport.getIntegralFormat(slots)))
        items = data.get('items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            if itemTypeID == I_T.crewBook:
                if not cls.__lobbyContext.getServerSettings().isCrewBooksEnabled():
                    continue
                itemDescr = tankmen.getItemByCompactDescr(intCD)
                name = _getCrewBookUserString(itemDescr)
            else:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                name = itemDescr.i18n.userString
            itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(count)))

        if itemsNames:
            result.append(cls.__makeQuestsAchieve('battleQuestsItems', names=', '.join(itemsNames)))
        _extendCrewSkinsData(data, result)
        if processCustomizations:
            _extendCustomizationData(data, result, htmlTplPostfix='QuestsReceived')
        berths = data.get('berths', 0)
        if berths:
            result.append(cls.__makeQuestsAchieve('battleQuestsBerths', berths=backport.getIntegralFormat(berths)))
        tmen = data.get('tankmen', {})
        if tmen:
            result.append(InvoiceReceivedFormatter.getTankmenString(tmen))
        goodies = data.get('goodies', {})
        if goodies:
            strGoodies = InvoiceReceivedFormatter.getGoodiesString(goodies)
            if strGoodies:
                result.append(strGoodies)
        blueprints = data.get('blueprints', {})
        if blueprints:
            strBlueprints = InvoiceReceivedFormatter.getBlueprintString(blueprints)
            if strBlueprints:
                result.append(strBlueprints)
        if not asBattleFormatter:
            achievementsNames = cls.__extractAchievements(data)
            if achievementsNames:
                result.append(cls.__makeQuestsAchieve('battleQuestsPopUps', achievements=', '.join(achievementsNames)))
            badgesNames = cls.__extractBadges(data)
            if badgesNames:
                result.append(cls.__makeQuestsAchieve('badgeAchievement', badges=', '.join(badgesNames)))
        return '<br/>'.join(result) if result else None

    @classmethod
    def _processTokens(cls, tokens):
        pass

    @property
    def _templateName(self):
        pass

    @staticmethod
    def __extractAchievements(data):
        achieves = data.get('popUpRecords', [])
        result = set()
        for recordIdx, value in achieves:
            record = DB_ID_TO_RECORD[recordIdx]
            if record[0] == BADGES_BLOCK:
                continue
            factory = getAchievementFactory(record)
            if factory is not None:
                a = factory.create(value=int(value))
                if a is not None:
                    result.add(a.getUserName())

        return result

    @staticmethod
    def __extractBadges(data):
        result = set()
        for block in data.get('dossier', {}).values():
            for record in block.keys():
                if record[0] == BADGES_BLOCK:
                    result.add(backport.text(R.strings.badge.dyn('badge_{}'.format(record[1]))()))

        return result

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
                            _logger.warning('Could not find user name for the badge %s', badge.badgeID)
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
            text = backport.text(R.strings.system_messages.personalMissions.freeAwardListReturn(), count=retAwardListCount)
            result.append(text)
        if newAwardListCount > 0:
            text = backport.text(R.strings.system_messages.personalMissions.freeAwardListGain(), count=newAwardListCount)
            result.append(text)
        for vehIntCD in camouflageGivenFor:
            vehicle = self._itemsCache.items.getItemByCD(vehIntCD)
            text = backport.text(R.strings.system_messages.personalMissions.camouflageGiven(), vehicleName=vehicle.userName)
            result.append(text)

        for vehIntCD in camouflageUnlockedFor:
            vehicle = self._itemsCache.items.getItemByCD(vehIntCD)
            nationName = backport.text(R.strings.menu.nations.dyn(vehicle.nationName)())
            text = backport.text(R.strings.system_messages.personalMissions.camouflageUnlocked(), vehicleName=vehicle.userName, nation=nationName)
            result.append(text)

        if badges:
            text = backport.text(R.strings.system_messages.personalMissions.badge(), name=', '.join(badges))
            result.append(text)
        if tankmenAward:
            result.append(backport.text(R.strings.system_messages.personalMissions.tankmenGain()))
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
                campaignNameKey = 'both' if len(campaigns) == 2 else 'c_{}'.format(first(campaigns))
                templateParams['text'] = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.personalMissions.dyn(campaignNameKey)())
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
        _logger.debug('Message has received from notification center %s', message)
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
                _logger.warning('Type of message is not valid, uses default type %s', msgType)
                msgType = NC_MESSAGE_TYPE.INFO
        else:
            msgType = NC_MESSAGE_TYPE.INFO
        return self.__templateKeyFormat.format(msgType)

    def __getGuiPriority(self, data):
        priority = NC_MESSAGE_PRIORITY.DEFAULT
        if 'priority' in data:
            priority = data['priority']
            if priority not in NC_MESSAGE_PRIORITY.ORDER:
                _logger.warning('Priority of message is not valid, uses default priority %s', priority)
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
            _logger.error('Context is invalid %s', ctx)
            return result
        getItemFormat = NCContextItemFormatter.getItemFormat
        for key, item in ctx.iteritems():
            if len(item) > 1:
                itemType, itemValue = item[0:2]
                result[key] = getItemFormat(itemType, itemValue)
            _logger.error('Context item is invalid %s', item)
            result[key] = str(item)

        return result


class ClanMessageFormatter(ServiceChannelFormatter):
    __templates = {SYS_MESSAGE_CLAN_EVENT.LEFT_CLAN: 'clanMessageWarning'}

    def format(self, message, *args):
        _logger.debug('Message has received from clan %s', message)
        data = message.data
        if data and 'event' in data:
            event = data['event']
            templateKey = self.__templates.get(event)
            fullName = getClanFullName(passCensor(data['clanName']), passCensor(data['clanAbbrev']))
            message = backport.text(R.strings.messenger.serviceChannelMessages.clan.dyn(SYS_MESSAGE_CLAN_EVENT_NAMES[event])())
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
        _logger.debug('Message has received from fort %s', message)
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
            _logger.warning('StrongholdMessageFormatter has no available formatters for given message type: %s', event)
        return []

    def _buildMessage(self, event, ctx=None):
        if ctx is None:
            ctx = {}
        return backport.text(R.strings.messenger.serviceChannelMessages.fort.dyn(SYS_MESSAGE_FORT_EVENT_NAMES[event])(), **ctx)

    def getOrderUserString(self, orderTypeID):
        return backport.text(R.strings.fortifications.orders.dyn(constants.FORT_ORDER_TYPE_NAMES[orderTypeID])())

    def _reserveActivatedMessage(self, data):
        event = data['event']
        orderTypeID = data['orderTypeID']
        expirationTime = data['timeExpiration']
        order = text_styles.neutral(self.getOrderUserString(orderTypeID))
        return self._buildMessage(event, {'order': order,
         'timeLeft': backport.getTillTimeStringByRClass(time_utils.getTimeDeltaFromNow(expirationTime), R.strings.menu.Time.timeValueWithSecs)})

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


class FrontlineExchangeQuestFormatter(TokenQuestsFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data or {}
            templateParams = {}
            rate = {}
            exchangeQ = self._eventsCache.getAllQuests().get(self._FRONTLINE_PRESTIGE_POINTS_EXCHANGE_TEMPLATE)
            if exchangeQ:
                for b in exchangeQ.getBonuses():
                    rate[b.getName()] = b.getValue()

            crystal = data.get(Currency.CRYSTAL, 0)
            if crystal:
                templateParams[Currency.CRYSTAL] = makeHtmlString('html_templates:lobby/battle_results', 'crystal_small_label', {'value': backport.getIntegralFormat(int(crystal))})
                if Currency.CRYSTAL in rate:
                    crystalRate = rate[Currency.CRYSTAL]
                    if crystalRate:
                        templateParams['points'] = int(crystal / crystalRate)
            gold = data.get(Currency.GOLD, 0)
            if gold:
                templateParams[Currency.GOLD] = makeHtmlString('html_templates:lobby/battle_results', 'gold_small_label', {'value': backport.getIntegralFormat(int(gold))})
                if Currency.GOLD in rate and 'points' not in templateParams:
                    goldRate = rate[Currency.GOLD]
                    if goldRate:
                        templateParams['points'] = int(gold / goldRate)
            settings = self._getGuiSettings(message, self._getTemplateName())
            formatted = g_settings.msgTemplates.format(self._getTemplateName(), templateParams)
        callback([_MessageData(formatted, settings)])
        return None

    def _getTemplateName(self):
        pass

    @classmethod
    def __formatAward(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)


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
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            goodieID = message.data.get('gid', None)
            if goodieID is not None:
                booster = self.__goodiesCache.getBooster(goodieID)
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


class TelecomStatusFormatter(WaitItemsSyncFormatter):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def __getVehicleNames(cls, vehTypeCompDescrs):
        itemGetter = cls._itemsCache.items.getItemByCD
        return ', '.join((itemGetter(vehicleCD).userName for vehicleCD in vehTypeCompDescrs))

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            try:
                template = 'telecomVehicleStatus'
                ctx = self.__getMessageContext(message.data)
                settings = self._getGuiSettings(message, template)
                formatted = g_settings.msgTemplates.format(template, ctx, data={'timestamp': time.time()})
            except Exception:
                _logger.error("Can't format telecom status message %s", message)
                _logger.exception('TelecomStatusFormatter catches exception')

        messageData = _MessageData(formatted, settings)
        callback([messageData])
        return None

    @staticmethod
    def __addProviderToRes(res, provider):
        return res.dyn(provider, res.default)

    def __getMessageContext(self, data):
        key = 'vehicleUnblocked' if data['orderStatus'] else 'vehicleBlocked'
        vehTypeDescrs = data['vehTypeCompDescrs']
        provider = ''
        if vehTypeDescrs:
            telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
            provider = telecomConfig.getInternetProvider(list(vehTypeDescrs)[0])
        providerLocName = ''
        if provider:
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            providerLocName = backport.text(providerLocRes.name()) if providerLocRes else ''
        msgctx = {'vehicles': self.__getVehicleNames(vehTypeDescrs),
         'provider': providerLocName}
        ctx = {}
        resShortcut = R.strings.system_messages.telecom
        for txtBlock in ('title', 'comment', 'subcomment'):
            ctx[txtBlock] = backport.text(self.__addProviderToRes(resShortcut.notifications.dyn(key).dyn(txtBlock), provider)(), **msgctx)

        return ctx


class TelecomReceivedInvoiceFormatter(InvoiceReceivedFormatter):
    _lobbyContext = dependency.descriptor(ILobbyContext)

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

    @staticmethod
    def _addProviderToRes(res, provider):
        return res.dyn(provider, res.default)

    @classmethod
    def _getProvider(cls, data):
        provider = ''
        if 'data' in data and 'vehicles' in data['data']:
            vehicles = data['data']['vehicles']
            for vehCompDescr in vehicles.iterkeys():
                if cls._isValidCD(vehCompDescr):
                    telecomConfig = cls._lobbyContext.getServerSettings().telecomConfig
                    return telecomConfig.getInternetProvider(abs(vehCompDescr))

        return provider

    @classmethod
    def _isValidCD(cls, vehCompDescr):
        return vehCompDescr > 0

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
        msgctx = {}
        hasCrew = self.invoiceHasCrew(data)
        if hasCrew:
            if self.invoiceHasBrotherhood(data):
                skills = ' (%s)' % backport.text(R.strings.item_types.tankman.skills.brotherhood())
            else:
                skills = ''
            msgctx['crew'] = backport.text(self._addProviderToRes(R.strings.system_messages.telecom.notifications.vehicleReceived.crew, self._getProvider(data)), skills=skills)
        else:
            msgctx['crew'] = ''
        msgctx['vehicles'] = ', '.join(vehicleNames)
        msgctx['datetime'] = self._getOperationTimeString(data)
        ctx = {}
        resShortcut = R.strings.system_messages.telecom.notifications.vehicleReceived
        for txtBlock in ('title', 'comment', 'subcomment'):
            ctx[txtBlock] = backport.text(self._addProviderToRes(resShortcut.dyn(txtBlock), self._getProvider(data))(), **msgctx)

        return ctx

    def _formatData(self, assetType, data):
        vehicleNames = self._getVehicles(data)
        return None if not vehicleNames else g_settings.msgTemplates.format(self._getMessageTemplateKey(data), ctx=self._getMessageContext(data, vehicleNames), data={'timestamp': time.time()})


class TelecomRemovedInvoiceFormatter(TelecomReceivedInvoiceFormatter):

    @classmethod
    def _isValidCD(cls, vehCompDescr):
        return vehCompDescr < 0

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
        provider = self._getProvider(data)
        providerLocTariff = ''
        if provider != '':
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            providerLocTariff = backport.text(providerLocRes.tariff()) if providerLocRes else ''
        msgctx = {'vehicles': ', '.join(vehicleNames),
         'datetime': self._getOperationTimeString(data),
         'tariff': providerLocTariff}
        ctx = {}
        resShortcut = R.strings.system_messages.telecom.notifications.vehicleRemoved
        for txtBlock in ('title', 'comment', 'subcomment'):
            ctx[txtBlock] = backport.text(self._addProviderToRes(resShortcut.dyn(txtBlock), provider)(), **msgctx)

        return ctx


class PrbVehicleKickFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        self.__itemsCache.items.getVehicle(vehInvID)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format('prbVehicleKick', ctx={'vehName': vehicle.userName})
        return [_MessageData(formatted, self._getGuiSettings(message, 'prbVehicleKick'))]


class PrbVehicleMaxSpgKickFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
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


class RankedQuestFormatter(TokenQuestsFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __awardsStyles = {Currency.CREDITS: text_styles.credits,
     Currency.GOLD: text_styles.gold,
     Currency.CRYSTAL: text_styles.crystal}
    __rankAwardsFormatters = ((Currency.CRYSTAL, getBWFormatter(Currency.CRYSTAL)), (Currency.GOLD, getBWFormatter(Currency.GOLD)), (Currency.CREDITS, getBWFormatter(Currency.CREDITS)))
    __seasonAwardsFormatters = (('badge', lambda b: b),
     ('badges', lambda b: b),
     ('style', lambda b: b),
     ('styles', lambda b: b))

    def __init__(self, forToken=False):
        super(RankedQuestFormatter, self).__init__()
        self.__forToken = forToken

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = message.data.get('completedQuestIDs', set())
            if self.__forToken:
                messages = self._formatTokenQuests(completedQuestIDs, message.data.copy())
            else:
                messages = self._formatRankedQuests(completedQuestIDs, message.data.copy())
            callback([ _MessageData(formattedMessage, self._getGuiSettings(message)) for formattedMessage in messages ])
        else:
            callback([_MessageData(None, self._getGuiSettings(message))])
        return

    @classmethod
    def _getRankedTokens(cls, quest):
        for bonus in quest.getBonuses():
            value = bonus.getValue()
            if isinstance(value, dict):
                return value.get(YEAR_POINTS_TOKEN, {}).get('count', 0)

    @classmethod
    def _makeAwardsDict(cls, extraAwards, awards):
        awardsDict = awards.copy()
        awardsDict.update(extraAwards)
        return awardsDict

    @classmethod
    def _packAward(cls, key, value):
        return '{} {}'.format(backport.text(R.strings.system_messages.ranked.notifications.bonusName.dyn(key)()), cls.__awardsStyles.get(key, text_styles.stats)(value))

    @classmethod
    def _packAwards(cls, awardsDict, formattersList):
        result = []
        for awardName, extractor in formattersList:
            award = None
            if awardName in awardsDict:
                award = awardsDict.pop(awardName)
            if award is not None:
                value = extractor(award)
                if value and value != '0':
                    result.append(cls._packAward(awardName, value))

        return result

    @classmethod
    def _packRankAwards(cls, awardsDict):
        result = cls._processTokens(awardsDict)
        result.extend(cls._packAwards(awardsDict, cls.__rankAwardsFormatters))
        otherStr = cls.formatQuestAchieves(awardsDict, asBattleFormatter=False)
        if otherStr:
            result.append(otherStr)
        return _EOL.join(result)

    @classmethod
    def _packSeasonAwards(cls, awardsDict):
        result = list()
        if awardsDict:
            result.extend(cls._packAwards(awardsDict, cls.__seasonAwardsFormatters))
        return _EOL.join(result)

    @classmethod
    def _packSeasonExtra(cls, data):
        extraAwards = dict()
        badges = cls._processBadges(data)
        if len(badges) > 1:
            extraAwards['badges'] = _EOL.join(badges)
        elif badges:
            extraAwards['badge'] = badges[0]
        styles = cls._processStyles(data)
        if len(styles) > 1:
            extraAwards['styles'] = _EOL.join(styles)
        elif styles:
            extraAwards['style'] = styles[0]
        return extraAwards

    @classmethod
    def _processTokensAmount(cls, awardsDict, isPop=True):
        tokens = awardsDict.pop('tokens', None) if isPop else awardsDict.get('tokens', None)
        if tokens is not None and YEAR_POINTS_TOKEN in tokens:
            yearTokens = tokens.get(YEAR_POINTS_TOKEN)
            return yearTokens.get('count', 0)
        else:
            return 0

    @classmethod
    def _processBadges(cls, data):
        result = list()
        for block in data.get('dossier', {}).values():
            for record in block.keys():
                if record[0] == BADGES_BLOCK:
                    result.append(backport.text(R.strings.badge.dyn('badge_{}'.format(record[1]))()))

        return result

    @classmethod
    def _processStyles(cls, data):
        result = list()
        customizations = data.get('customizations', [])
        for customizationItem in customizations:
            customizationType = customizationItem['custType']
            _, itemUserName = _getCustomizationItemData(customizationItem['id'], customizationType)
            if customizationType == 'style':
                result.append(itemUserName)

        return result

    @classmethod
    def _processTokens(cls, awardsDict):
        tokensAmount = cls._processTokensAmount(awardsDict)
        return [backport.text(R.strings.system_messages.ranked.notifications.bonusName.yearPoints(), yearPoints=text_styles.stats(tokensAmount))] if tokensAmount > 0 else []

    def _formatRankedQuests(self, completedQuestIDs, data):
        formattedMessage = None
        formattedRanks = {}
        quests = self.__eventsCache.getHiddenQuests()
        for questID in completedQuestIDs:
            quest = quests.get(questID)
            if quest is not None and quest.isForRank():
                rankID = quest.getRank()
                division = self.__rankedController.getDivision(rankID)
                textID = R.strings.system_messages.ranked.notifications.singleRank.text()
                if division.isQualification():
                    textID = R.strings.system_messages.ranked.notifications.qualificationFinish()
                formattedRanks[rankID] = backport.text(textID, rankName=division.getRankUserName(rankID), divisionName=division.getUserName())

        if formattedRanks:
            formattedMessage = g_settings.msgTemplates.format('rankedRankQuest', ctx={'ranksBlock': _EOL.join([ formattedRanks[key] for key in sorted(formattedRanks) ]),
             'awardsBlock': self._packRankAwards(data)})
        return [formattedMessage]

    def _formatSeasonProgress(self, season, league, isSprinter, data):
        webLeague = self.__rankedController.getLeagueProvider().webLeague
        if webLeague.league == UNDEFINED_LEAGUE_ID:
            webLeague = self.__rankedController.getClientLeague()
        resultStrings = []
        rankedQuests = self.__eventsCache.getRankedQuests(lambda q: q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID() and q.isCompleted())
        rankedQuests = rankedQuests.values()
        if league != UNDEFINED_LEAGUE_ID:
            position = 0
            if webLeague.league == league:
                position = webLeague.position
            resultStrings.append(backport.text(R.strings.system_messages.ranked.notifications.league(), leagueName=text_styles.stats(backport.text(R.strings.system_messages.ranked.notifications.dyn('league{}'.format(league))()))))
            if position > 0:
                resultStrings.append(backport.text(R.strings.system_messages.ranked.notifications.position(), position=text_styles.stats(backport.getNiceNumberFormat(position))))
        else:
            maxRankID = max([ quest.getRank() for quest in rankedQuests ])
            division = self.__rankedController.getDivision(maxRankID)
            resultStrings.append(backport.text(R.strings.system_messages.ranked.notifications.maxRank(), result=text_styles.stats(backport.text(R.strings.system_messages.ranked.notifications.maxRankResult(), rankName=division.getRankUserName(maxRankID), divisionName=division.getUserName()))))
        if isSprinter:
            if league == TOP_LEAGUE_ID:
                sprinterTextID = R.strings.system_messages.ranked.notifications.sprinterTop()
            else:
                sprinterTextID = R.strings.system_messages.ranked.notifications.sprinterImproved()
            resultStrings.append(backport.text(sprinterTextID))
        tokenForLeague = self._processTokensAmount(data, isPop=False)
        if tokenForLeague > 0:
            resultStrings.append(backport.text(R.strings.system_messages.ranked.notifications.leaguePoints(), points=text_styles.stats(tokenForLeague)))
        resultStrings.append(backport.text(R.strings.system_messages.ranked.notifications.seasonPoints(), points=text_styles.stats(sum([ self._getRankedTokens(quest) for quest in rankedQuests ]) + tokenForLeague)))
        return _EOL.join(resultStrings)

    def _formatTokenQuests(self, completedQuestIDs, data):
        formattedMessages = []
        quests = self.__eventsCache.getHiddenQuests()
        for questID in completedQuestIDs:
            quest = quests.get(questID)
            if quest is not None:
                if ranked_helpers.isSeasonTokenQuest(questID):
                    seasonID, league, isSprinter = ranked_helpers.getDataFromSeasonTokenQuestID(questID)
                    season = self.__rankedController.getSeason(seasonID)
                    if season is not None:
                        isMastered = league != UNDEFINED_LEAGUE_ID
                        seasonProgress = self._formatSeasonProgress(season, league, isSprinter, data)
                        extraAwards = self._packSeasonExtra(data) if isMastered else {}
                        formattedMessages.append(g_settings.msgTemplates.format('rankedSeasonQuest', ctx={'title': backport.text(R.strings.system_messages.ranked.notifications.seasonResults(), seasonNumber=season.getUserName()),
                         'seasonProgress': seasonProgress,
                         'awardsBlock': self._packSeasonAwards(extraAwards)}, data={'savedData': {'quest': quest,
                                       'awards': data}}))

        return formattedMessages


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


class CustomizationChangedFormatter(WaitItemsSyncFormatter):
    _template = 'CustomizationRemoved'

    @async
    @process
    def format(self, message, callback=None):
        from gui.customization.shared import SEASON_TYPE_TO_NAME
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            vehicleIntCD = first(data)
            vehicleData = data[vehicleIntCD]
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            data = {'savedData': {'vehicleIntCD': vehicleIntCD}}
            text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.removeCustomizations(), vehicle=vehicle.userName)
            for season, seasonData in vehicleData.iteritems():
                items = []
                for itemIntCD, count in seasonData.iteritems():
                    item = self._itemsCache.items.getItemByCD(itemIntCD)
                    formattedItem = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizations.item(), itemType=item.userType, itemName=item.userName, count=count)
                    items.append(formattedItem)

                if items:
                    seasonName = SEASON_TYPE_TO_NAME.get(season)
                    formattedSeason = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizations.map.dyn(seasonName)()) + ', '.join(items) + '.'
                    text += '\n' + formattedSeason

            formatted = g_settings.msgTemplates.format(self._template, {'text': text}, data=data)
            settings = self._getGuiSettings(message, self._template, messageType=message.type)
            settings.showAt = BigWorld.time()
            callback([_MessageData(formatted, settings)])
        else:
            callback([_MessageData(None, None)])
        return


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


class ProgressiveRewardFormatter(WaitItemsSyncFormatter):
    _template = 'ProgressiveRewardMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            if 'rewards' in data and 'level' in data:
                fmt = TokenQuestsFormatter.formatQuestAchieves(data['rewards'], False)
                if fmt:
                    formatted = g_settings.msgTemplates.format(self._template, ctx={'text': fmt})
                    settings = self._getGuiSettings(message, self._template)
                    settings.showAt = BigWorld.time()
                    callback([_MessageData(formatted, settings)])
                else:
                    callback([_MessageData(None, None)])
            else:
                callback([_MessageData(None, None)])
        else:
            callback([_MessageData(None, None)])
        return


class PiggyBankSmashedFormatter(ServiceChannelFormatter):
    _template = 'PiggyBankSmashedMessage'

    def format(self, message, *args):
        if message.data:
            data = message.data
            credits_ = data.get('credits')
            if credits_:
                formatted = g_settings.msgTemplates.format(self._template, {'credits': backport.getIntegralFormat(credits_)})
                return [_MessageData(formatted, self._getGuiSettings(message, self._template))]


class BlackMapRemovedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'BlackMapRemovedMessage'
    __REASONS_SETTINGS = {MapRemovedFromBLReason.MAP_DISABLED: {'text': R.strings.messenger.serviceChannelMessages.blackMapRemoved.mapDisabled(),
                                           'priority': NC_MESSAGE_PRIORITY.MEDIUM},
     MapRemovedFromBLReason.SLOT_DISABLED: {'text': R.strings.messenger.serviceChannelMessages.blackMapRemoved.slotDisabled(),
                                            'priority': NC_MESSAGE_PRIORITY.LOW}}

    def format(self, message, *args):
        if message.data:
            mapIDs = message.data.get('mapIDs')
            reason = message.data.get('reason')
            if mapIDs is None or reason not in self.__REASONS_SETTINGS:
                return [_MessageData(None, None)]
            mapNames = []
            for mapID in mapIDs:
                if mapID in ArenaType.g_cache:
                    mapNames.append(i18n.makeString(ArenaType.g_cache[mapID].name))

            settings = self.__REASONS_SETTINGS[reason]
            text = backport.text(settings['text'], mapNames=','.join(mapNames))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=settings['priority'])
            return [_MessageData(formatted, guiSettings)]
        else:
            return [_MessageData(None, None)]
