# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel.py
import logging
import operator
import time
import types
from Queue import Queue
from collections import defaultdict
import typing
import ArenaType
import BigWorld
import constants
import nations
import personal_missions
from adisp import async, process
from battle_pass_common import BATTLE_PASS_BADGE_ID, BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS, BATTLE_PASS_TOKEN_3D_STYLE, BattlePassRewardReason, FinalReward
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from cache import cached_property
from chat_shared import MapRemovedFromBLReason, SYS_MESSAGE_TYPE, decompressSysMessage
from constants import ARENA_GUI_TYPE, AUTO_MAINTENANCE_RESULT, AUTO_MAINTENANCE_TYPE, FINISH_REASON, INVOICE_ASSET, KICK_REASON, KICK_REASON_NAMES, NC_MESSAGE_PRIORITY, NC_MESSAGE_TYPE, OFFER_TOKEN_PREFIX, PREBATTLE_TYPE, PREMIUM_ENTITLEMENTS, PREMIUM_TYPE, SYS_MESSAGE_CLAN_EVENT, SYS_MESSAGE_CLAN_EVENT_NAMES, SYS_MESSAGE_FORT_EVENT_NAMES
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from goodies.goodie_constants import GOODIE_VARIETY
from gui import GUI_NATIONS, GUI_SETTINGS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.SystemMessages import SM_TYPE
from gui.clans.formatters import getClanFullName
from gui.dog_tag_composer import dogTagComposer
from gui.game_control.blueprints_convert_sale_controller import BCSActionState
from gui.game_control.dragon_boat_controller import DBOAT_POINTS
from gui.impl import backport
from gui.impl.gen import R
from gui.mapbox.mapbox_helpers import formatMapboxRewards
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.ranked_battles.constants import YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX, YEAR_POINTS_TOKEN
from gui.ranked_battles.ranked_helpers import getBonusBattlesIncome, getQualificationBattlesCountFromID, isQualificationQuestID
from gui.ranked_battles.ranked_models import PostBattleRankInfo, RankChangeStates
from gui.server_events.awards_formatters import CompletionTokensBonusFormatter
from gui.server_events.bonuses import DEFAULT_CREW_LVL, EntitlementBonus, MetaBonus, VehiclesBonus, getMergedBonusesFromDicts
from gui.server_events.finders import PERSONAL_MISSION_TOKEN
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import formatters as shared_fmts
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import applyAll, getBWFormatter, getStyle
from gui.shared.formatters.time_formatters import RentDurationKeys, getTillTimeByResource, getTimeLeftInfo
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import getShortUserName, getUserName
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.money import Currency, MONEY_UNDEFINED, Money, ZERO_MONEY
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel
from gui.shared.utils.requesters.ShopRequester import _NamedGoodieData
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID, getUniqueBlueprints
from gui.shared.utils.transport import z_loads
from helpers import dependency, getLocalizedData, html, i18n, int2roman, time_utils
from items import ITEM_TYPES as I_T, getTypeInfoByIndex, getTypeInfoByName, tankmen, vehicles as vehicles_core
from items.components.c11n_constants import UNBOUND_VEH_KEY
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from maps_training_common.maps_training_constants import SCENARIO_INDEXES, SCENARIO_RESULT
from messenger import g_settings
from messenger.ext import passCensor
from messenger.formatters import NCContextItemFormatter, TimeFormatter
from messenger.formatters.service_channel_helpers import EOL, MessageData, getCustomizationItemData, getRewardsForQuests, mergeRewards
from nations import NAMES
from shared_utils import BoundMethodWeakref, first
from skeletons.gui.game_control import IBattlePassController, IBattleRoyaleController, IMapboxController, IRankedBattlesController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Tuple
    from account_helpers.offers.events_data import OfferEventData, OfferGift
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from messenger.proto.bw.wrappers import ServiceChannelMessage
_logger = logging.getLogger(__name__)
_TEMPLATE = 'template'
_RENT_TYPE_NAMES = {RentDurationKeys.DAYS: 'rentDays',
 RentDurationKeys.BATTLES: 'rentBattles',
 RentDurationKeys.WINS: 'rentWins'}
_PREMIUM_MESSAGES = {PREMIUM_TYPE.BASIC: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumBought(),
                      str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumExtended(),
                      str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumExpired(),
                      str(SYS_MESSAGE_TYPE.premiumChanged): R.strings.messenger.serviceChannelMessages.premiumChanged()},
 PREMIUM_TYPE.PLUS: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumPlusBought(),
                     str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumPlusExtended(),
                     str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumPlusExpired(),
                     str(SYS_MESSAGE_TYPE.premiumChanged): R.strings.messenger.serviceChannelMessages.premiumPlusChanged()}}
_PREMIUM_TEMPLATES = {PREMIUM_ENTITLEMENTS.BASIC: 'battleQuestsPremium',
 PREMIUM_ENTITLEMENTS.PLUS: 'battleQuestsPremiumPlus'}
_PROGRESSION_INVOICE_POSTFIX = 'progression'
BATTLE_BONUS_X5_TOKEN = 'battle_bonus_x5'

def _getTimeStamp(message):
    if message.createdAt is not None:
        result = time_utils.getTimestampFromUTC(message.createdAt.timetuple())
    else:
        result = time_utils.getCurrentTimestamp()
    return result


def _extendCustomizationData(newData, extendable, htmlTplPostfix):
    if extendable is None:
        return
    else:
        customizations = newData.get('customizations', [])
        for customizationItem in customizations:
            splittedCustType = customizationItem.get('custType', '').split(':')
            custType = splittedCustType[0]
            custValue = customizationItem['value']
            if len(splittedCustType) == 2 and _PROGRESSION_INVOICE_POSTFIX in splittedCustType[1]:
                continue
            if custValue > 0:
                operation = 'added'
            elif custValue < 0:
                operation = 'removed'
            else:
                operation = None
            if operation is not None:
                guiItemType, itemUserName = getCustomizationItemData(customizationItem['id'], custType)
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


def _getRareAchievements(dossiers):
    rares = []
    for d in dossiers.itervalues():
        it = d if not isinstance(d, dict) else d.iteritems()
        for (blck, _), rec in it:
            if blck == ACHIEVEMENT_BLOCK.RARE:
                rares.append(rec['value'])

    return rares


def _toPairLists(dct):
    return [ [k, v] for k, v in dct.iteritems() ]


def _composeAchievements(dossiers):
    result = {}
    for dossierKey, rec in dossiers.iteritems():
        uniqueReceived, uniqueRemoved, other = {}, {}, []
        it = rec if not isinstance(rec, dict) else rec.iteritems()
        for recType, recData in it:
            value = recData['value']
            if value == 0:
                continue
            updated = uniqueReceived if value > 0 else uniqueRemoved
            _updateUnique(recType, recData, updated, other)

        result[dossierKey] = _toPairLists(uniqueReceived) + _toPairLists(uniqueRemoved) + other

    return result


def _updateUnique(recType, recData, uniqueAchieves, nonMerged):
    if recType not in uniqueAchieves:
        uniqueAchieves[recType] = recData
        return
    savedRecData = uniqueAchieves[recType]
    if savedRecData['type'] == recData['type']:
        savedRecData['value'] += recData['value']
        savedActualValue = savedRecData['actualValue']
        updateFunc = max if recData['value'] > 0 else min
        savedRecData['actualValue'] = updateFunc(savedActualValue, recData['actualValue'])
    else:
        nonMerged.append([recType, recData])


def _getFormatAchieveString(name, block, recData):
    if 'actualValue' in recData:
        achieve = getAchievementFactory((block, name)).create(recData['actualValue'])
    else:
        achieve = None
        _logger.warning("Couldn't find 'actualValue' field in data %s", recData)
    if achieve is not None:
        achieveName = achieve.getUserName()
    else:
        achieveName = backport.text(R.strings.achievements.dyn(name)())
    value = abs(recData['value'])
    return ''.join((achieveName, backport.text(R.strings.messenger.serviceChannelMessages.multiplier(), count=backport.getIntegralFormat(value)))) if value > 1 else achieveName


def _getRaresAchievementsStrings(battleResults):
    dossiers = battleResults.get('dossier', {})
    rares = []
    for d in dossiers.itervalues():
        it = d if not isinstance(d, dict) else d.iteritems()
        for (blck, _), rec in it:
            if blck == ACHIEVEMENT_BLOCK.RARE:
                value = rec['value']
                if value > 0:
                    rares.append(value)

    return _processRareAchievements(rares) if rares else None


def _getCrewBookUserString(itemDescr):
    params = {}
    if itemDescr.type not in CREW_BOOK_RARITY.NO_NATION_TYPES:
        params['nation'] = i18n.makeString('#nations:{}'.format(itemDescr.nation))
    return i18n.makeString(itemDescr.name, **params)


def _getAchievementsFromQuestData(data):
    achievesList = []
    for rec in data.get('dossier', {}).values():
        it = rec if not isinstance(rec, dict) else rec.iteritems()
        for (block, name), value in it:
            if block not in ACHIEVEMENT_BLOCK.ALL:
                continue
            achieve = getAchievementFactory((block, name)).create(value.get('actualValue', 0))
            if achieve is not None:
                achievesList.append(achieve.getUserName())
            achievesList.append(backport.text(R.strings.achievements.dyn(name)()))

    return achievesList


def _processTankmanToken(tokenName):
    if tokenName.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
        tankmanInfo = getRecruitInfo(tokenName)
        if tankmanInfo is not None:
            rBattlePass = R.strings.battle_pass
            text = backport.text(rBattlePass.universalTankmanBonus(), name=tankmanInfo.getFullUserName())
            return g_settings.htmlTemplates.format('battlePassTMan', {'text': text})
    return


@dependency.replace_none_kwargs(offersProvider=IOffersDataProvider)
def _processOfferToken(tokenName, offersProvider=None):
    if tokenName.startswith(OFFER_TOKEN_PREFIX):
        offers = offersProvider.getAvailableOffersByToken(tokenName)
        if offers:
            text = backport.text(R.strings.messenger.serviceChannelMessages.offerTokenBonus.title())
            return g_settings.htmlTemplates.format('offerTokenText', {'text': text})
    return None


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
            try:
                self.__callbackQueue.get_nowait()(self._itemsCache.isSynced())
            except Exception:
                _logger.exception('Exception in service channel formatter')

        self.__unregisterHandler()


class ServerRebootFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverReboot', ctx={'date': local_dt.strftime('%c')})
            return [MessageData(formatted, self._getGuiSettings(message, 'serverReboot'))]
        else:
            return [MessageData(None, None)]


class ServerRebootCancelledFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format('serverRebootCancelled', ctx={'date': local_dt.strftime('%c')})
            return [MessageData(formatted, self._getGuiSettings(message, 'serverRebootCancelled'))]
        else:
            return [MessageData(None, None)]


class FormatSpecialReward(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def getString(self, message):
        formattedItems = self.__formattedItems(message)
        return None if not formattedItems else g_settings.msgTemplates.format('specialReward', ctx={'specialRewardItems': formattedItems})

    def __formattedItems(self, message):
        data = message.data
        itemsNames = []
        itemsNames.extend(self.__getCrewBookNames(data.get('items', {})))
        itemsNames.extend(self.__getBlueprintNames(data.get('blueprints', {})))
        return None if not itemsNames else g_settings.htmlTemplates.format('specialRewardItems', ctx={'names': '<br/>'.join(itemsNames)})

    def __getCrewBookNames(self, items):
        result = []
        if not self.__lobbyContext.getServerSettings().isCrewBooksEnabled():
            return result
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            if itemTypeID != I_T.crewBook:
                continue
            itemDescr = tankmen.getItemByCompactDescr(intCD)
            name = _getCrewBookUserString(itemDescr)
            result.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(count)))

        return result

    def __getBlueprintNames(self, blueprints):
        vehicleFragments, nationFragments, universalFragments = getUniqueBlueprints(blueprints)
        result = []
        for fragmentCD, count in vehicleFragments.iteritems():
            fragmentsCount = backport.getIntegralFormat(count)
            vehicleName = getUserName(vehicles_core.getVehicleType(abs(fragmentCD)))
            result.append(backport.text(R.strings.messenger.serviceChannelMessages.specialReward.vehicleBlueprints(), vehicleName=vehicleName, fragmentsCount=fragmentsCount))

        for nationID, count in nationFragments.iteritems():
            fragmentsCount = backport.getIntegralFormat(count)
            nationName = backport.text(R.strings.nations.dyn(NAMES[nationID])())
            result.append(backport.text(R.strings.messenger.serviceChannelMessages.specialReward.nationalBlueprints(), nationName=nationName, fragmentsCount=fragmentsCount))

        if universalFragments:
            fragmentsCount = backport.getIntegralFormat(universalFragments)
            result.append(backport.text(R.strings.messenger.serviceChannelMessages.specialReward.intelligenceBlueprints(), fragmentsCount=fragmentsCount))
        return result


class BattleResultsFormatter(WaitItemsSyncFormatter):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __battleResultKeys = {-1: 'battleDefeatResult',
     0: 'battleDrawGameResult',
     1: 'battleVictoryResult'}
    __BRResultKeys = {-1: 'battleRoyaleDefeatResult',
     0: 'battleRoyaleDefeatResult',
     1: 'battleRoyaleVictoryResult'}
    __MTResultKeys = {SCENARIO_RESULT.LOSE: 'mapsTrainingDefeatResult',
     SCENARIO_RESULT.WIN: 'mapsTrainingVictoryResult'}
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
                accEventCoin = battleResults.get(Currency.EVENT_COIN)
                ctx['eventCoinStr'] = ''
                if accEventCoin:
                    ctx[Currency.EVENT_COIN] = self.__makeCurrencyString(Currency.EVENT_COIN, accEventCoin)
                    ctx['eventCoinStr'] = g_settings.htmlTemplates.format('battleResultEventCoin', {Currency.EVENT_COIN: ctx[Currency.EVENT_COIN]})
                accBpcoin = battleResults.get(Currency.BPCOIN)
                ctx['bpcoinStr'] = ''
                if accBpcoin:
                    ctx[Currency.BPCOIN] = self.__makeCurrencyString(Currency.BPCOIN, accBpcoin)
                    ctx['bpcoinStr'] = g_settings.htmlTemplates.format('battleResultBpcoin', {Currency.BPCOIN: ctx[Currency.BPCOIN]})
                ctx['creditsEx'] = self.__makeCreditsExString(accCredits, battleResults.get('creditsPenalty', 0), battleResults.get('creditsContributionIn', 0), battleResults.get('creditsContributionOut', 0))
                platformCurrencies = battleResults.get('currencies', {})
                if platformCurrencies:
                    ctx['platformCurrencyStr'] = '<br/>' + '<br/>'.join((g_settings.htmlTemplates.format('platformCurrency', {'msg': backport.text(R.strings.messenger.platformCurrencyMsg.received.dyn(currency)()),
                     'count': backport.getIntegralFormat(countDict.get('count', 0))}) for currency, countDict in platformCurrencies.iteritems()))
                else:
                    ctx['platformCurrencyStr'] = ''
                guiType = battleResults.get('guiType', 0)
                ctx['achieves'], ctx['badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
                ctx['rankedProgress'] = self.__makeRankedFlowStrings(battleResults)
                ctx['rankedBonusBattles'] = self.__makeRankedBonusString(battleResults)
                ctx['battlePassProgress'] = self.__makeBattlePassProgressionString(guiType, battleResults)
                ctx['lock'] = self.__makeVehicleLockString(vehicleNames, battleResults)
                ctx['quests'] = self.__makeQuestsAchieve(message)
                ctx['DBPointsStr'] = self.__makeDragonBoatPointsString(battleResults)
                team = battleResults.get('team', 0)
                if guiType == ARENA_GUI_TYPE.FORT_BATTLE_2 or guiType == ARENA_GUI_TYPE.SORTIE_2:
                    if battleResKey == 0:
                        winnerIfDraw = battleResults.get('winnerIfDraw')
                        if winnerIfDraw:
                            battleResKey = 1 if winnerIfDraw == team else -1
                if guiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
                    ctx['brcoin'] = self.__makeBRCoinString(battleResults)
                    battleResultKeys = self.__BRResultKeys
                elif guiType == ARENA_GUI_TYPE.MAPS_TRAINING:
                    ctx = self.__makeMapsTrainingMsgCtx(battleResults, ctx)
                    battleResKey = battleResults.get('mtScenarioResult')
                    battleResultKeys = self.__MTResultKeys
                else:
                    battleResultKeys = self.__battleResultKeys
                templateName = battleResultKeys[battleResKey]
                bgIconSource = None
                arenaUniqueID = battleResults.get('arenaUniqueID', 0)
                formatted = g_settings.msgTemplates.format(templateName, ctx=ctx, data={'timestamp': arenaCreateTime,
                 'savedData': arenaUniqueID}, bgIconSource=bgIconSource)
                formattedSpecialReward = FormatSpecialReward().getString(message)
                settings = self._getGuiSettings(message, templateName)
                settings.showAt = BigWorld.time()
                messages = list()
                if formattedSpecialReward:
                    messages.append(MessageData(formattedSpecialReward, settings))
                messages.append(MessageData(formatted, settings))
                callback(messages)
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return

    def __makeMapsTrainingMsgCtx(self, battleResults, ctx):
        vehTypeCompDescr = next(battleResults['playerVehicles'].iterkeys())
        vType = vehicles_core.getVehicleType(vehTypeCompDescr)
        vehicleClass = vehicles_core.getVehicleClassFromVehicleType(vType)
        team = battleResults['team']
        vehTypeStr = backport.text(R.strings.maps_training.vehicleType.dyn(vehicleClass)())
        ctx['baseStr'] = backport.text(R.strings.maps_training.baseNum()).format(base=team)
        ctx['mtRewards'] = self.__makeMapsTrainingRewardsMsg(battleResults)
        ctx['scenario'] = backport.text(R.strings.maps_training.scenarioTooltip.scenario.title()).format(num=SCENARIO_INDEXES[team, vehicleClass], vehicleType=vehTypeStr)
        return ctx

    def __makeMapsTrainingRewardsMsg(self, battleResults):
        if not battleResults.get('mtCanGetRewards'):
            return g_settings.htmlTemplates.format('mtRewardGot')
        rewards = []
        creditsReward = battleResults.get('credits', 0)
        creditsXMLString = 'mtCreditsHighlight' if creditsReward else 'mtCredits'
        rewards.append(g_settings.htmlTemplates.format(creditsXMLString, ctx={'credits': self.__makeCurrencyString(Currency.CREDITS, creditsReward)}))
        freeXP = battleResults.get('freeXP', 0)
        if freeXP:
            rewards.append(g_settings.htmlTemplates.format('mtFreeXP', ctx={'freeXP': backport.getIntegralFormat(freeXP)}))
        questResults = QuestAchievesFormatter.formatQuestAchieves(battleResults, asBattleFormatter=True)
        if questResults:
            rewards.append(g_settings.htmlTemplates.format('mtQuests', ctx={'quests': questResults}))
        return '<br/>'.join(rewards)

    def __makeQuestsAchieve(self, message):
        fmtMsg = QuestAchievesFormatter.formatQuestAchieves(message.data, asBattleFormatter=True)
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
                if achieve is not None and achieve not in popUpRecords:
                    popUpRecords.append(achieve)

            if 'markOfMastery' in vehBattleResults and vehBattleResults['markOfMastery'] > 0:
                popUpRecords.append(getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, 'markOfMastery')).create(value=vehBattleResults['markOfMastery']))

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

    def __makeRankedFlowStrings(self, battleResults):
        rankedProgressStrings = []
        if battleResults.get('guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            stateChange = self.__rankedController.getRankChangeStatus(rankInfo)
            if stateChange in (RankChangeStates.QUAL_EARNED, RankChangeStates.QUAL_UNBURN_EARNED):
                stateChange = RankChangeStates.DIVISION_EARNED
            shortcut = R.strings.messenger.serviceChannelMessages.battleResults
            stateChangeResID = shortcut.rankedState.dyn(stateChange)()
            if stateChange == RankChangeStates.DIVISION_EARNED:
                divisionNumber = backport.text(shortcut.divisions.dyn(self.__rankedController.getDivision(rankInfo.accRank + 1).getUserID())())
                stateChangeStr = backport.text(stateChangeResID, divisionNumber=divisionNumber)
            elif stateChange in (RankChangeStates.RANK_LOST, RankChangeStates.RANK_EARNED):
                rankID = rankInfo.prevAccRank
                if stateChange == RankChangeStates.RANK_EARNED:
                    rankID = rankInfo.accRank
                division = self.__rankedController.getDivision(rankID)
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
        bonusBattlesString = ''
        if battleResults.get('guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            stateChange = self.__rankedController.getRankChangeStatus(rankInfo)
            bonusBattlesString = getBonusBattlesIncome(R.strings.messenger.serviceChannelMessages.battleResults.rankedBonusBattles, rankInfo.stepsBonusBattles, rankInfo.efficiencyBonusBattles, stateChange == RankChangeStates.LEAGUE_EARNED)
        dailyBattles = battleResults.get('rankedDailyBattles', 0)
        persistBattles = battleResults.get('rankedBonusBattles', 0)
        questsBonusBattlesString = InvoiceReceivedFormatter.getRankedBonusBattlesString(persistBattles, dailyBattles)
        if questsBonusBattlesString:
            questsStrRes = R.strings.messenger.serviceChannelMessages.battleResults.rankedBonusBattles.quests()
            questsBonusBattlesString = backport.text(questsStrRes, bonusBattles=questsBonusBattlesString)
            bonusBattlesString = text_styles.concatStylesToSingleLine(bonusBattlesString, questsBonusBattlesString)
        rankedBonusBattlesBlock = ''
        if bonusBattlesString:
            rankedBonusBattlesBlock = g_settings.htmlTemplates.format('battleResultRankedBonusBattles', {'rankedBonusBattles': bonusBattlesString})
        return rankedBonusBattlesBlock

    def __makeBattlePassProgressionString(self, guiType, battleResults):
        battlePassString = ''
        value = sum((points for points in battleResults.get('battlePassPoints', {}).get('vehicles', {}).itervalues()))
        value += battleResults.get('basePointsDiff', 0)
        if value > 0:
            if guiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
                bonusType = battleResults.get('bonusType', 0)
                if self.__battleRoyaleController.isBattlePassAvailable(bonusType):
                    battlePassString = backport.text(R.strings.messenger.serviceChannelMessages.BRbattleResults.battlePass(), pointsDiff=text_styles.neutral(value))
            else:
                battlePassString = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.battlePass(), pointsDiff=text_styles.neutral(value))
        return '' if not battlePassString else g_settings.htmlTemplates.format('battlePass', ctx={'battlePassProgression': battlePassString})

    def __makePiggyBankString(self, credits_):
        return '' if not credits_ else g_settings.htmlTemplates.format('piggyBank', ctx={'credits': self.__makeCurrencyString(Currency.CREDITS, credits_)})

    def __makeBRCoinString(self, battleResults):
        value = battleResults.get('brcoin', 0)
        if value:
            text = backport.text(R.strings.messenger.serviceChannelMessages.BRbattleResults.battleRoyaleBrCoin(), value=text_styles.neutral(value))
            return g_settings.htmlTemplates.format('battleResultBrcoin', ctx={'brcoin': text})

    def __makeDragonBoatPointsString(self, battleResults):
        points = battleResults.get('tokens', {}).get(DBOAT_POINTS, {}).get('count', 0)
        return '' if not points else g_settings.htmlTemplates.format('battleResultDBPoints', ctx={'DBPoints': points})


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
     Currency.CRYSTAL: 'PurchaseForCrystalSysMessage',
     Currency.EVENT_COIN: 'PurchaseForEventCoinSysMessage',
     Currency.BPCOIN: 'PurchaseForBpcoinSysMessage'}

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
                            msgArgs = (vehName, styleName, style.rentCount)
                        else:
                            msgArgs = (styleName, vehName)
                else:
                    vehName = vehicle.userName
                    msgArgs = (vehName,)
                if msgArgs is not None:
                    msgTmpl = backport.text(msgTmplKey)
                    if not msgTmpl:
                        _logger.warning('Invalid typeID field in message: %s', message)
                        callback([MessageData(None, None)])
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
                elif result == AUTO_MAINTENANCE_RESULT.DISABLED_OPTION:
                    templateName = 'ErrorSysMessage'
                else:
                    templateName = 'WarningSysMessage'
                if result == AUTO_MAINTENANCE_RESULT.OK:
                    msg += shared_fmts.formatPrice(cost.toAbs(), ignoreZeros=True) + '.'
                formatted = g_settings.msgTemplates.format(templateName, {'text': msg}, data=data)
                settings = self._getGuiSettings(message, priorityLevel=priorityLevel, messageType=message.type, messageSubtype=result)
                callback([MessageData(formatted, settings)])
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
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
            callback([MessageData(None, None)])
            return
        else:
            formatted = g_settings.msgTemplates.format('achievementReceived', {'achieves': ', '.join(achievesList)})
            if badgesList:
                badgesBlock = g_settings.htmlTemplates.format('badgeAchievement', {'badges': ', '.join(badgesList)})
                formatted = EOL.join([formatted, badgesBlock])
            callback([MessageData(formatted, self._getGuiSettings(message, 'achievementReceived'))])
            return


class CurrencyUpdateFormatter(ServiceChannelFormatter):
    _EMITTER_ID_TO_TITLE = {2525: R.strings.messenger.serviceChannelMessages.currencyUpdate.auction(),
     2524: R.strings.messenger.serviceChannelMessages.currencyUpdate.battlepass()}
    _DEFAULT_TITLE = R.strings.messenger.serviceChannelMessages.currencyUpdate.financial_transaction()

    def format(self, message, *args):
        data = message.data
        currencyCode = data['currency_name']
        amountDelta = data['amount_delta']
        transactionTime = data['date']
        emitterID = data.get('emitterID')
        if currencyCode and amountDelta and transactionTime:
            xmlKey = 'currencyUpdate'
            formatted = g_settings.msgTemplates.format(xmlKey, ctx={'title': backport.text(self._EMITTER_ID_TO_TITLE.get(emitterID, self._DEFAULT_TITLE)),
             'date': TimeFormatter.getLongDatetimeFormat(transactionTime),
             'currency': self.__getCurrencyString(currencyCode, amountDelta),
             'amount': getStyle(currencyCode)(getBWFormatter(currencyCode)(abs(amountDelta)))}, data={'icon': currencyCode.title() + 'Icon'})
            return [MessageData(formatted, self._getGuiSettings(message, xmlKey))]
        else:
            return [MessageData(None, None)]

    def __ifPlatformCurrency(self, currencyCode):
        return currencyCode not in Currency.ALL

    def __getCurrencyString(self, currencyCode, amountDelta):
        return backport.text(R.strings.messenger.platformCurrencyMsg.dyn('debited' if amountDelta < 0 else 'received').dyn(currencyCode)()) if self.__ifPlatformCurrency(currencyCode) else backport.text(R.strings.messenger.serviceChannelMessages.currencyUpdate.dyn('debited' if amountDelta < 0 else 'received').dyn(currencyCode)())


class GiftReceivedFormatter(ServiceChannelFormatter):
    __handlers = {'money': ('_GiftReceivedFormatter__formatMoneyGiftMsg', {1: 'creditsReceivedAsGift',
                2: 'goldReceivedAsGift',
                3: 'creditsAndGoldReceivedAsGift',
                8: 'eventCoinReceivedAsGift'}),
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
                return [MessageData(formatted, self._getGuiSettings(message, templateKey))]
        return [MessageData(None, None)]

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
    __purchaseCache = dependency.descriptor(IPurchaseCache)
    __assetHandlers = {INVOICE_ASSET.GOLD: '_formatAmount',
     INVOICE_ASSET.CREDITS: '_formatAmount',
     INVOICE_ASSET.CRYSTAL: '_formatAmount',
     INVOICE_ASSET.EVENT_COIN: '_formatAmount',
     INVOICE_ASSET.BPCOIN: '_formatAmount',
     INVOICE_ASSET.PREMIUM: '_formatAmount',
     INVOICE_ASSET.FREE_XP: '_formatAmount',
     INVOICE_ASSET.DATA: '_formatData',
     INVOICE_ASSET.PURCHASE: '_formatPurchase'}
    __currencyToInvoiceAsset = {Currency.GOLD: INVOICE_ASSET.GOLD,
     Currency.CREDITS: INVOICE_ASSET.CREDITS,
     Currency.CRYSTAL: INVOICE_ASSET.CRYSTAL,
     Currency.EVENT_COIN: INVOICE_ASSET.EVENT_COIN,
     Currency.BPCOIN: INVOICE_ASSET.BPCOIN}
    __operationTemplateKeys = {INVOICE_ASSET.GOLD: 'goldAccruedInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsAccruedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: 'crystalAccruedInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN: 'eventCoinAccruedInvoiceReceived',
     INVOICE_ASSET.BPCOIN: 'bpcoinAccruedInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumAccruedInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpAccruedInvoiceReceived',
     INVOICE_ASSET.GOLD | 16: 'goldDebitedInvoiceReceived',
     INVOICE_ASSET.CREDITS | 16: 'creditsDebitedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL | 16: 'crystalDebitedInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN | 16: 'eventCoinDebitedInvoiceReceived',
     INVOICE_ASSET.BPCOIN | 16: 'bpcoinDebitedInvoiceReceived',
     INVOICE_ASSET.PREMIUM | 16: 'premiumDebitedInvoiceReceived',
     INVOICE_ASSET.FREE_XP | 16: 'freeXpDebitedInvoiceReceived'}
    __blueprintsTemplateKeys = {BlueprintTypes.VEHICLE: ('vehicleBlueprintsAccruedInvoiceReceived', 'vehicleBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.NATIONAL: ('nationalBlueprintsAccruedInvoiceReceived', 'nationalBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.INTELLIGENCE_DATA: ('intelligenceBlueprintsAccruedInvoiceReceived', 'intelligenceBlueprintsDebitedInvoiceReceived')}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: 'goldInvoiceReceived',
     INVOICE_ASSET.CREDITS: 'creditsInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: 'crystalInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN: 'eventCoinInvoiceReceived',
     INVOICE_ASSET.BPCOIN: 'bpcoinInvoiceReceived',
     INVOICE_ASSET.PREMIUM: 'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: 'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: 'dataInvoiceReceived',
     INVOICE_ASSET.PURCHASE: 'purchaseInvoiceReceived'}
    __INVALID_TYPE_ASSET = -1
    __auxMessagesHandlers = {INVOICE_ASSET.DATA: 'getInvoiceDataAuxMessages'}
    __DESTROY_PAIR_MODIFICATIONS_MSG_TEMPLATE = 'DestroyAllPairsModifications'
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        mainMassage = MessageData(None, None)
        auxMassages = []
        if isSynced:
            data = message.data
            isDataSynced = yield self.__waitForSyncData(data)
            if isDataSynced:
                self.__prerocessRareAchievements(data)
                assetType = data.get('assetType', self.__INVALID_TYPE_ASSET)
                handler = self.__assetHandlers.get(assetType)
                if handler is not None:
                    formatted = getattr(self, handler)(assetType, data)
                if formatted is not None:
                    settings = self._getGuiSettings(message, self._getMessageTemplateKey(assetType))
            else:
                assetType = self.__INVALID_TYPE_ASSET
                _logger.debug('Message will not be shown!')
            mainMassage = MessageData(formatted, settings)
            auxMessagesHandler = self.__auxMessagesHandlers.get(assetType, None)
            if auxMessagesHandler is not None:
                auxMassages = getattr(self, auxMessagesHandler)(data)
        result = [mainMassage]
        result.extend(auxMassages)
        callback(result)
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
        for vehicleDict in vehicles:
            for vehCompDescr, vehData in vehicleDict.iteritems():
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

        return '<br/>'.join(result) if any(result) else ''

    @classmethod
    def getCustomizationCompensationString(cls, customizationItem, htmlTplPostfix='InvoiceReceived'):
        result = ''
        if 'customCompensation' not in customizationItem:
            return result
        customItemData = getCustomizationItemData(customizationItem['id'], customizationItem['custType'])
        strItemType = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.compensation.dyn(customItemData.guiItemType)())
        comp = Money.makeFromMoneyTuple(customizationItem['customCompensation'])
        result = cls._getCustomizationCompensationString(comp, strItemType, customItemData.userName, customizationItem['compensatedNumber'], htmlTplPostfix)
        return result

    @classmethod
    def getTankmenString(cls, tmen, dismiss=False):
        tmanUserStrings = []
        for tmanData in tmen:
            try:
                if isinstance(tmanData, dict):
                    tankman = Tankman(tmanData['tmanCompDescr'])
                elif isinstance(tmanData, Tankman):
                    tankman = tmanData
                else:
                    tankman = Tankman(tmanData)
                tmanUserStrings.append('{0:s} {1:s} ({2:s}, {3:s}, {4:d}%)'.format(tankman.rankUserName, tankman.lastUserName, tankman.roleUserName, getUserName(tankman.vehicleNativeDescr.type), tankman.roleLevel))
            except Exception:
                _logger.error('Wrong tankman data: %s', tmanData)
                _logger.exception('getTankmenString catch exception')

        result = ''
        if dismiss:
            invoiceStr = 'tankmenInvoiceDismiss'
            tankmanStr = 'tankmenToRemove'
        else:
            invoiceStr = 'tankmenInvoiceReceived'
            tankmanStr = 'tankman'
        if tmanUserStrings:
            result = g_settings.htmlTemplates.format(invoiceStr, ctx={tankmanStr: ', '.join(tmanUserStrings)})
        return result

    @classmethod
    def getGoodiesString(cls, goodies, exclude=None):
        result = []
        boostersStrings = []
        discountsStrings = []
        demountKitStrings = []
        for goodieID, ginfo in goodies.iteritems():
            if exclude is not None and goodieID in exclude:
                continue
            if goodieID in cls._itemsCache.items.shop.boosters:
                booster = cls.__goodiesCache.getBooster(goodieID)
                if booster is not None and booster.enabled:
                    if ginfo.get('count'):
                        boostersStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=booster.userName, count=ginfo.get('count')))
                    else:
                        boostersStrings.append(booster.userName)
            if goodieID in cls._itemsCache.items.shop.discounts:
                discount = cls.__goodiesCache.getDiscount(goodieID)
                if discount is not None and discount.enabled:
                    discountsStrings.append(discount.description)
            if goodieID in cls._itemsCache.items.shop.demountKits:
                dk = cls.__goodiesCache.getDemountKit(goodieID)
                if dk and dk.enabled:
                    if ginfo.get('count'):
                        demountKitStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=dk.userName, count=ginfo.get('count')))
                    else:
                        demountKitStrings.append(dk.userName)

        if boostersStrings:
            result.append(g_settings.htmlTemplates.format('boostersInvoiceReceived', ctx={'boosters': ', '.join(boostersStrings)}))
        if discountsStrings:
            result.append(g_settings.htmlTemplates.format('discountsInvoiceReceived', ctx={'discounts': ', '.join(discountsStrings)}))
        if demountKitStrings:
            result.append(g_settings.htmlTemplates.format('demountKitsInvoiceReceived', ctx={'demountKits': ', '.join(demountKitStrings)}))
        return '; '.join(result)

    @classmethod
    def getEnhancementsString(cls, enhancements):
        added = 0
        removed = 0
        result = []
        for extra in enhancements.itervalues():
            count = extra.get('count', 0)
            if count > 0:
                added += count
            removed += -count

        if added:
            result.append(g_settings.htmlTemplates.format('enhancementsAccruedInvoiceReceived', ctx={'count': added}))
        if removed:
            result.append(g_settings.htmlTemplates.format('enhancementsDebitedInvoiceReceived', ctx={'count': removed}))
        return None if not result else '; '.join(result)

    @staticmethod
    def getEntitlementsString(entitlements):
        result = [ EntitlementBonus.getUserNameWithCount(entitlementID, count) for entitlementID, count in entitlements ]
        return ', '.join(filter(None, result))

    @staticmethod
    def getRankedBonusBattlesString(persistentBattles, dailyBattles):
        result = []
        rShortCut = R.strings.messenger.serviceChannelMessages.battleResults.quests.rankedBonusBattles
        if persistentBattles > 0:
            count = text_styles.neutral(backport.getIntegralFormat(persistentBattles))
            result.append(backport.text(rShortCut.persistent(), count=count))
        if dailyBattles > 0:
            count = text_styles.neutral(backport.getIntegralFormat(dailyBattles))
            result.append(backport.text(rShortCut.daily(), count=count))
        return ', '.join(result)

    def getInvoiceDataAuxMessages(self, data):
        result = []
        result.extend(self.__getDiscardPairModificationsMsg(data))
        return result

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
            tmenToRemove = dataEx.get('tmenToRemove', [])
            vehicles = dataEx.get('vehicles', {})
            vehicleItems = {}
            if vehicles:
                if isinstance(vehicles, dict):
                    vehicles = [vehicles]
                result = self.getVehiclesString(vehicles)
                if result:
                    operations.append(result)
                comptnStr = self.getVehiclesCompensationString(vehicles)
                if comptnStr:
                    operations.append(comptnStr)
                for vehicleDict in vehicles:
                    for v in vehicleDict.itervalues():
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
            if tmenToRemove:
                tankmanCache = self._itemsCache.items.getTankmen()
                tmen = [ tankmanCache[tankman] for tankman in tmenToRemove.get('ids', []) ]
                operations.append(self.getTankmenString(tmen, True))
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
            enhancements = dataEx.get('enhancements', {})
            if enhancements:
                operations.append(self.getEnhancementsString(enhancements))
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
                operations.extend(tokensStr)
            entitlementsStr = self.__getEntitlementsString(dataEx.get('entitlements', {}))
            if entitlementsStr:
                operations.append(entitlementsStr)
            rankedDailyBattles = dataEx.get('rankedDailyBattles', 0)
            rankedPersistentBattles = dataEx.get('rankedBonusBattles', 0)
            rankedBonusBattlesStr = self.__getRankedBonusBattlesString(rankedPersistentBattles, rankedDailyBattles)
            if rankedBonusBattlesStr:
                operations.append(rankedBonusBattlesStr)
            platformCurrenciesStr = self.__getPlatformCurrenciesString(dataEx.get('currencies', {}))
            if platformCurrenciesStr:
                operations.append(platformCurrenciesStr)
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

    def _formatPurchase(self, assetType, data):
        if 'customFormatting' in data.get('tags', ()):
            return None
        else:
            operations = self._composeOperations(data)
            if not operations:
                return None
            ctx = {'at': self._getOperationTimeString(data),
             'desc': self.__getL10nDescription(data),
             'op': '<br/>'.join(operations)}
            templateData = {}
            metadata = data.get('meta')
            title = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.invoice())
            subtitle = ''
            if metadata:
                purchase = self.__purchaseCache.getCachedPurchase(self.__purchaseCache.getProductCode(metadata))
                titleID = purchase.getTitleID()
                if titleID:
                    title = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.purchase.title.dyn(titleID)())
                else:
                    _logger.info('Could not find title in the purchase descriptor!')
                purchaseName = purchase.getProductName()
                if purchaseName:
                    subtitle = g_settings.htmlTemplates.format('purchaseSubtitle', {'text': purchaseName})
                else:
                    _logger.info('Could not find name in the purchase descriptor!')
                iconID = purchase.getIconID()
                if iconID:
                    templateData['icon'] = iconID
                else:
                    _logger.info('Could not find icon in the purchase descriptor!')
            ctx['title'] = title
            ctx['subtitle'] = subtitle
            return g_settings.msgTemplates.format(self._getMessageTemplateKey(assetType), ctx=ctx, data=templateData)

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
        for vehicleDict in vehicles:
            for vehCompDescr, vehData in vehicleDict.iteritems():
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

        def __compensationCalc(calc, vehicleDictionary):
            for value in vehicleDictionary.itervalues():
                if 'rentCompensation' in value:
                    calc += Money.makeFromMoneyTuple(value['rentCompensation'])
                if 'customCompensation' in value:
                    calc += Money.makeFromMoneyTuple(value['customCompensation'])

        vehicles = data.get('vehicles')
        comp = MONEY_UNDEFINED
        if vehicles is not None:
            if isinstance(vehicles, dict):
                __compensationCalc(comp, vehicles)
            else:
                for vehicle in vehicles:
                    __compensationCalc(comp, vehicle)

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
            rares = _getRareAchievements(dossiers)
            uniqueAchieves = _composeAchievements(dossiers)
            addDossierStrings, delDossierStrings, addBadgesStrings, removedBadgesStrings = ([],
             [],
             [],
             [])
            for rec in uniqueAchieves.itervalues():
                for (block, name), recData in rec:
                    if name != '':
                        isRemoving = recData['value'] < 0
                        if block == BADGES_BLOCK:
                            if isRemoving:
                                removedBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                            else:
                                addBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                        elif block != ACHIEVEMENT_BLOCK.RARE:
                            achieveStr = _getFormatAchieveString(name, block, recData)
                            if isRemoving:
                                delDossierStrings.append(achieveStr)
                            else:
                                addDossierStrings.append(achieveStr)

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
                rentTypeName, rentLeftCount = cls.__processRentVehicleData(vehData['rent'])
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

    @staticmethod
    def __processRentVehicleData(rentData):
        timeLeft = rentData.get(RentDurationKeys.TIME, 0)
        if timeLeft:
            rentInfo = RentalInfoProvider(time=timeLeft)
            timeKey, rentLeftCount = getTimeLeftInfo(rentInfo.getTimeLeft())
            return (_RENT_TYPE_NAMES.get(timeKey, None), rentLeftCount)
        else:
            for rentType in [RentDurationKeys.WINS, RentDurationKeys.BATTLES, RentDurationKeys.DAYS]:
                rentTypeValue = rentData.get(rentType, 0)
                if rentTypeValue > 0 and rentType != float('inf'):
                    return (_RENT_TYPE_NAMES.get(rentType, None), int(rentTypeValue))

            return (None, 0)

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

    def __getTokensString(self, data):
        count = 0
        tokenStrings = []
        for tokenName, tokenData in data.iteritems():
            tankmanTokenResult = _processTankmanToken(tokenName)
            if tankmanTokenResult:
                tokenStrings.append(tankmanTokenResult)
            else:
                offerTokenResult = _processOfferToken(tokenName)
                if offerTokenResult:
                    tokenStrings.append(offerTokenResult)
            if tokenName == constants.PERSONAL_MISSION_FREE_TOKEN_NAME:
                count += tokenData.get('count', 0)
            quests = self.__eventsCache.getQuestsByTokenRequirement(tokenName)
            for quest in quests:
                text = quest.getNotificationText().format(count=tokenData.get('count', 0))
                if text:
                    tokenStrings.append(g_settings.htmlTemplates.format('questTokenInvoiceReceived', {'text': text}))

        if count != 0:
            template = 'awardListAccruedInvoiceReceived' if count > 0 else 'awardListDebitedInvoiceReceived'
            tokenStrings.append(g_settings.htmlTemplates.format(template, {'count': count}))
        return tokenStrings

    def __getEntitlementsString(self, data):
        accrued = []
        debited = []
        for entitlementID, entitlementData in data.iteritems():
            count = entitlementData.get('count', 0)
            accrued.append((entitlementID, max(count, 0)))
            debited.append((entitlementID, max(-count, 0)))

        result = ''
        accruedStr = self.getEntitlementsString(accrued)
        debitedStr = self.getEntitlementsString(debited)
        if accruedStr:
            templateId = 'entitlementsAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={'entitlements': accruedStr})
        if debitedStr:
            templateId = 'entitlementsDebitedInvoiceReceived'
            debitedFormatted = g_settings.htmlTemplates.format(templateId, ctx={'entitlements': debitedStr})
            result = text_styles.concatStylesToMultiLine(result, debitedFormatted) if result else debitedFormatted
        return result

    def __getRankedBonusBattlesString(self, persistentBattles, dailyBattles):
        result = ''
        accruedStr = self.getRankedBonusBattlesString(max(persistentBattles, 0), max(dailyBattles, 0))
        debitedStr = self.getRankedBonusBattlesString(max(-persistentBattles, 0), max(-dailyBattles, 0))
        if accruedStr:
            templateId = 'rankedBonusBattlesAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={'bonusBattles': accruedStr})
        if debitedStr:
            templateId = 'rankedBonusBattlesDebitedInvoiceReceived'
            debitedFormatted = g_settings.htmlTemplates.format(templateId, ctx={'bonusBattles': debitedStr})
            result = text_styles.concatStylesToMultiLine(result, debitedFormatted) if result else debitedFormatted
        return result

    def __getPlatformCurrenciesString(self, data):
        msgs = []
        for currencyName, countData in data.iteritems():
            count = countData.get('count', 0)
            if count == 0:
                continue
            elif count > 0:
                op = 'received'
            else:
                op = 'debited'
            msg = backport.text(R.strings.messenger.platformCurrencyMsg.dyn(op).dyn(currencyName)())
            msgs.append(g_settings.htmlTemplates.format('platformCurrency', {'msg': msg,
             'count': backport.getIntegralFormat(abs(count))}))

        return '<br/>'.join(msgs)

    def __getDiscardPairModificationsMsg(self, data):
        dataEx = data.get('data', {})
        result = []
        if not dataEx:
            return result
        else:
            vehicles = dataEx.get('vehicles', [])
            if vehicles:
                if isinstance(vehicles, dict):
                    vehicles = [vehicles]
            for vehicleDict in vehicles:
                for vehCompDescr, vehData in vehicleDict.iteritems():
                    isNegative = False
                    if isinstance(vehCompDescr, types.IntType):
                        isNegative = vehCompDescr < 0
                    if 'customCompensation' not in vehData and isNegative and vehData.get('destroyPairModifications', False):
                        vehicleName = self.__getVehicleName(vehCompDescr)
                        if vehicleName is not None:
                            rMessage = R.strings.messenger.serviceChannelMessages
                            template = self.__DESTROY_PAIR_MODIFICATIONS_MSG_TEMPLATE
                            formatted = g_settings.msgTemplates.format(template, ctx={'text': backport.text(rMessage.vehiclePostProgression.discardAllPairsModification.body(), vehicle=vehicleName)})
                            result.append(MessageData(formatted, self._getGuiSettings(formatted, template)))

            return result

    @async
    @process
    def __waitForSyncData(self, data, callback):
        yield lambda callback: callback(True)
        assetType = data.get('assetType', self.__INVALID_TYPE_ASSET)
        if assetType == INVOICE_ASSET.PURCHASE:
            if self.__purchaseCache.canBeRequestedFromProduct(data):
                purchaseDescrUrl = self.__purchaseCache.getProductCode(data.get('meta'))
                pD = yield self.__purchaseCache.requestPurchaseByID(purchaseDescrUrl)
                callback(pD.getDisplayWays().showNotification)
            else:
                _logger.debug('Data can not be requested from the product! System message will be shown without product data!')
                callback(True)
        else:
            callback(True)

    def __getMetaUrlData(self, data):
        meta = data.get('meta')
        if meta:
            productUrl = meta.get('product_id')
            if productUrl:
                return productUrl
            _logger.error('Could not find product_code in meta section of invoice!')
        else:
            _logger.error('Could not find meta section in purchase invoice!')
        return None


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
                _logger.error('Text of message not found: %s', message)
                return (None, None)
            formatted = g_settings.msgTemplates.format('adminMessage', {'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, 'adminMessage'))]
        else:
            return [MessageData(None, None)]
            return None


class AccountTypeChangedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium', None)
        expiryTime = data.get('expiryTime', None)
        result = [MessageData(None, None)]
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
            result = [MessageData(formatted, self._getGuiSettings(message, templateKey))]
        return result


class _PremiumActionFormatter(ServiceChannelFormatter):
    _templateKey = None
    _msgTemplateKey = None

    def _getMessage(self, isPremium, premiumType, expiryTime):
        return None

    def format(self, message, *args):
        data = message.data
        isPremium = data.get('isPremium')
        expiryTime = data.get('expiryTime', 0)
        premiumType = data.get('premType')
        return [MessageData(self._getMessage(isPremium, premiumType, expiryTime), self._getGuiSettings(message, self._templateKey))] if isPremium is not None and premiumType is not None else [MessageData(None, None)]


class PremiumBoughtFormatter(_PremiumActionFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumBought)
    _msgTemplateKey = str(SYS_MESSAGE_TYPE.premiumChanged)

    def _getMessage(self, isPremium, premiumType, expiryTime):
        result = None
        if isPremium is True and expiryTime > 0:
            formattedText = backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey], expiryTime=text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime)))
            result = g_settings.msgTemplates.format(self._msgTemplateKey, ctx={'text': formattedText})
        return result


class PremiumExtendedFormatter(PremiumBoughtFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumExtended)


class PremiumChangedFormatter(PremiumBoughtFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumChanged)


class PremiumExpiredFormatter(_PremiumActionFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumExpired)
    _msgTemplateKey = str(SYS_MESSAGE_TYPE.premiumExpired)

    def _getMessage(self, isPremium, premiumType, expiryTime):
        result = None
        if isPremium is False:
            result = g_settings.msgTemplates.format(self._msgTemplateKey, ctx={'text': backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey])})
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
            return [MessageData(formatted, self._getGuiSettings(message, 'prebattleArenaFinish'))]


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
            result = [MessageData(formatted, self._getGuiSettings(message, 'prebattleKick'))]
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
            return [MessageData(formatted, self._getGuiSettings(message, 'prebattleDestruction'))]


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
        return [MessageData(formatted, self._getGuiSettings(message, 'vehCamouflageTimedOut'))]


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
        return [MessageData(formatted, self._getGuiSettings(message, 'vehEmblemTimedOut'))]


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
        return [MessageData(formatted, self._getGuiSettings(message, 'vehInscriptionTimedOut'))]


class ConverterFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __CONVERTER_BLUEPRINTS_TEMPLATE = 'ConverterBlueprintsNotify'

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
            messagesListData.append(MessageData(formatted, self._getGuiSettings(message, 'ConverterNotify')))
        if data.get('projectionDecalsDemounted'):
            messageKey = R.strings.messenger.serviceChannelMessages.sysMsg.converter.projectionDecalsDemounted()
            messageText = backport.text(messageKey)
            templateName = 'ProjectionDecalsDemountedSysMessage'
            formatted = g_settings.msgTemplates.format(templateName, {'text': messageText})
            messagesListData.append(MessageData(formatted, self._getGuiSettings(message, 'ProjectionDecalsDemountedSysMessage')))
        blueprints = data.get('blueprints')
        if blueprints:
            blueprintsText = self.__getBlueprintsMessageText(blueprints)
            if blueprintsText is not None:
                messagesListData.append(MessageData(blueprintsText, self._getGuiSettings(message, self.__CONVERTER_BLUEPRINTS_TEMPLATE)))
        return messagesListData

    def __getBlueprintsMessageText(self, blueprints):
        universal = 0
        national = defaultdict(int)
        text = []
        for blueprintCD in blueprints:
            fragmentType = getFragmentType(blueprintCD)
            if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
                universal += blueprints[blueprintCD]
            if fragmentType == BlueprintTypes.NATIONAL:
                nationID = getFragmentNationID(blueprintCD)
                nationName = nations.MAP.get(nationID, nations.NONE_INDEX)
                national[nationName] += blueprints[blueprintCD]

        if universal > 0:
            text.append(g_settings.htmlTemplates.format('intelligenceBlueprintReceived', {'count': backport.getIntegralFormat(universal)}))
        for nation in GUI_NATIONS:
            if national[nation] > 0:
                text.append(g_settings.htmlTemplates.format('nationalBlueprintReceived', {'count': backport.getIntegralFormat(national[nation]),
                 'nationName': backport.text(R.strings.nations.dyn(nation).genetiveCase())}))

        return g_settings.msgTemplates.format(self.__CONVERTER_BLUEPRINTS_TEMPLATE, {'text': '<br/>'.join(text)}) if text else None


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
        return [MessageData(formatted, self._getGuiSettings(args, templateKey))]

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
        return [MessageData(formatted, self._getGuiSettings(args, 'durationOfPremiumAccountExpires'))]


class SessionControlFormatter(ServiceChannelFormatter):

    def _doFormat(self, text, key, auxData):
        formatted = g_settings.msgTemplates.format(key, {'text': text})
        priorityLevel = g_settings.msgTemplates.priority(key)
        return [MessageData(formatted, NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData))]


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
            result = [MessageData(formatted, self._getGuiSettings(message, 'vehicleLockExpired'))]
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
                result = [MessageData(formatted, self._getGuiSettings(message, self.__templateKey))]
        return result


class ActionNotificationFormatter(ClientSysMessageFormatter):
    __templateKey = 'action%s'

    def format(self, message, *args):
        result = []
        data = message.get('data')
        if data:
            templateKey = self.__templateKey % message.get('state', '')
            formatted = g_settings.msgTemplates.format(templateKey, ctx={'text': data}, data={'icon': message.get('type', '')})
            result = [MessageData(formatted, self._getGuiSettings(args, templateKey))]
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
            return [MessageData(formatted, self._getGuiSettings(args, key))]
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
        callback([MessageData(formatted, settings)])
        return None

    def __formatAwards(self, results):
        awards = backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.awards()) + '<br/>'
        awards += self.__getAssetString(results, INVOICE_ASSET.GOLD, 'gold')
        awards += self.__getAssetString(results, INVOICE_ASSET.PREMIUM, 'premium')
        awards += self.__getAssetString(results, INVOICE_ASSET.CREDITS, 'credits')
        tankPremiumDays = results.get(PREMIUM_ENTITLEMENTS.PLUS, 0)
        if tankPremiumDays:
            awards += '<br/>' + g_settings.htmlTemplates.format('tankPremiumAccruedInvoiceReceived', {'amount': backport.getIntegralFormat(abs(tankPremiumDays))})

        def sortVehsByLvl(vehCD):
            veh = self._itemsCache.items.getItemByCD(vehCD)
            return veh.level

        vehicles = results.get('vehicles', {})
        vehicleCDs = sorted(vehicles.keys(), key=sortVehsByLvl)
        vehiclesNames = []
        devicesAndCrew = ''
        for vehCD in vehicleCDs:
            vehData = vehicles[vehCD]
            vehicle = self._itemsCache.items.getItemByCD(vehCD)
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


class QuestAchievesFormatter(object):
    _SEPARATOR = '<br/>'
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = []
        tokenResult = cls._processTokens(data)
        if tokenResult and processTokens:
            result.append(tokenResult)
        if not asBattleFormatter:
            crystal = data.get(Currency.CRYSTAL, 0)
            if crystal:
                fomatter = getBWFormatter(Currency.CRYSTAL)
                result.append(cls.__makeQuestsAchieve('battleQuestsCrystal', crystal=fomatter(crystal)))
            eventCoin = data.get(Currency.EVENT_COIN, 0)
            if eventCoin:
                fomatter = getBWFormatter(Currency.EVENT_COIN)
                result.append(cls.__makeQuestsAchieve('battleQuestsEventCoin', eventCoin=fomatter(eventCoin)))
            gold = data.get(Currency.GOLD, 0)
            if gold:
                fomatter = getBWFormatter(Currency.GOLD)
                result.append(cls.__makeQuestsAchieve('battleQuestsGold', gold=fomatter(gold)))
            bpcoin = data.get(Currency.BPCOIN, 0)
            if bpcoin:
                fomatter = getBWFormatter(Currency.BPCOIN)
                result.append(cls.__makeQuestsAchieve('battleQuestsBpcoin', bpcoin=fomatter(bpcoin)))
            platformCurrencies = data.get('currencies', {})
            for currency, countDict in platformCurrencies.iteritems():
                result.append(cls.__makeQuestsAchieve('platformCurrency', msg=backport.text(R.strings.messenger.platformCurrencyMsg.received.dyn(currency)()), count=backport.getIntegralFormat(countDict.get('count', 0))))

        for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
            premium = data.get(premiumType, 0)
            if premium:
                result.append(cls.__makeQuestsAchieve(_PREMIUM_TEMPLATES[premiumType], days=premium))

        if not asBattleFormatter:
            freeXP = data.get('freeXP', 0)
            if freeXP:
                result.append(cls.__makeQuestsAchieve('battleQuestsFreeXP', freeXP=backport.getIntegralFormat(freeXP)))
        vehiclesList = data.get('vehicles', [])
        msg = InvoiceReceivedFormatter.getVehiclesString(vehiclesList, htmlTplPostfix='QuestsReceived')
        if msg:
            result.append(msg)
        comptnStr = InvoiceReceivedFormatter.getVehiclesCompensationString(vehiclesList, htmlTplPostfix='QuestsReceived')
        if comptnStr:
            result.append(cls._SEPARATOR + comptnStr if result else comptnStr)
        if not asBattleFormatter:
            creditsVal = data.get(Currency.CREDITS, 0)
            if creditsVal:
                fomatter = getBWFormatter(Currency.CREDITS)
                result.append(cls.__makeQuestsAchieve('battleQuestsCredits', credits=fomatter(creditsVal)))
        slots = data.get('slots', 0)
        if slots:
            result.append(cls.__makeQuestsAchieve('battleQuestsSlots', slots=backport.getIntegralFormat(slots)))
        if not asBattleFormatter:
            dailyBattles = data.get('rankedDailyBattles', 0)
            persistBattles = data.get('rankedBonusBattles', 0)
            rankedBonusBattlesStr = InvoiceReceivedFormatter.getRankedBonusBattlesString(persistBattles, dailyBattles)
            if rankedBonusBattlesStr:
                mainStrRes = R.strings.messenger.serviceChannelMessages.battleResults.quests.rankedBonusBattles()
                result.append(backport.text(mainStrRes, bonusBattles=rankedBonusBattlesStr))
        items = data.get('items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            if itemTypeID == I_T.crewBook:
                if asBattleFormatter or not cls.__lobbyContext.getServerSettings().isCrewBooksEnabled():
                    continue
                itemDescr = tankmen.getItemByCompactDescr(intCD)
                name = _getCrewBookUserString(itemDescr)
            else:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                name = itemDescr.i18n.userString
            itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(count)))

        goodies = data.get('goodies', {})
        excludeGoodies = set()
        for goodieID, ginfo in goodies.iteritems():
            if goodieID in cls.__itemsCache.items.shop.demountKits:
                excludeGoodies.add(goodieID)
                demountKit = cls.__goodiesCache.getDemountKit(goodieID)
                if demountKit is not None and demountKit.enabled:
                    itemsNames.append(backport.text(R.strings.demount_kit.demountKit.gained.count(), count=ginfo.get('count')))

        abilityPts = data.get(constants.EPIC_ABILITY_PTS_NAME)
        if abilityPts:
            name = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.epicAbilityPoints())
            itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(abilityPts)))
        tokens = data.get('tokens')
        if tokens:
            for tokenID, tokenData in tokens.iteritems():
                count = backport.getIntegralFormat(tokenData.get('count', 1))
                name = None
                if tokenID == BATTLE_BONUS_X5_TOKEN:
                    name = backport.text(R.strings.quests.bonusName.battle_bonus_x5())
                if name is not None:
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=count))

        entitlementsList = [ (eID, eData.get('count', 0)) for eID, eData in data.get('entitlements', {}).iteritems() ]
        entitlementsStr = InvoiceReceivedFormatter.getEntitlementsString(entitlementsList)
        if entitlementsStr:
            itemsNames.append(entitlementsStr)
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
            strGoodies = InvoiceReceivedFormatter.getGoodiesString(goodies, exclude=excludeGoodies)
            if strGoodies:
                result.append(strGoodies)
        enhancements = data.get('enhancements', {})
        if enhancements:
            strEnhancements = InvoiceReceivedFormatter.getEnhancementsString(enhancements)
            if strEnhancements:
                result.append(strEnhancements)
        if not asBattleFormatter:
            blueprints = data.get('blueprints', {})
            if blueprints:
                strBlueprints = InvoiceReceivedFormatter.getBlueprintString(blueprints)
                if strBlueprints:
                    result.append(strBlueprints)
        if not asBattleFormatter:
            achievementsNames = cls._extractAchievements(data)
            if achievementsNames:
                result.append(cls.__makeQuestsAchieve('battleQuestsPopUps', achievements=', '.join(achievementsNames)))
            addBadgesStrings, removedBadgesStrings = cls.__extractBadges(data)
            if addBadgesStrings:
                result.append(cls.__makeQuestsAchieve('badgeAchievement', badges=', '.join(addBadgesStrings)))
            if removedBadgesStrings:
                result.append(cls.__makeQuestsAchieve('removedBadgeAchievement', badges=', '.join(removedBadgesStrings)))
        if not asBattleFormatter:
            for crewbookName in data.get('selectableCrewbook', {}):
                result.append(backport.text(R.strings.messenger.serviceChannelMessages.selectableCrewbook.dyn(crewbookName)()))

        return cls._SEPARATOR.join(result) if result else None

    @classmethod
    def _processTokens(cls, tokens):
        pass

    @classmethod
    def _extractAchievements(cls, data):
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
        addBadgesStrings, removedBadgesStrings = [], []
        for rec in data.get('dossier', {}).values():
            it = rec if not isinstance(rec, dict) else rec.iteritems()
            for (block, name), recData in it:
                if name != '':
                    isRemoving = recData['value'] < 0
                    if block == BADGES_BLOCK:
                        if isRemoving:
                            removedBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))
                        else:
                            addBadgesStrings.append(backport.text(R.strings.badge.dyn('badge_{}'.format(name))()))

        return (addBadgesStrings, removedBadgesStrings)

    @classmethod
    def __makeQuestsAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)


class TokenQuestsFormatter(WaitItemsSyncFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __MESSAGE_TEMPLATE = 'tokenQuests'

    def __init__(self, subFormatters=()):
        super(TokenQuestsFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()
        self.__subFormatters = subFormatters

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = set(data.get('completedQuestIDs', set()))
            completedQuestIDs.update(data.get('rewardsGottenQuestIDs', set()))
            popUps = set(data.get('popUpRecords', set()))
            for qID in completedQuestIDs:
                self.__processMetaActions(qID)

            for subFormatter in self.__subFormatters:
                subTokenQuestIDs = subFormatter.getQuestOfThisGroup(completedQuestIDs)
                if subTokenQuestIDs:
                    if subFormatter.isAsync():
                        result = yield subFormatter.format(message)
                    else:
                        result = subFormatter.format(message)
                    if result:
                        messageDataList.extend(result)
                    completedQuestIDs.difference_update(subTokenQuestIDs)
                    popUps.difference_update(subFormatter.getPopUps(message))

            if completedQuestIDs or popUps:
                messageData = self.__formatSimpleTokenQuests(message, completedQuestIDs, popUps)
                if messageData is not None:
                    messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
            return
        else:
            callback([MessageData(None, None)])
            return

    @classmethod
    def __processMetaActions(cls, questID):
        quest = cls.__eventsCache.getAllQuests().get(questID)
        if quest is None:
            _logger.debug('Could not find quest with ID: %s', questID)
            return
        else:
            for bonus in quest.getBonuses():
                if not isinstance(bonus, MetaBonus):
                    continue
                for action, params in bonus.getActions():
                    bonus.handleAction(action, params)

            return

    def __formatSimpleTokenQuests(self, message, questIDs, popUps):
        rewards = getRewardsForQuests(message, questIDs)
        rewards['popUpRecords'] = popUps
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            return MessageData(formatted, settings)
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
        return [MessageData(formatted, settings)]

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
            return [MessageData(formatted, settings)]
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
                return [MessageData(formatted, settings)]
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
         'timeLeft': backport.getTillTimeStringByRClass(time_utils.getTimeDeltaFromNow(expirationTime), R.strings.menu.Time.timeValueWithSecs, removeLeadingZeros=False)})

    def _reserveExpiredMessage(self, data):
        return self._buildMessage(data['event'], {'order': self.getOrderUserString(data['orderTypeID'])})


class VehicleRentedFormatter(ServiceChannelFormatter):
    _templateKey = 'vehicleRented'

    def format(self, message, *args):
        data = message.data
        vehTypeCD = data.get('vehTypeCD', None)
        expiryTime = data.get('time', None)
        return [MessageData(self._getMessage(vehTypeCD, expiryTime), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else []

    def _getMessage(self, vehTypeCD, expiryTime):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {'vehicleName': vehicleName,
         'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class RentalsExpiredFormatter(ServiceChannelFormatter):
    _templateKey = 'rentalsExpired'

    def format(self, message, *args):
        vehTypeCD = message.data.get('vehTypeCD', None)
        return [MessageData(self._getMessage(vehTypeCD), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else (None, None)

    def _getMessage(self, vehTypeCD):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {'vehicleName': vehicleName}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class PersonalMissionsQuestAchievesFormatter(QuestAchievesFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def _processTokens(cls, data):
        quest = cls.__eventsCache.getPersonalMissions().getAllQuests().get(data.get('potapovQuestID'))
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


class LootBoxAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def _processTokens(cls, data):
        result = []
        for token in data.get('tokens', {}).iterkeys():
            tankmanTokenResult = _processTankmanToken(token)
            if tankmanTokenResult:
                result.append(tankmanTokenResult)

        return '\n'.join(result)

    @classmethod
    def _extractAchievements(cls, data):
        return _getAchievementsFromQuestData(data)


class BattlePassQuestAchievesFormatter(QuestAchievesFormatter):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    _BULLET = '- '
    _SEPARATOR = '<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(BattlePassQuestAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result

    @classmethod
    def _processTokens(cls, data):
        from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift
        result = []
        styleTokens = []
        rewardChoiceTokens = {}
        for token, tokenData in data.get('tokens', {}).iteritems():
            if token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS):
                offer = cls.__offersProvider.getOfferByToken(getOfferTokenByGift(token))
                gift = first(offer.getAllGifts())
                giftType = token.split(':')[2]
                rewardChoiceTokens.setdefault(giftType, 0)
                rewardChoiceTokens[giftType] += gift.giftCount * tokenData.get('count', 1)
            if token.startswith(BATTLE_PASS_TOKEN_3D_STYLE):
                styleTokens.append(token)
            tankmanTokenResult = _processTankmanToken(token)
            if tankmanTokenResult:
                result.append(tankmanTokenResult)

        result.extend(cls.__processStyleTokens(styleTokens))
        result.extend(cls.__processRewardChoiceTokens(rewardChoiceTokens))
        return cls._SEPARATOR.join(result)

    @classmethod
    def _extractAchievements(cls, data):
        return _getAchievementsFromQuestData(data)

    @classmethod
    def __processStyleTokens(cls, tokens):
        tokens.sort(key=lambda x: (int(x.split(':')[-2]), int(x.split(':')[-1])))
        return [ cls.__getFormattedStyleProgress(token) for token in tokens ]

    @classmethod
    def __processRewardChoiceTokens(cls, tokens):
        result = []
        rewardSelectTemplate = 'battlePassRewardSelectToken'
        rChosenBonuses = R.strings.battle_pass.chosenBonuses.bonus
        for rewardType, count in tokens.iteritems():
            result.append(g_settings.htmlTemplates.format(rewardSelectTemplate, {'text': backport.text(rChosenBonuses.dyn(rewardType)()),
             'count': count}))

        return result

    @classmethod
    def __getFormattedStyleProgress(cls, token):
        from gui.battle_pass.battle_pass_helpers import getStyleForChapter
        chapter = int(token.split(':')[3])
        level = int(token.split(':')[4])
        style = getStyleForChapter(chapter)
        text = backport.text(R.strings.battle_pass.styleProgressBonus(), styleName=style.userName, level=int2roman(level))
        return g_settings.htmlTemplates.format('battlePassStyleProgressToken', {'text': text})


class _GoodyFormatter(WaitItemsSyncFormatter):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    _VARIETY_TO_TEMPLATE = {}

    @async
    @process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            gid = message.data.get('gid')
            goodieDescr = self.__goodiesCache.getGoodieByID(gid)
            if goodieDescr.variety == GOODIE_VARIETY.DISCOUNT:
                goodie = self.__goodiesCache.getDiscount(gid)
            elif goodieDescr.variety == GOODIE_VARIETY.BOOSTER:
                goodie = self.__goodiesCache.getBooster(gid)
            else:
                goodie = self.__goodiesCache.getDemountKit(gid)
            if goodie:
                template = self._getTemplateName(goodieDescr.variety)
                if template:
                    formatted = g_settings.msgTemplates.format(template, ctx={'boosterName': goodie.userName})
                    callback([MessageData(formatted, self._getGuiSettings(message, template))])
                    return
            callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return

    def canBeEmpty(self):
        return True

    def _getTemplateName(self, goodieType):
        return self._VARIETY_TO_TEMPLATE.get(goodieType)


class GoodyRemovedFormatter(_GoodyFormatter):
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.BOOSTER: 'boosterExpired'}


class GoodyDisabledFormatter(_GoodyFormatter):
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.DEMOUNT_KIT: 'demountKitDisabled',
     GOODIE_VARIETY.BOOSTER: 'boosterDisabled'}


class GoodieEnabledFormatter(_GoodyFormatter):
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.DEMOUNT_KIT: 'demountKitEnabled'}


class TelecomStatusFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

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

        messageData = MessageData(formatted, settings)
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
            bundleId = data['bundleID']
            telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
            provider = telecomConfig.getInternetProvider(bundleId)
        providerLocName = ''
        if provider:
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            providerLocName = backport.text(providerLocRes.name()) if providerLocRes else ''
        msgctx = {'vehicles': self.__getVehicleUserNames(vehTypeDescrs),
         'provider': providerLocName}
        ctx = {}
        resShortcut = R.strings.system_messages.telecom
        for txtBlock in ('title', 'comment', 'subcomment'):
            ctx[txtBlock] = backport.text(self.__addProviderToRes(resShortcut.notifications.dyn(key).dyn(txtBlock), provider)(), **msgctx)

        return ctx

    @classmethod
    def __getVehicleUserNames(cls, vehTypeCompDescrs):
        itemGetter = cls._itemsCache.items.getItemByCD
        return ', '.join((itemGetter(vehicleCD).userName for vehicleCD in vehTypeCompDescrs))


class TelecomReceivedInvoiceFormatter(InvoiceReceivedFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

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

    def _getProvider(self, data):
        telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
        return telecomConfig.getInternetProvider(data['bundleID'])

    @classmethod
    def _isValidCD(cls, vehCompDescr):
        return vehCompDescr > 0

    def _getVehicles(self, data):
        dataEx = data.get('data', {})
        if not dataEx:
            return
        else:
            vehicles = [dataEx.get('vehicles', {})]
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
            vehicles = [dataEx.get('vehicles', {})]
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
    typeKick = 'prbVehicleKick'

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get('vehInvID', None)
        self.__itemsCache.items.getVehicle(vehInvID)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format(self.typeKick, ctx={'vehName': vehicle.userName})
        return [MessageData(formatted, self._getGuiSettings(message, self.typeKick))]


class PrbVehicleKickFilterFormatter(PrbVehicleKickFormatter):
    typeKick = 'prbVehicleKickFilter'


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
        return [MessageData(formatted, self._getGuiSettings(message, 'prbVehicleMaxSpgKick'))]


class RotationGroupLockFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        templateKey = self._getMessageTemplateKey()
        if isinstance(message.data, list):
            groups = ', '.join(map(str, message.data))
        else:
            groups = message.data
        formatted = g_settings.msgTemplates.format(templateKey, ctx={'groupNum': groups})
        return [MessageData(formatted, self._getGuiSettings(message, templateKey))]

    def _getMessageTemplateKey(self):
        pass


class RotationGroupUnlockFormatter(RotationGroupLockFormatter):

    def _getMessageTemplateKey(self):
        pass


class RankedQuestAchievesFormatter(QuestAchievesFormatter):
    __rankAwardsFormatters = tuple(((currency, getBWFormatter(currency)) for currency in Currency.ALL))
    __offersDP = dependency.descriptor(IOffersDataProvider)
    __awardsStyles = {Currency.CREDITS: text_styles.credits,
     Currency.GOLD: text_styles.gold,
     Currency.CRYSTAL: text_styles.crystal,
     Currency.EVENT_COIN: text_styles.eventCoin,
     Currency.BPCOIN: text_styles.bpcoin}

    def packRankAwards(self, awardsDict):
        result = [self._processTokens(awardsDict)]
        result.extend(self.packAwards(awardsDict, self.__rankAwardsFormatters))
        otherStr = self.formatQuestAchieves(awardsDict, asBattleFormatter=False)
        if otherStr:
            result.append(otherStr)
        return EOL.join(result)

    def packAwards(self, awardsDict, formattersList):
        result = []
        for awardName, extractor in formattersList:
            award = None
            if awardName in awardsDict:
                award = awardsDict.pop(awardName)
            if award is not None:
                value = extractor(award)
                if value and value != '0':
                    result.append(self.__packAward(awardName, value))

        return result

    @classmethod
    def _processTokens(cls, awardsDict):
        tokensAmount = cls.__getYearPointsAmount(awardsDict)
        processedTokens = []
        if tokensAmount > 0:
            processedTokens.append(backport.text(R.strings.system_messages.ranked.notifications.bonusName.yearPoints(), yearPoints=text_styles.stats(tokensAmount)))
        selectableTokensAmount = cls.__getSelectableAwardCount(awardsDict)
        if selectableTokensAmount > 0:
            processedTokens.append(backport.text(R.strings.system_messages.ranked.notifications.bonusName.selectableReward(), selectableRewardCount=text_styles.stats(selectableTokensAmount)))
        awardsDict.pop('tokens', None)
        return EOL.join(processedTokens)

    @classmethod
    def __getYearPointsAmount(cls, awardsDict):
        return awardsDict.get('tokens', {}).get(YEAR_POINTS_TOKEN, {}).get('count', 0)

    @classmethod
    def __getSelectableAwardCount(cls, awardsDict):
        awardMainTokenID = YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX
        result = 0
        for tokenID in awardsDict.get('tokens', {}):
            if tokenID.startswith(awardMainTokenID):
                result += int(tokenID.split(':')[-1])

        return result

    def __packAward(self, key, value):
        return '{} {}'.format(backport.text(R.strings.system_messages.ranked.notifications.bonusName.dyn(key)()), self.__awardsStyles.get(key, text_styles.stats)(value))


class BRQuestsFormatter(TokenQuestsFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = message.data.get('completedQuestIDs', set())
            messages = self.__formatEveryLevel(completedQuestIDs, message.data.copy())
            callback([ MessageData(formattedMessage, self._getGuiSettings(message)) for formattedMessage in messages ])
        else:
            callback([MessageData(None, self._getGuiSettings(message))])
        return

    def __formatEveryLevel(self, completedQuestIDs, data):
        formattedMessage = None
        formattedLevels = {}
        quests = self.__eventsCache.getHiddenQuests()
        for questID in completedQuestIDs:
            quest = quests.get(questID)
            if quest is not None:
                levelID = self.__getLevel(quest)
                textID = R.strings.system_messages.royale.notifications.singleLevel.text()
                formattedLevels[levelID] = backport.text(textID, level=levelID)

        if formattedLevels:
            formattedMessage = g_settings.msgTemplates.format('BrLevelQuest', ctx={'levelsBlock': EOL.join([ formattedLevels[key] for key in sorted(formattedLevels) ]),
             'awardsBlock': self._packTitleAwards(data)})
        return [formattedMessage]

    def _packTitleAwards(self, awardsDict):
        return self._achievesFormatter.formatQuestAchieves(awardsDict, asBattleFormatter=False) or ''

    @classmethod
    def __getLevel(cls, quest):
        return str(quest.getID().split(':')[-1])


class RankedQuestFormatter(WaitItemsSyncFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedQuestFormatter, self).__init__()
        self.__achievesFormatter = RankedQuestAchievesFormatter()

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = message.data.get('completedQuestIDs', set())
            messages = self.__formatRankedQuests(completedQuestIDs, message.data.copy())
            callback([ MessageData(formattedMessage, self._getGuiSettings(message)) for formattedMessage in messages ])
        else:
            callback([MessageData(None, self._getGuiSettings(message))])
        return

    def __formatRankedQuests(self, completedQuestIDs, data):
        formattedMessage = None
        formattedRanks = {}
        quests = self.__eventsCache.getHiddenQuests()
        qualificationBattles = 0
        for questID in completedQuestIDs:
            quest = quests.get(questID)
            if quest is not None and quest.isForRank():
                rankID = quest.getRank()
                division = self.__rankedController.getDivision(rankID)
                textID = R.strings.system_messages.ranked.notifications.singleRank.text()
                if division.isQualification():
                    if isQualificationQuestID(questID):
                        textID = R.strings.ranked_battles.awards.gotQualificationQuest()
                        qualificationBattles = getQualificationBattlesCountFromID(questID)
                    else:
                        textID = R.strings.system_messages.ranked.notifications.qualificationFinish()
                formattedRanks[rankID] = backport.text(textID, rankName=division.getRankUserName(rankID), divisionName=division.getUserName(), count=qualificationBattles)

        if formattedRanks:
            formattedMessage = g_settings.msgTemplates.format('rankedRankQuest', ctx={'ranksBlock': EOL.join([ formattedRanks[key] for key in sorted(formattedRanks) ]),
             'awardsBlock': self.__achievesFormatter.packRankAwards(data)})
        return [formattedMessage]


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
                    settings = self._getGuiSettings(message, self._template, messageType=message.type)
                    settings.showAt = BigWorld.time()
                    callback([MessageData(formatted, settings)])

            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return


class CustomizationChangedFormatter(WaitItemsSyncFormatter):
    _template = 'CustomizationRemoved'

    @async
    @process
    def format(self, message, callback=None):
        from gui.customization.shared import SEASON_TYPE_TO_NAME, SEASONS_ORDER
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            vehicleIntCD = first(data)
            vehicleData = data[vehicleIntCD]
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            data = {'savedData': {'vehicleIntCD': vehicleIntCD}}
            text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.removeCustomizations(), vehicle=vehicle.userName)
            seasonTexts = {}
            for season, seasonData in vehicleData.iteritems():
                items = []
                for itemIntCD, count in seasonData.iteritems():
                    item = self._itemsCache.items.getItemByCD(itemIntCD)
                    formattedItem = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizations.item(), itemType=item.userType, itemName=item.userName, count=count)
                    items.append(formattedItem)

                if items:
                    seasonName = SEASON_TYPE_TO_NAME.get(season)
                    formattedSeason = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizations.map.dyn(seasonName)()) + ', '.join(items) + '.'
                    seasonTexts[season] = '\n' + formattedSeason

            for season in SEASONS_ORDER:
                if season in seasonTexts:
                    text += seasonTexts[season]

            formatted = g_settings.msgTemplates.format(self._template, {'text': text}, data=data)
            settings = self._getGuiSettings(message, self._template, messageType=message.type)
            settings.showAt = BigWorld.time()
            callback([MessageData(formatted, settings)])
        else:
            callback([MessageData(None, None)])
        return


class LootBoxAutoOpenFormatter(WaitItemsSyncFormatter):
    __MESSAGE_TEMPLATE = 'LootBoxRewardsSysMessage'

    def __init__(self, subFormatters=()):
        super(LootBoxAutoOpenFormatter, self).__init__()
        self._achievesFormatter = LootBoxAchievesFormatter()
        self.__subFormatters = subFormatters

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced and message.data:
            openedBoxesIDs = set(message.data.keys())
            for subFormatter in self.__subFormatters:
                subBoxesIDs = subFormatter.getBoxesOfThisGroup(openedBoxesIDs)
                print 'subBoxesIDs____', subBoxesIDs, subFormatter
                if subBoxesIDs:
                    if subFormatter.isAsync():
                        result = yield subFormatter.format(message)
                    else:
                        result = subFormatter.format(message)
                    if result:
                        messageDataList.extend(result)
                    openedBoxesIDs.difference_update(subBoxesIDs)

            if openedBoxesIDs:
                messageData = self.__formatSimpleBoxes(message, openedBoxesIDs)
                if messageData is not None:
                    messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
            return
        else:
            callback([MessageData(None, None)])
            return

    def __formatSimpleBoxes(self, message, openedBoxesIDs):
        data = message.data
        openedBoxesIDs.difference_update({'rewards', 'boxIDs'})
        oldRewards, _ = data.pop('rewards', {}), data.pop('boxIDs', None)
        allRewards = getMergedBonusesFromDicts([ data[bID]['rewards'] for bID in openedBoxesIDs ] + [oldRewards])
        fmt = self._achievesFormatter.formatQuestAchieves(allRewards, asBattleFormatter=False, processTokens=False)
        formattedRewards = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'text': fmt})
        settingsRewards = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        settingsRewards.showAt = BigWorld.time()
        return MessageData(formattedRewards, settingsRewards)


class ProgressiveRewardFormatter(WaitItemsSyncFormatter):
    _template = 'ProgressiveRewardMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            if 'rewards' in data and 'level' in data:
                fmt = QuestAchievesFormatter.formatQuestAchieves(data['rewards'], False)
                if fmt:
                    formatted = g_settings.msgTemplates.format(self._template, ctx={'text': fmt})
                    settings = self._getGuiSettings(message, self._template)
                    settings.showAt = BigWorld.time()
                    callback([MessageData(formatted, settings)])
                else:
                    callback([MessageData(None, None)])
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return


class PiggyBankSmashedFormatter(ServiceChannelFormatter):
    _piggyBankTemplate = 'PiggyBankSmashedMessage'
    _goldReserveTemplate = 'GoldReserveSmashedMessage'

    def format(self, message, *args):
        if not message.data:
            return []
        sysNotifications = []
        credits_ = message.data.get('credits')
        gold = message.data.get('gold')
        if credits_:
            ctx = {'credits': backport.getIntegralFormat(credits_)}
            formatted = g_settings.msgTemplates.format(self._piggyBankTemplate, ctx)
            sysNotifications.append(MessageData(formatted, self._getGuiSettings(message, self._piggyBankTemplate)))
        if gold:
            ctx = {'gold': backport.getGoldFormat(gold)}
            formatted = g_settings.msgTemplates.format(self._goldReserveTemplate, ctx)
            sysNotifications.append(MessageData(formatted, self._getGuiSettings(message, self._goldReserveTemplate)))
        return sysNotifications


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
                return [MessageData(None, None)]
            mapNames = []
            for mapID in mapIDs:
                if mapID in ArenaType.g_cache:
                    mapNames.append(i18n.makeString(ArenaType.g_cache[mapID].name))

            settings = self.__REASONS_SETTINGS[reason]
            text = backport.text(settings['text'], mapNames=','.join(mapNames))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=settings['priority'])
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementRemovedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'EnhancementRemovedMessage'

    def format(self, message, *args):
        if message.data:
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.removed())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementsWipedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'EnhancementsWipedMessage'

    def format(self, message, *args):
        if message.data:
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.wiped())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementsWipedOnVehiclesFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'EnhancementsWipedOnVehiclesMessage'

    def format(self, message, *args):
        if message.data:
            vehCompDescriptors = message.data.get('vehicles', set())
            vehNames = [ getUserName(vehicles_core.getVehicleType(vehCD)) for vehCD in vehCompDescriptors ]
            vehNames = ', '.join(vehNames)
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.wipedOnVehicles())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': text,
             'vehicleNames': vehNames})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class BattlePassRewardFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __TEMPLATE = 'BattlePassRewardSysMessage'
    __PROGRESSION_BUTTON_TEMPLATE = 'BattlePassRewardWithProgressionButtonMessage'
    __SHOP_BUTTON_TEMPLATE = 'BattlePassRewardWithShopButtonMessage'
    __GOLD_TEMPLATE_KEY = 'battlePassGold'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            if 'reward' in data and 'ctx' in data:
                rewards = data.get('reward')
                ctx = data.get('ctx')
                reason = ctx.get('reason')
                description = ''
                additionalText = ''
                template = self.__TEMPLATE
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.default())
                priorityLevel = None
                savedData = None
                if reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS:
                    if not rewards:
                        callback([])
                    header, description, priorityLevel, additionalText = self.__makeAfterBattlePassPurchase(ctx)
                else:
                    if reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE:
                        callback([])
                        return
                    if reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS:
                        header, description, priorityLevel, additionalText = self.__makeAfterLevelsPurchase(ctx)
                    elif reason == BattlePassRewardReason.SELECT_CHAPTER:
                        description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.activateChapter.text())
                    elif reason in (BattlePassRewardReason.INVOICE, BattlePassRewardReason.BATTLE):
                        description, template, priorityLevel, additionalText, savedData = self.__makeAfterBattle(ctx)
                formattedBonuses = BattlePassQuestAchievesFormatter.formatQuestAchieves(rewards, False)
                if formattedBonuses is None:
                    formattedBonuses = ''
                if formattedBonuses and additionalText:
                    additionalText = '<br/>' + additionalText
                formatted = g_settings.msgTemplates.format(template, ctx={'header': header,
                 'description': description,
                 'text': formattedBonuses,
                 'additionalText': additionalText}, data={'savedData': savedData})
                settings = self._getGuiSettings(message, template, messageType=message.type)
                settings.showAt = BigWorld.time()
                if priorityLevel is not None:
                    settings.priorityLevel = priorityLevel
                resultMessage = MessageData(formatted, settings)
        callback([resultMessage])
        return

    def __makeAfterBattle(self, ctx):
        newLevel = ctx.get('newLevel')
        priorityLevel = None
        additionalText = ''
        chapterID = ctx.get('chapter')
        savedData = None
        if not self.__battlePassController.isCompleted():
            chapterName = backport.text(R.strings.battle_pass.chapter.dyn(self.__battlePassController.getRewardType(chapterID).value).fullName.num(chapterID)())
            if not self.__battlePassController.isFinalLevel(chapterID, newLevel):
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.newLevel.text(), newLevel=text_styles.credits(newLevel), chapter=text_styles.credits(chapterName))
            else:
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.chapterFinal.text(), chapter=text_styles.credits(chapterName))
            template = self.__PROGRESSION_BUTTON_TEMPLATE
            savedData = {'chapterID': chapterID}
        else:
            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.text(), season=self.__battlePassController.getSeasonNum())
            priorityLevel = NotificationPriorityLevel.LOW
            template = self.__SHOP_BUTTON_TEMPLATE
            additionalText = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.additionalText())
        return (description,
         template,
         priorityLevel,
         additionalText,
         savedData)

    def __makeAfterLevelsPurchase(self, ctx):
        chapterID = ctx.get('chapter')
        currentLevel = ctx.get('newLevel')
        prevLevel = ctx.get('prevLevel')
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyProgress())
        levelCount = currentLevel - prevLevel
        if self.__battlePassController.isFinalLevel(chapterID, currentLevel):
            level = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyProgress.finalText())
        else:
            level = currentLevel + 1
        description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyProgress.text(), levelCount=text_styles.credits(levelCount), currentLevel=text_styles.credits(level), chapter=text_styles.credits(backport.text(R.strings.battle_pass.chapter.dyn(self.__battlePassController.getRewardType(chapterID).value).fullName.num(chapterID)())))
        price = self.__itemsCache.items.shop.getBattlePassLevelCost().get(Currency.GOLD, 0) * levelCount
        additionalText = self.__makeGoldString(price)
        priorityLevel = NotificationPriorityLevel.LOW
        return (header,
         description,
         priorityLevel,
         additionalText)

    def __makeAfterBattlePassPurchase(self, ctx):
        chapterID = ctx.get('chapter')
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyBP())
        description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithRewards.text())
        price = self.__battlePassController.getBattlePassCost(chapterID).get(Currency.GOLD, 0)
        additionalText = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithRewards.additionalText(), chapter=text_styles.credits(backport.text(R.strings.battle_pass.chapter.dyn(self.__battlePassController.getRewardType(chapterID).value).fullName.num(chapterID)())))
        additionalText += '<br/>' + self.__makeGoldString(price)
        priorityLevel = NotificationPriorityLevel.LOW
        return (header,
         description,
         priorityLevel,
         additionalText)

    def __makeGoldString(self, gold):
        if not gold:
            return ''
        formatter = getBWFormatter(Currency.GOLD)
        return g_settings.htmlTemplates.format(self.__GOLD_TEMPLATE_KEY, {Currency.GOLD: formatter(gold)})


class BattlePassBoughtFormatter(WaitItemsSyncFormatter):

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced and message.data.get('chapter') == 0:
            template = 'BattlePassBuyMultipleMessage'
            header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyMultiple.text())
            formatted = g_settings.msgTemplates.format(template, ctx={'header': header})
            settings = self._getGuiSettings(message, template)
            settings.showAt = BigWorld.time()
            resultMessage = MessageData(formatted, settings)
        callback([resultMessage])
        return


class BattlePassReachedCapFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = 'BattlePassReachedCapMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            vehCD = data.get('vehTypeCompDescr')
            limitPoints = data.get('vehiclePoints')
            bonusPoints = data.get('bonusPoints')
            if vehCD and limitPoints and bonusPoints:
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.reachedCap.text(), vehName=self.__itemsCache.items.getItemByCD(vehCD).userName, bonusPoints=text_styles.neutral(bonusPoints))
                formatted = g_settings.msgTemplates.format(self.__template, {'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return


class BattlePassStyleReceivedFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __template = 'BattlePassStyleReceivedMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            rewardType = self.__battlePass.getRewardType(data.get('chapter'))
            text = ''
            if rewardType == FinalReward.STYLE:
                styleCD = data.get('styleCD')
                if styleCD is not None:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.styleChosen.text(), name=self.__itemsCache.items.getItemByCD(styleCD).userName)
            elif rewardType == FinalReward.TANKMAN:
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.tankmanChosen.text())
            if text:
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.styleChosen.header())
                formatted = g_settings.msgTemplates.format(self.__template, {'header': header,
                 'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return


class BattlePassSeasonEndFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = 'BattlePassSeasonEndMessage'
    __rewardTemplate = 'battlePassDefaultRewardReceived'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            rewards = data.get('data')
            if rewards is not None:
                description = backport.text(R.strings.system_messages.battlePass.seasonEnd.text())
                text = []
                if 'customizations' in rewards:
                    text.extend(self.__formatCustomizationStrings(rewards['customizations']))
                if 'items' in rewards:
                    text.extend(self.__formatItemsStrings(rewards['items']))
                if 'blueprints' in rewards:
                    text.extend(self.__formatBlueprintsStrings(rewards['blueprints']))
                formatted = g_settings.msgTemplates.format(self.__template, {'description': description,
                 'text': '<br>'.join(text)})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return

    def __formatItemsStrings(self, items):
        rewardStrings = []
        for itemCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(itemCD)
            if itemTypeID == I_T.optionalDevice:
                rewardStrings.append(self.__formatOptionalDeviceString(itemCD, count))
            if itemTypeID == I_T.crewBook:
                rewardStrings.append(self.__formatCrewBookString(itemCD, count))

        return rewardStrings

    def __formatOptionalDeviceString(self, itemCD, count):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        if item.isTrophy:
            textRes = R.strings.system_messages.battlePass.seasonEnd.rewards.trophy()
        else:
            textRes = R.strings.system_messages.battlePass.seasonEnd.rewards.device()
        text = backport.text(textRes, name=item.userName)
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {'text': text,
         'count': count})

    def __formatCrewBookString(self, itemCD, count):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        text = backport.text(R.strings.system_messages.battlePass.seasonEnd.rewards.crewBook(), name=item.userName)
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {'text': text,
         'count': count})

    def __formatBlueprintsStrings(self, blueprints):
        rewardStrings = []
        for fragmentCD, count in blueprints.iteritems():
            nation = nations.NAMES[getFragmentNationID(fragmentCD)]
            nationName = backport.text(R.strings.nations.dyn(nation)())
            text = backport.text(R.strings.system_messages.battlePass.seasonEnd.rewards.blueprints(), name=nationName)
            rewardStrings.append(g_settings.htmlTemplates.format(self.__rewardTemplate, {'text': text,
             'count': count}))

        return rewardStrings

    def __formatCustomizationStrings(self, customizations):
        rewardStrings = []
        for item in customizations:
            guiItemType = item['custType']
            itemData = getCustomizationItemData(item['id'], guiItemType)
            typeRes = R.strings.system_messages.battlePass.seasonEnd.rewards.dyn(guiItemType)
            if typeRes.exists():
                text = backport.text(typeRes(), name=itemData.userName)
                rewardStrings.append(g_settings.htmlTemplates.format('battlePassDefaultStyleReceived', {'text': text}))

        return rewardStrings


class BattlePassFreePointsUsedFormatter(ServiceChannelFormatter):
    __template = 'BattlePassFreePointsUsedMessage'
    __battlePassController = dependency.descriptor(IBattlePassController)

    def format(self, message, *args):
        resultMessage = MessageData(None, None)
        if message.data:
            data = message.data
            chapterID = data.get('chapter')
            pointsDiff = data.get('diffPoints')
            if not (chapterID is None or pointsDiff is None):
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.freePointsUsed.header())
                chapterName = backport.text(R.strings.battle_pass.chapter.dyn(self.__battlePassController.getRewardType(chapterID).value).fullName.num(chapterID)())
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.freePointsUsed.text(), chapter=text_styles.credits(chapterName), points=pointsDiff)
                formatted = g_settings.msgTemplates.format(self.__template, {'header': header,
                 'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        return [resultMessage]


class BadgesFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = 'BattlePassBadgesMessage'

    def format(self, message, *args):
        if message.data:
            badges = message.data
            if badges:
                for badgeID, value in badges.iteritems():
                    if badgeID == BATTLE_PASS_BADGE_ID and value.get('amount', 0) < 0:
                        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.badges.header.remove())
                        text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.badges.text.remove(), badgeName=backport.text(R.strings.badge.dyn('badge_{}'.format(badgeID))()))
                        formatted = g_settings.msgTemplates.format(self.__template, {'text': text,
                         'header': header})
                        return [MessageData(formatted, self._getGuiSettings(message, self.__template))]


class CollectibleVehiclesUnlockedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'UnlockedCollectibleVehiclesMessage'

    def format(self, message, *args):
        data = message.data
        if data:
            nationID = data.get('nationID')
            level = data.get('level')
            if nationID is not None and nationID < len(NAMES):
                formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'header': backport.text(R.strings.messenger.serviceChannelMessages.vehicleCollector.unlockLevel.header()),
                 'text': backport.text(R.strings.messenger.serviceChannelMessages.vehicleCollector.unlockLevel.text(), level=int2roman(level), nation=backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase()))})
                return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
        return [MessageData(None, None)]


class TechTreeActionDiscountFormatter(ServiceChannelFormatter):
    __template = 'TechTreeActionDiscountMessage'

    def format(self, message, *args):
        actionName = message.get('actionName', None)
        timeLeft = message.get('timeLeft', None)
        single = message.get('single', True)
        textKey = R.strings.system_messages.techtree.action.text
        if actionName is not None and timeLeft is not None:
            formatted = g_settings.msgTemplates.format(self.__template, {'header': backport.text(R.strings.system_messages.techtree.action.header(), actionName=actionName),
             'text': backport.text(textKey() if single else textKey.closest()),
             'timeLeft': getTillTimeByResource(timeLeft, R.strings.menu.Time.timeLeftShort, useRoundUp=True)})
            return [MessageData(formatted, self._getGuiSettings(message, self.__template))]
        else:
            return [MessageData(None, None)]


class BlueprintsConvertSaleFormatter(ServiceChannelFormatter):
    __templates = {BCSActionState.STARTED: 'BlueprintsConvertSaleStartMessage',
     BCSActionState.PAUSED: 'BlueprintsConvertSalePauseMessage',
     BCSActionState.RESTORE: 'BlueprintsConvertSaleRestoreMessage',
     BCSActionState.END: 'BlueprintsConvertSaleEndMessage'}

    def format(self, message, *args):
        actionName = message.get('state', None)
        if actionName is not None and actionName in self.__templates:
            formatted = g_settings.msgTemplates.format(self.__templates[actionName], {'header': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.header()),
             'text': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.dyn(actionName.value)()),
             'button': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.button())})
            return [MessageData(formatted, self._getGuiSettings(message, self.__templates[actionName]))]
        else:
            return [MessageData(None, None)]


class CustomizationProgressFormatter(WaitItemsSyncFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    @async
    @process
    def format(self, message, callback):
        from gui.customization.shared import checkIsFirstProgressionDecalOnVehicle
        priorityLevel = NotificationPriorityLevel.MEDIUM
        isSynced = yield self._waitForSyncItems()
        if isSynced and message.data:
            messageData = []
            for vehicleCD, items in message.data.iteritems():
                vehicleName = self.itemsCache.items.getItemByCD(vehicleCD).shortUserName if vehicleCD != UNBOUND_VEH_KEY else ''
                isFirst = checkIsFirstProgressionDecalOnVehicle(vehicleCD, items.keys())
                for itemCD, level in items.iteritems():
                    itemName = self.itemsCache.items.getItemByCD(itemCD).userName
                    text = self.__getMessageText(itemName, level, vehicleName)
                    if vehicleName:
                        template = 'ProgressiveItemUpdatedMessage'
                        ctx = {'text': text}
                    else:
                        template = 'notificationsCenterMessage_1'
                        ctx = {'topic': '',
                         'body': text}
                    data = {'savedData': {'itemIntCD': itemCD,
                                   'vehicleIntCD': vehicleCD,
                                   'toProjectionDecals': True}}
                    guiSettings = self._getGuiSettings(message, template, priorityLevel=priorityLevel, messageType=message.type)
                    formatted = g_settings.msgTemplates.format(template, ctx, data=data)
                    messageData.append(MessageData(formatted, guiSettings))

                if isFirst:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.editStyleUnlocked(), vehicleName=vehicleName)
                    ctx = {'text': text}
                    template = 'ProgressiveItemUpdatedMessage'
                    data = {'savedData': {'vehicleIntCD': vehicleCD,
                                   'toStyle': True}}
                    guiSettings = self._getGuiSettings(message, template, priorityLevel=priorityLevel, messageType=message.type)
                    formatted = g_settings.msgTemplates.format(template, ctx, data=data)
                    messageData.append(MessageData(formatted, guiSettings))

            callback(messageData)
        else:
            callback([MessageData(None, None)])
        return

    @staticmethod
    def __getMessageText(itemName, level, vehicleName=''):
        text = ''
        if vehicleName:
            if level == 1:
                text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.itemReceived(), itemName=itemName, vehicleName=vehicleName)
            elif level > 1:
                text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.itemUpdated(), level=level, itemName=itemName, vehicleName=vehicleName)
        elif level == 1:
            text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.itemReceivedNotAutoBound(), itemName=itemName)
        elif level > 1:
            text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.itemUpdatedNotAutoBound(), level=level, itemName=itemName)
        return text


class CustomizationProgressionChangedFormatter(ServiceChannelFormatter):
    REQUIRED_KEYS = {'custType',
     'id',
     'prevLevel',
     'actualLevel'}

    def format(self, message, *args):
        result = [MessageData(None, None)]
        if not message:
            return result
        else:
            data = message.data
            if data and self.REQUIRED_KEYS == set(data.keys()):
                guiItemType, itemUserName = getCustomizationItemData(data['id'], data['custType'])
                prevLevel = data['prevLevel']
                actualLevel = data['actualLevel']
                if actualLevel == 0:
                    return result
                if actualLevel > prevLevel:
                    operation = 'up'
                elif actualLevel < prevLevel:
                    operation = 'down'
                else:
                    return result
                messageR = R.strings.system_messages.customization.progression.dyn(operation).dyn(guiItemType)
                if messageR.exists():
                    messageString = backport.text(messageR(), itemUserName, int2roman(actualLevel))
                else:
                    _logger.warning("CustomizationProgressionChangedFormatter doesn't have message for custType: %s", guiItemType)
                    return result
                formatted = g_settings.msgTemplates.format('CustomizationProgressionMessage', ctx={'message': messageString})
                result = [MessageData(formatted, self._getGuiSettings(message))]
            return result


class PrbEventEnqueueDataFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format('prbWrongEnqueueDataKick', ctx={})
        return [MessageData(formatted, self._getGuiSettings(message, 'prbWrongEnqueueDataKick'))]


class DogTagFormatter(ServiceChannelFormatter):

    @cached_property
    def serviceMessageSource(self):
        return R.strings.messenger.serviceChannelMessages.dogTags

    @cached_property
    def viewTypes(self):
        viewTypeSource = {ComponentViewType.ENGRAVING: self.serviceMessageSource.viewType.engraving(),
         ComponentViewType.BACKGROUND: self.serviceMessageSource.viewType.background()}
        return viewTypeSource

    def getViewTypeText(self, viewType):
        return backport.text(self.viewTypes[viewType])


class DogTagComponentUnlockFormatter(DogTagFormatter):

    def format(self, message, *args):
        if not message:
            return []
        title = backport.text(self.serviceMessageSource.unlockMessage.title())
        lines = []
        composer = dogTagComposer
        for data in message.data:
            component = componentConfigAdapter.getComponentById(int(data))
            viewTypeText = self.getViewTypeText(component.viewType)
            name = composer.getComponentTitle(component.componentId) or 'No name'
            lines.append('{} "{}"'.format(viewTypeText, name))

        messageString = '<br/>'.join(lines)
        ctx = {'title': title,
         'message': messageString}
        templateKey = 'DogTagComponentUnlockMessage'
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
        return [MessageData(formatted, self._getGuiSettings(message))]


class DogTagComponentGradingFormatter(DogTagFormatter):
    grades = {0: 'I',
     1: 'II',
     2: 'III',
     3: 'IV',
     4: 'V',
     5: 'VI',
     6: 'VII',
     7: 'VIII',
     8: 'IX',
     9: 'X',
     10: 'XI',
     11: 'XII',
     12: 'XIII',
     13: 'XIV',
     14: 'XV'}

    def format(self, message, *args):
        if not message:
            return []
        title = backport.text(self.serviceMessageSource.gradingMessage.title())
        lines = []
        composer = dogTagComposer
        for data in message.data:
            compId, grade = data
            component = componentConfigAdapter.getComponentById(int(compId))
            viewTypeText = self.getViewTypeText(component.viewType)
            name = composer.getComponentTitle(component.componentId) or 'No name'
            levelUpToText = backport.text(self.serviceMessageSource.gradingMessage.levelUpToText())
            gradingText = self.grades.get(int(grade), 'No Data')
            lines.append('{viewTypeText} "{name}" {levelUpToText} {gradingText}'.format(viewTypeText=viewTypeText, name=name, levelUpToText=levelUpToText, gradingText=gradingText))

        messageString = '<br/>'.join(lines)
        ctx = {'title': title,
         'message': messageString}
        templateKey = 'DogTagComponentGradingMessage'
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
        return [MessageData(formatted, self._getGuiSettings(message))]


class DedicationRewardFormatter(ServiceChannelFormatter):
    _template = 'DedicationRewardMessage'

    @classmethod
    def _getCountOfCustomizations(cls, rewards):
        customizations = rewards.get('customizations', [])
        totalCount = 0
        for customizationItem in customizations:
            totalCount += customizationItem['value']

        return totalCount

    def format(self, message, *args):
        result = [MessageData(None, None)]
        if message.data:
            data = message.data
            if 'ctx' in data and 'rewards' in data:
                ctx = data['ctx']
                rewards = data['rewards']
                battleCount = ctx.get('reason', 0)
                medalName = _getAchievementsFromQuestData(rewards)
                decalsCount = self._getCountOfCustomizations(rewards)
                if battleCount and medalName and decalsCount:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.dedicationReward.text(), battlesCount=battleCount, medalName=medalName[0], decalsCount=decalsCount)
                    formatted = g_settings.msgTemplates.format(self._template, {'text': text})
                    result = [MessageData(formatted, self._getGuiSettings(message, self._template))]
        return result


class MapboxStartedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'MapboxStartedMessage'

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE)
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class MapboxEndedFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'Mapbox{}Message'
    __REWARDS_LEFT_MSG = 'Ended'
    __NO_REWARDS_LEFT_MSG = 'EndedNoRewards'

    def format(self, message, *args):
        rewards = message.get('rewards')
        if rewards is not None:
            template = self.__TEMPLATE.format(self.__REWARDS_LEFT_MSG)
            resultRewards = {}
            mergeRewards(resultRewards, {reward['name']:reward['value'] for reward in rewards})
            formatted = g_settings.msgTemplates.format(template, {'header': backport.text(R.strings.messenger.serviceChannelMessages.mapbox.congrats.title()),
             'text': backport.text(R.strings.messenger.serviceChannelMessages.mapbox.eventEnded.text()),
             'achieves': QuestAchievesFormatter.formatQuestAchieves(resultRewards, False)})
        else:
            template = self.__TEMPLATE.format(self.__NO_REWARDS_LEFT_MSG)
            formatted = g_settings.msgTemplates.format(template)
        return [MessageData(formatted, self._getGuiSettings(message, template))]


class MapboxSurveyAvailableFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'MapboxSurveyAvailableMessage'
    __STR_PATH = R.strings.messenger.serviceChannelMessages.mapbox

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            mapName = message.get('map')
            header = backport.text(self.__STR_PATH.surveyAvailable.header())
            if mapName in ArenaType.g_geometryNamesToIDs:
                arenaType = ArenaType.g_cache[ArenaType.g_geometryNamesToIDs[mapName]]
                text = backport.text(self.__STR_PATH.surveyAvailable.singleMap(), mapName=arenaType.name)
            else:
                text = backport.text(self.__STR_PATH.surveyAvailable.allMaps())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'header': header,
             'text': text}, data={'savedData': mapName})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, messageSubtype=message.get('msgType')))]


class MapboxRewardReceivedFormatter(ServiceChannelFormatter):
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __TEMPLATE = 'MapboxRewardReceivedMessage'
    __STR_PATH = R.strings.messenger.serviceChannelMessages.mapbox

    def format(self, message, *args):
        rewards = message.get('rewards')
        if rewards is None:
            return [MessageData(None, None)]
        else:
            resultRewards = {}
            textItems = []
            battles = message.get('battles')
            if battles is not None:
                textItems.append(backport.text(self.__STR_PATH.progressionStageCompleted(), battles=battles))
            isFinal = message.get('isFinal', False) and battles is not None
            if isFinal:
                textItems.append(backport.text(self.__STR_PATH.progressionFinalRewardReceived()))
            else:
                textItems.append(backport.text(self.__STR_PATH.rewardReceived()))
            rewards = {item['name']:item['value'] for item in formatMapboxRewards(rewards)}
            mergeRewards(resultRewards, rewards)
            textItems.append(LootBoxAchievesFormatter.formatQuestAchieves(resultRewards, False))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'header': backport.text(self.__STR_PATH.congrats.title()),
             'text': '<br>'.join(textItems)}, data={'savedData': {'rewards': rewards,
                           'battles': battles}})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, messageSubtype=message.get('msgType')))]


class TelecomMergeResultsFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = 'telecomMergeResultsMessage'

    @async
    @process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        data = message.data
        if data and isSynced:
            debitedVehIDs = data.get('debitedVehIDs')
            mergedVehID = data.get('mergedVehID')
            crewVehIDs = data.get('crewVehIDs')
            creditsCompens = data.get('creditsCompens')
            xpCompens = data.get('xpCompens')
            goldCompens = data.get('goldCompens')
            textItems = []
            if mergedVehID:
                mergedVehName = getUserName(vehicles_core.getVehicleType(mergedVehID))
                if debitedVehIDs:
                    debitedVehNames = [ getUserName(vehicles_core.getVehicleType(vehCD)) for vehCD in debitedVehIDs ]
                    debitedVehNamesStr = backport.text(R.strings.system_messages.telecomMergeResults.body.listSeparator()).join(debitedVehNames)
                    textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.accrualMsg(), tanks=debitedVehNamesStr))
                    if len(debitedVehIDs) == 1:
                        textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.equipAndStatisticMovedMsg(), mergedTank=mergedVehName))
                    else:
                        textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.statisticMovedMsg(), mergedTank=mergedVehName))
                        textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.demountMsg()))
                    textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.battleQuestsMsg()))
                else:
                    textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.statisticMovedMsg(), mergedTank=mergedVehName))
                textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.tankXPMsg()))
            if crewVehIDs:
                crewVehNames = [ getUserName(vehicles_core.getVehicleType(vehCD)) for vehCD in crewVehIDs ]
                crewVehNamesStr = backport.text(R.strings.system_messages.telecomMergeResults.body.listSeparator()).join(crewVehNames)
                textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.crewRetrainingMsg(), tanks=crewVehNamesStr))
            if creditsCompens or xpCompens:
                compensationList = []
                if xpCompens:
                    compensationList.append(backport.text(R.strings.system_messages.telecomMergeResults.body.freeXP(), value=text_styles.expText(backport.getIntegralFormat(xpCompens))))
                if creditsCompens:
                    compensationList.append(backport.text(R.strings.system_messages.telecomMergeResults.body.credits(), value=text_styles.credits(backport.getIntegralFormat(creditsCompens))))
                compensationStr = backport.text(R.strings.system_messages.telecomMergeResults.body.conjunction()).join(compensationList)
                textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.postprogressionMsg(), compensation=compensationStr))
            if goldCompens:
                textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.progressDecalesCompens(), value=goldCompens))
            textItems.append(backport.text(R.strings.system_messages.telecomMergeResults.body.wishMsg()))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'text': '<br>'.join(textItems)})
            callback([MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))])
        else:
            callback([MessageData(None, None)])
        return
