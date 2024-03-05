# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/service_channel.py
from __future__ import unicode_literals
import logging
import operator
import time
import types
from Queue import Queue
from collections import OrderedDict, defaultdict, deque
from copy import copy, deepcopy
from itertools import islice, chain
import typing
import ArenaType
import BigWorld
import constants
import nations
import personal_missions
from adisp import adisp_async, adisp_process
from battle_pass_common import BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS, BATTLE_PASS_TOKEN_3D_STYLE, BattlePassRewardReason, FinalReward
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from cache import cached_property
from chat_shared import MapRemovedFromBLReason, SYS_MESSAGE_TYPE, decompressSysMessage
from constants import ARENA_BONUS_TYPE, ARENA_GUI_TYPE, AUTO_MAINTENANCE_RESULT, AUTO_MAINTENANCE_TYPE, FAIRPLAY_VIOLATIONS, FINISH_REASON, INVOICE_ASSET, KICK_REASON, KICK_REASON_NAMES, NC_MESSAGE_PRIORITY, NC_MESSAGE_TYPE, OFFER_TOKEN_PREFIX, PREBATTLE_TYPE, PREMIUM_ENTITLEMENTS, PREMIUM_TYPE, RESTRICTION_TYPE, SYS_MESSAGE_CLAN_EVENT, SYS_MESSAGE_CLAN_EVENT_NAMES, SYS_MESSAGE_FORT_EVENT_NAMES, SwitchState
from debug_utils import LOG_ERROR
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from dossiers2.custom.records import DB_ID_TO_RECORD, RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from epic_constants import EPIC_BATTLE_LEVEL_IMAGE_INDEX
from goodies.goodie_constants import GOODIE_VARIETY
from gui import GUI_NATIONS, GUI_SETTINGS, makeHtmlString
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.SystemMessages import SM_TYPE
from gui.clans.formatters import getClanFullName
from gui.collection.collections_constants import COLLECTION_ITEM_PREFIX_NAME
from gui.dog_tag_composer import dogTagComposer
from gui.game_control.blueprints_convert_sale_controller import BCSActionState
from gui.impl import backport
from gui.impl.backport import getNiceNumberFormat
from gui.impl.gen import R
from gui.impl.lobby.winback.winback_helpers import getLevelFromSelectableToken, getDiscountFromGoody, getDiscountFromBlueprint
from gui.mapbox.mapbox_helpers import formatMapboxRewards
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.ranked_battles.constants import YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX, YEAR_POINTS_TOKEN
from gui.ranked_battles.ranked_helpers import getBonusBattlesIncome, getQualificationBattlesCountFromID, isQualificationQuestID
from gui.ranked_battles.ranked_models import PostBattleRankInfo, RankChangeStates
from gui.resource_well.resource_well_constants import ResourceType
from gui.achievements.achievements_constants import Achievements20SystemMessages
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CompletionTokensBonusFormatter, CREW_BONUS_X3_TOKEN
from gui.server_events.bonuses import DEFAULT_CREW_LVL, EntitlementBonus, MetaBonus, VehiclesBonus, SelectableBonus
from gui.server_events.finders import PERSONAL_MISSION_TOKEN
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared import formatters as shared_fmts
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.currency import applyAll, getBWFormatter, getStyle
from gui.shared.formatters.time_formatters import RentDurationKeys, getTillTimeByResource, getTimeLeftInfo
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import getShortUserName, getUserName, getWotPlusExclusiveVehicleTypeUserName
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.dossier.achievements.abstract.class_progress import ClassProgressAchievement
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.gui_items.loot_box import REFERRAL_PROGRAM_CATEGORY
from gui.shared.money import Currency, MONEY_UNDEFINED, Money, ZERO_MONEY
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel
from gui.shared.system_factory import collectTokenQuestsSubFormatters
from gui.shared.utils.requesters.ShopRequester import _NamedGoodieData
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID, getUniqueBlueprints
from gui.shared.utils.transport import z_loads
from gui.battle_pass.battle_pass_constants import ChapterState
from helpers import dependency, getLocalizedData, html, i18n, int2roman, time_utils
from items import ITEM_TYPES as I_T, getTypeInfoByIndex, getTypeInfoByName, tankmen, vehicles as vehicles_core, ITEM_TYPE_NAMES
from items.components.c11n_constants import CustomizationType, CustomizationTypeNames, UNBOUND_VEH_KEY
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from items.vehicles import getVehicleType
from maps_training_common.maps_training_constants import SCENARIO_INDEXES, SCENARIO_RESULT
from messenger import g_settings
from messenger.ext import passCensor
from messenger.formatters import NCContextItemFormatter, TimeFormatter
from messenger.formatters.service_channel_helpers import EOL, MessageData, getCustomizationItem, getCustomizationItemData, getRewardsForQuests, mergeRewards, popCollectionEntitlements
from nations import NAMES
from shared_utils import BoundMethodWeakref, first
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IBattlePassController, IBattleRoyaleController, ICollectionsSystemController, IEpicBattleMetaGameController, IFunRandomController, IMapboxController, IRankedBattlesController, IResourceWellController, IWinbackController, IWotPlusController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.comp7.comp7_quest_helpers import isComp7Quest, getComp7QuestType
from comp7_common import Comp7QuestType, COMP7_TOKEN_WEEKLY_REWARD_ID
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Tuple, Callable, Optional
    from account_helpers.offers.events_data import OfferEventData, OfferGift
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from messenger.proto.bw.wrappers import ServiceChannelMessage
_logger = logging.getLogger(__name__)
_TEMPLATE = u'template'
_RENT_TYPE_NAMES = {RentDurationKeys.DAYS: u'rentDays',
 RentDurationKeys.BATTLES: u'rentBattles',
 RentDurationKeys.WINS: u'rentWins'}
_PREMIUM_MESSAGES = {PREMIUM_TYPE.BASIC: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumBought(),
                      str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumExtended(),
                      str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumExpired(),
                      str(SYS_MESSAGE_TYPE.premiumChanged): R.strings.messenger.serviceChannelMessages.premiumChanged()},
 PREMIUM_TYPE.PLUS: {str(SYS_MESSAGE_TYPE.premiumBought): R.strings.messenger.serviceChannelMessages.premiumPlusBought(),
                     str(SYS_MESSAGE_TYPE.premiumExtended): R.strings.messenger.serviceChannelMessages.premiumPlusExtended(),
                     str(SYS_MESSAGE_TYPE.premiumExpired): R.strings.messenger.serviceChannelMessages.premiumPlusExpired(),
                     str(SYS_MESSAGE_TYPE.premiumChanged): R.strings.messenger.serviceChannelMessages.premiumPlusChanged()}}
_PREMIUM_TEMPLATES = {PREMIUM_ENTITLEMENTS.BASIC: u'battleQuestsPremium',
 PREMIUM_ENTITLEMENTS.PLUS: u'battleQuestsPremiumPlus'}
_PROGRESSION_INVOICE_POSTFIX = u'progression'
EPIC_LEVELUP_TOKEN_TEMPLATE = u'epicmetagame:levelup:'

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
        customizations = newData.get(u'customizations', [])
        for customizationItem in customizations:
            splittedCustType = customizationItem.get(u'custType', u'').split(u':')
            custType = splittedCustType[0]
            custValue = customizationItem[u'value']
            if len(splittedCustType) == 2 and _PROGRESSION_INVOICE_POSTFIX in splittedCustType[1]:
                continue
            if custValue > 0:
                operation = u'added'
            elif custValue < 0:
                operation = u'removed'
            else:
                operation = None
            if operation is not None:
                guiItemType, itemUserName = getCustomizationItemData(customizationItem[u'id'], custType)
                custValue = abs(custValue)
                if custValue > 1:
                    extendable.append(backport.text(R.strings.system_messages.customization.dyn(operation).dyn(u'{}Value'.format(guiItemType))(), itemUserName, custValue))
                else:
                    extendable.append(backport.text(R.strings.system_messages.customization.dyn(operation).dyn(guiItemType)(), itemUserName))
            if u'compensatedNumber' in customizationItem:
                compStr = InvoiceReceivedFormatter.getCustomizationCompensationString(customizationItem, htmlTplPostfix=htmlTplPostfix)
                if compStr:
                    extendable.append(compStr)

        return


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def _extendCrewSkinsData(newData, extendable, lobbyContext=None, itemsCache=None):
    if extendable is None:
        return
    else:
        crewSkinsData = newData.get(u'crewSkins', None)
        if crewSkinsData is None:
            return
        totalCompensation = ZERO_MONEY
        accrued = []
        debited = []
        for crewSkinData in crewSkinsData:
            crewSkinID = crewSkinData.get(u'id', NO_CREW_SKIN_ID)
            count = crewSkinData.get(u'count', 0)
            if crewSkinID != NO_CREW_SKIN_ID:
                totalCompensation += Money(credits=crewSkinData.get(u'customCompensation', 0))
                if count:
                    crewSkinItem = itemsCache.items.getCrewSkin(crewSkinID)
                    if crewSkinItem is not None:
                        crewSkinUserStrings = accrued if count > 0 else debited
                        if abs(count) > 1:
                            crewSkinUserStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.crewSkinsCount(), label=localizedFullName(crewSkinItem), count=str(abs(count))))
                        else:
                            crewSkinUserStrings.append(localizedFullName(crewSkinItem))

        if accrued:
            resultStr = g_settings.htmlTemplates.format(u'crewSkinsAccruedReceived', ctx={u'crewSkins': u', '.join(accrued)})
            extendable.append(resultStr)
        if debited:
            resultStr = g_settings.htmlTemplates.format(u'crewSkinsDebitedReceived', ctx={u'crewSkins': u', '.join(debited)})
            extendable.append(resultStr)
        formattedCurrencies = []
        currencies = totalCompensation.getSetCurrencies(byWeight=True)
        for currency in currencies:
            formattedCurrencies.append(applyAll(currency, totalCompensation.get(currency=currency)))

        if formattedCurrencies:
            extendable.append(backport.text(R.strings.system_messages.crewSkinsCompensation.success(), compensation=u', '.join(formattedCurrencies)))
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
                rares.append(rec[u'value'])

    return rares


def _toPairLists(dct):
    return [ [k, v] for k, v in dct.iteritems() ]


def _composeAchievements(dossiers):
    result = {}
    for dossierKey, rec in dossiers.iteritems():
        uniqueReceived, uniqueRemoved, other = {}, {}, []
        it = rec if not isinstance(rec, dict) else rec.iteritems()
        for recType, recData in it:
            value = recData[u'value']
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
    if savedRecData[u'type'] == recData[u'type']:
        savedRecData[u'value'] += recData[u'value']
        savedActualValue = savedRecData[u'actualValue']
        updateFunc = max if recData[u'value'] > 0 else min
        savedRecData[u'actualValue'] = updateFunc(savedActualValue, recData[u'actualValue'])
    else:
        nonMerged.append([recType, recData])


def _getFormatAchieveString(name, block, recData):
    if u'actualValue' in recData:
        achieve = getAchievementFactory((block, name)).create(recData[u'actualValue'])
    else:
        achieve = None
        _logger.warning(u"Couldn't find 'actualValue' field in data %s", recData)
    if achieve is not None:
        achieveName = achieve.getUserName()
    else:
        achieveName = backport.text(R.strings.achievements.dyn(name)())
    if not isinstance(achieve, ClassProgressAchievement):
        value = abs(recData[u'value'])
        if value > 1:
            return u''.join((achieveName, backport.text(R.strings.messenger.serviceChannelMessages.multiplier(), count=backport.getIntegralFormat(value))))
    return achieveName


def _getRaresAchievementsStrings(battleResults):
    dossiers = battleResults.get(u'dossier', {})
    rares = []
    for d in dossiers.itervalues():
        it = d if not isinstance(d, dict) else d.iteritems()
        for (blck, _), rec in it:
            if blck == ACHIEVEMENT_BLOCK.RARE:
                value = rec[u'value']
                if value > 0:
                    rares.append(value)

    return _processRareAchievements(rares) if rares else None


def _getCrewBookUserString(itemDescr):
    params = {}
    if itemDescr.type not in CREW_BOOK_RARITY.NO_NATION_TYPES:
        params[u'nation'] = i18n.makeString(u'#nations:{}'.format(itemDescr.nation))
    return i18n.makeString(itemDescr.name, **params)


def _getAchievementsFromQuestData(data):
    achievesList = []
    for rec in data.get(u'dossier', {}).values():
        it = rec if not isinstance(rec, dict) else rec.iteritems()
        for (block, name), value in it:
            if block not in ACHIEVEMENT_BLOCK.ALL:
                continue
            achieve = getAchievementFactory((block, name)).create(value.get(u'actualValue', 0))
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
            return g_settings.htmlTemplates.format(u'battlePassTMan', {u'text': text})
    return


def _processOfferToken(tokenName, count):
    if tokenName.startswith(OFFER_TOKEN_PREFIX):
        text = backport.text(R.strings.messenger.serviceChannelMessages.offerTokenBonus.title())
        offerName = g_settings.htmlTemplates.format(u'offerTokenText', {u'text': text})
        template = u'offersAccruedInvoiceReceived' if count > 0 else u'offersDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {u'offer': offerName})
    else:
        return None


@dependency.replace_none_kwargs(collections=ICollectionsSystemController)
def _getCollectionItemName(entitlementName, collections=None):
    from gui.collection.collections_helpers import getItemName
    collectionID, itemID = entitlementName.split(u'_')[2:]
    return getItemName(int(collectionID), collections.getCollectionItem(int(collectionID), int(itemID)))


class ServiceChannelFormatter(object):

    def format(self, data, *args):
        return []

    def isNotify(self):
        return True

    def isAsync(self):
        return False

    def canBeEmpty(self):
        return False

    def _getGuiSettings(self, data, key=None, priorityLevel=None, messageType=None, messageSubtype=None, decorator=None):
        try:
            isAlert = data.isHighImportance and data.active
        except AttributeError:
            isAlert = False

        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        lifeTime = g_settings.msgTemplates.lifeTime(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel, isAlert, messageType=messageType, messageSubtype=messageSubtype, decorator=decorator, lifeTime=lifeTime)


class SimpleFormatter(ServiceChannelFormatter):

    def __init__(self, templateName):
        self._template = templateName

    def format(self, message, *args):
        if message is None:
            return []
        else:
            formatted = g_settings.msgTemplates.format(self._template, ctx=self.getCtx(message, *args))
            return [MessageData(formatted, self._getGuiSettings(message, self._template))]

    def getCtx(self, message, *args):
        return None

    def getConvertedDateTime(self, dTime):
        return TimeFormatter.getShortDatetimeFormat(time_utils.makeLocalServerTime(dTime))


class ExclusiveVehicleWotPlusFormatter(ServiceChannelFormatter):

    def __init__(self, isEnabled=False):
        self.template = u'WotPlusExclusiveVehicleDisabledMessage' if not isEnabled else u'WotPlusExclusiveVehicleEnabledMessage'

    def format(self, message, *args):
        if message.data:
            formatted = g_settings.msgTemplates.format(self.template, ctx={u'vehicleName': self.__getVehicleName(message.data.get(u'vehCD', -1)),
             u'vehicleType': self.__getVehicleType(message.data.get(u'vehCD', -1))})
            return [MessageData(formatted, self._getGuiSettings(message, self.template))]
        return []

    def __getVehicleName(self, vehTypeCD):
        return getUserName(getVehicleType(vehTypeCD))

    def __getVehicleType(self, vehTypeCD):
        return getWotPlusExclusiveVehicleTypeUserName(getVehicleType(vehTypeCD).getVehicleClass())


class WaitItemsSyncFormatter(ServiceChannelFormatter):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__callbackQueue = None
        return

    def isAsync(self):
        return True

    @adisp_async
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
                _logger.exception(u'Exception in service channel formatter')

        self.__unregisterHandler()


class ServerRebootFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format(u'serverReboot', ctx={u'date': local_dt.strftime(u'%c')})
            return [MessageData(formatted, self._getGuiSettings(message, u'serverReboot'))]
        else:
            return [MessageData(None, None)]


class ServerRebootCancelledFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        if message.data:
            local_dt = time_utils.utcToLocalDatetime(message.data)
            formatted = g_settings.msgTemplates.format(u'serverRebootCancelled', ctx={u'date': local_dt.strftime(u'%c')})
            return [MessageData(formatted, self._getGuiSettings(message, u'serverRebootCancelled'))]
        else:
            return [MessageData(None, None)]


class FormatSpecialReward(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __winbackController = dependency.descriptor(IWinbackController)
    __funRandomController = dependency.descriptor(IFunRandomController)

    def getString(self, message):
        formattedItems = self.__formattedItems(message)
        return None if not formattedItems else g_settings.msgTemplates.format(u'specialReward', ctx={u'specialRewardItems': formattedItems})

    def __formattedItems(self, message):
        data = message.data
        itemsNames = []
        data = self.__extractExcludedItems(data)
        itemsNames.extend(self.__getCrewBookNames(data.get(u'items', {})))
        itemsNames.extend(self.__getBlueprintNames(data.get(u'blueprints', {})))
        return None if not itemsNames else g_settings.htmlTemplates.format(u'specialRewardItems', ctx={u'names': u'<br/>'.join(itemsNames)})

    def __getCrewBookNames(self, items):
        result = []
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

    def __extractExcludedItems(self, data):
        excludeFilters = (self.__battleMattersController.isBattleMattersQuestID, self.__funRandomController.progressions.isProgressionExecutor, self.__winbackController.isWinbackQuest)
        excludedQuests = (qID for qID in data.get(u'completedQuestIDs', set()) if any((excludeFilter(qID) for excludeFilter in excludeFilters)))
        processingTypes = (u'blueprints', u'items')
        resultData = {rewardType:copy(data.get(rewardType, {})) for rewardType in processingTypes}
        for rewardType in processingTypes:
            for questID in excludedQuests:
                rewards = data[u'detailedRewards'][questID].get(rewardType, {})
                for k, v in rewards.iteritems():
                    resultData[rewardType][k] -= v
                    if resultData[rewardType][k] <= 0:
                        resultData[rewardType].pop(k)

            if not resultData[rewardType]:
                resultData.pop(rewardType)

        return resultData


class Comp7BattleQuestsFormatter(object):

    def format(self, message):
        formattedSysMessages = []
        if message.data:
            for questID in self.__getComp7Quests(message.data.get(u'completedQuestIDs', set())):
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
        return set((qId for qId in questIDs if isComp7Quest(qId)))

    def __formatWeeklyReward(self, message, questID):
        rewardsData = message.data.get(u'detailedRewards', {}).get(questID, {})
        if rewardsData:
            achievesFormatter = QuestAchievesFormatter()
            return g_settings.msgTemplates.format(u'comp7RegularRewardMessage', ctx={u'title': backport.text(R.strings.comp7.system_messages.weeklyReward.title()),
             u'body': backport.text(R.strings.comp7.system_messages.weeklyReward.body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False))})
        else:
            return None

    def __formatTokensReward(self, message, questID):
        rewardsData = message.data.get(u'detailedRewards', {}).get(questID, {})
        dossierData = rewardsData.get(u'dossier')
        if dossierData:
            popUps = self.__getDossierPopUps(dossierData, message.data.get(u'popUpRecords', set()))
            rewardsData.update({u'popUpRecords': popUps})
        if rewardsData:
            achievesFormatter = QuestAchievesFormatter()
            return g_settings.msgTemplates.format(u'comp7RegularRewardMessage', ctx={u'title': backport.text(R.strings.comp7.system_messages.tokenWeeklyReward.title()),
             u'body': backport.text(R.strings.comp7.system_messages.tokenWeeklyReward.body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False))})
        else:
            return None

    def __getDossierPopUps(self, dossierData, popUpRecords):
        popUps = set()
        for dossierRecord in chain.from_iterable(dossierData.values()):
            if dossierRecord[0] in ACHIEVEMENT_BLOCK.ALL:
                achievementID = RECORD_DB_IDS.get(dossierRecord, None)
                popUps.update((popUp for popUp in popUpRecords if popUp[0] == achievementID))

        return popUps


class BattleResultsFormatter(WaitItemsSyncFormatter):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _battleResultKeys = {-1: u'battleDefeatResult',
     0: u'battleDrawGameResult',
     1: u'battleVictoryResult'}
    __BRResultKeys = {-1: u'battleRoyaleDefeatResult',
     0: u'battleRoyaleDefeatResult',
     1: u'battleRoyaleVictoryResult'}
    __MTResultKeys = {SCENARIO_RESULT.LOSE: u'mapsTrainingDefeatResult',
     SCENARIO_RESULT.WIN: u'mapsTrainingVictoryResult'}
    __COMP7SeasonResultsKeys = {SCENARIO_RESULT.LOSE: u'comp7SeasonBattleDefeatResult',
     SCENARIO_RESULT.PARTIAL: u'comp7SeasonBattleDrawGameResult',
     SCENARIO_RESULT.WIN: u'comp7SeasonBattleVictoryResult'}
    __COMP7QualificationResultsKeys = {SCENARIO_RESULT.LOSE: u'comp7QualificationBattleDefeatResult',
     SCENARIO_RESULT.PARTIAL: u'comp7QualificationBattleDrawGameResult',
     SCENARIO_RESULT.WIN: u'comp7QualificationBattleVictoryResult'}
    __goldTemplateKey = u'battleResultGold'
    __questsTemplateKey = u'battleQuests'

    def isNotify(self):
        return True

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            battleResults = message.data
            arenaTypeID = battleResults.get(u'arenaTypeID', 0)
            if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
                arenaType = ArenaType.g_cache[arenaTypeID]
            else:
                arenaType = None
            arenaCreateTime = battleResults.get(u'arenaCreateTime', None)
            if arenaCreateTime and arenaType:
                ctx = {u'arenaName': i18n.makeString(arenaType.name),
                 u'vehicleNames': u'N/A',
                 u'xp': u'0',
                 Currency.CREDITS: u'0'}
                templateName, formatData = self._prepareFormatData(message)
                ctx.update(formatData)
                bgIconSource = None
                arenaUniqueID = battleResults.get(u'arenaUniqueID', 0)
                formatted = g_settings.msgTemplates.format(templateName, ctx=ctx, data={u'timestamp': arenaCreateTime,
                 u'savedData': arenaUniqueID}, bgIconSource=bgIconSource)
                formattedSpecialReward = FormatSpecialReward().getString(message)
                settings = self._getGuiSettings(message, templateName)
                settings.showAt = BigWorld.time()
                messages = list()
                if formattedSpecialReward:
                    messages.append(MessageData(formattedSpecialReward, settings))
                comp7QuestsFormatter = Comp7BattleQuestsFormatter()
                for reward in comp7QuestsFormatter.format(message):
                    messages.append(MessageData(reward, settings))

                messages.append(MessageData(formatted, settings))
                callback(messages)
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return

    def _prepareFormatData(self, message):
        battleResults = message.data
        ctx = {}
        vehicleNames = {intCD:self._itemsCache.items.getItemByCD(intCD) for intCD in battleResults.get(u'playerVehicles', {}).keys()}
        ctx[u'vehicleNames'] = u', '.join(map(operator.attrgetter(u'userName'), sorted(vehicleNames.values())))
        xp = battleResults.get(u'xp')
        if xp:
            ctx[u'xp'] = backport.getIntegralFormat(xp)
        battleResKey = battleResults.get(u'isWinner', 0)
        ctx[u'xpEx'] = self.__makeXpExString(xp, battleResKey, battleResults.get(u'xpPenalty', 0), battleResults)
        ctx[Currency.GOLD] = self.__makeGoldString(battleResults.get(Currency.GOLD, 0))
        accCredits = battleResults.get(Currency.CREDITS) - battleResults.get(u'creditsToDraw', 0)
        if accCredits:
            ctx[Currency.CREDITS] = self.__makeCurrencyString(Currency.CREDITS, accCredits)
        ctx[u'piggyBank'] = self.__makePiggyBankString(battleResults.get(u'piggyBank'))
        accCrystal = battleResults.get(Currency.CRYSTAL)
        ctx[u'crystalStr'] = u''
        if accCrystal:
            ctx[Currency.CRYSTAL] = self.__makeCurrencyString(Currency.CRYSTAL, accCrystal)
            ctx[u'crystalStr'] = g_settings.htmlTemplates.format(u'battleResultCrystal', {Currency.CRYSTAL: ctx[Currency.CRYSTAL]})
        accEventCoin = battleResults.get(Currency.EVENT_COIN)
        ctx[u'eventCoinStr'] = u''
        if accEventCoin:
            ctx[Currency.EVENT_COIN] = self.__makeCurrencyString(Currency.EVENT_COIN, accEventCoin)
            ctx[u'eventCoinStr'] = g_settings.htmlTemplates.format(u'battleResultEventCoin', {Currency.EVENT_COIN: ctx[Currency.EVENT_COIN]})
        accBpcoin = battleResults.get(Currency.BPCOIN)
        ctx[u'bpcoinStr'] = u''
        if accBpcoin:
            ctx[Currency.BPCOIN] = self.__makeCurrencyString(Currency.BPCOIN, accBpcoin)
            ctx[u'bpcoinStr'] = g_settings.htmlTemplates.format(u'battleResultBpcoin', {Currency.BPCOIN: ctx[Currency.BPCOIN]})
        accEqCoin = battleResults.get(Currency.EQUIP_COIN)
        ctx[u'equipCoinStr'] = u''
        if accEqCoin:
            ctx[Currency.EQUIP_COIN] = self.__makeCurrencyString(Currency.EQUIP_COIN, accEqCoin)
            ctx[u'equipCoinStr'] = g_settings.htmlTemplates.format(u'battleResultEquipCoin', {Currency.EQUIP_COIN: ctx[Currency.EQUIP_COIN]})
        ctx[u'creditsEx'] = self.__makeCreditsExString(accCredits, battleResults.get(u'creditsPenalty', 0), battleResults.get(u'creditsContributionIn', 0), battleResults.get(u'creditsContributionOut', 0))
        platformCurrencies = battleResults.get(u'currencies', {})
        if platformCurrencies:
            ctx[u'platformCurrencyStr'] = u'<br/>' + u'<br/>'.join((g_settings.htmlTemplates.format(u'platformCurrency', {u'msg': backport.text(R.strings.messenger.platformCurrencyMsg.received.dyn(currency)()),
             u'count': backport.getIntegralFormat(countDict.get(u'count', 0))}) for currency, countDict in platformCurrencies.iteritems()))
        else:
            ctx[u'platformCurrencyStr'] = u''
        guiType = battleResults.get(u'guiType', 0)
        ctx[u'achieves'], ctx[u'badges'] = self.__makeAchievementsAndBadgesStrings(battleResults)
        ctx[u'rankedProgress'] = self.__makeRankedFlowStrings(battleResults)
        ctx[u'rankedBonusBattles'] = self.__makeRankedBonusString(battleResults)
        ctx[u'battlePassProgress'] = self.__makeBattlePassProgressionString(guiType, battleResults)
        ctx[u'lock'] = self.__makeVehicleLockString(vehicleNames, battleResults)
        ctx[u'quests'] = self.__makeQuestsAchieve(message)
        team = battleResults.get(u'team', 0)
        if guiType == ARENA_GUI_TYPE.FORT_BATTLE_2 or guiType == ARENA_GUI_TYPE.SORTIE_2:
            if battleResKey == 0:
                winnerIfDraw = battleResults.get(u'winnerIfDraw')
                if winnerIfDraw:
                    battleResKey = 1 if winnerIfDraw == team else -1
        if guiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
            ctx[u'brcoin'] = self.__makeBRCoinString(battleResults)
            battleResultKeys = self.__BRResultKeys
        elif guiType == ARENA_GUI_TYPE.MAPS_TRAINING:
            ctx = self.__makeMapsTrainingMsgCtx(battleResults, ctx)
            battleResKey = battleResults.get(u'mtScenarioResult')
            battleResultKeys = self.__MTResultKeys
        elif guiType == ARENA_GUI_TYPE.COMP7:
            isQualificationBattle = battleResults.get(u'comp7QualActive', False)
            if isQualificationBattle:
                battleResultKeys = self.__COMP7QualificationResultsKeys
            else:
                battleResultKeys = self.__COMP7SeasonResultsKeys
                ctx = self.__makeComp7SeasonMsgCtx(battleResults, ctx)
        else:
            battleResultKeys = self._battleResultKeys
        templateName = battleResultKeys[battleResKey]
        return (templateName, ctx)

    def __makeMapsTrainingMsgCtx(self, battleResults, ctx):
        vehTypeCompDescr = next(battleResults[u'playerVehicles'].iterkeys())
        vType = vehicles_core.getVehicleType(vehTypeCompDescr)
        vehicleClass = vehicles_core.getVehicleClassFromVehicleType(vType)
        team = battleResults[u'team']
        vehTypeStr = backport.text(R.strings.maps_training.vehicleType.dyn(vehicleClass)())
        ctx[u'baseStr'] = backport.text(R.strings.maps_training.baseNum()).format(base=team)
        ctx[u'mtRewards'] = self.__makeMapsTrainingRewardsMsg(battleResults)
        ctx[u'scenario'] = backport.text(R.strings.maps_training.scenarioTooltip.scenario.title()).format(num=SCENARIO_INDEXES[team, vehicleClass], vehicleType=vehTypeStr)
        return ctx

    def __makeMapsTrainingRewardsMsg(self, battleResults):
        if not battleResults.get(u'mtCanGetRewards'):
            return g_settings.htmlTemplates.format(u'mtRewardGot')
        rewards = []
        creditsReward = battleResults.get(u'credits', 0)
        creditsXMLString = u'mtCreditsHighlight' if creditsReward else u'mtCredits'
        rewards.append(g_settings.htmlTemplates.format(creditsXMLString, ctx={u'credits': self.__makeCurrencyString(Currency.CREDITS, creditsReward)}))
        freeXP = battleResults.get(u'freeXP', 0)
        if freeXP:
            rewards.append(g_settings.htmlTemplates.format(u'mtFreeXP', ctx={u'freeXP': backport.getIntegralFormat(freeXP)}))
        questResults = QuestAchievesFormatter.formatQuestAchieves(battleResults, asBattleFormatter=True)
        if questResults:
            rewards.append(g_settings.htmlTemplates.format(u'mtQuests', ctx={u'quests': questResults}))
        return u'<br/>'.join(rewards)

    def __makeComp7SeasonMsgCtx(self, battleResults, ctx):
        ctx[u'ratingPointsStr'] = g_settings.htmlTemplates.format(u'battleResultRatingPoints', {u'ratingPoints': u'{:+}'.format(battleResults[u'comp7RatingDelta'])})
        return ctx

    def __makeQuestsAchieve(self, message):
        fmtMsg = QuestAchievesFormatter.formatQuestAchieves(message.data, asBattleFormatter=True)
        return g_settings.htmlTemplates.format(u'battleQuests', {u'achieves': fmtMsg}) if fmtMsg is not None else u''

    def __makeVehicleLockString(self, vehicleNames, battleResults):
        locks = []
        for vehIntCD, battleResult in battleResults.get(u'playerVehicles', {}).iteritems():
            expireTime = battleResult.get(u'vehTypeUnlockTime', 0)
            if not expireTime:
                continue
            vehicleName = vehicleNames.get(vehIntCD)
            if vehicleName is None:
                continue
            locks.append(g_settings.htmlTemplates.format(u'battleResultLocks', ctx={u'vehicleName': vehicleName,
             u'expireTime': TimeFormatter.getLongDatetimeFormat(expireTime)}))

        return u', '.join(locks)

    def __makeXpExString(self, xp, battleResKey, xpPenalty, battleResults):
        if not xp:
            return u''
        exStrings = []
        if xpPenalty > 0:
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.penaltyForDamageAllies(), backport.getIntegralFormat(xpPenalty)))
        if battleResKey == 1:
            xpFactorStrings = []
            xpFactor = battleResults.get(u'dailyXPFactor', 1)
            if xpFactor > 1:
                xpFactorStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.doubleXpFactor()) % xpFactor)
            if xpFactorStrings:
                exStrings.append(u', '.join(xpFactorStrings))
        return u' ({0:s})'.format(u'; '.join(exStrings)) if exStrings else u''

    def __makeCreditsExString(self, accCredits, creditsPenalty, creditsContributionIn, creditsContributionOut):
        if not accCredits:
            return u''
        formatter = getBWFormatter(Currency.CREDITS)
        exStrings = []
        penalty = sum([creditsPenalty, creditsContributionOut])
        if penalty > 0:
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.penaltyForDamageAllies(), formatter(penalty)))
        if creditsContributionIn > 0:
            exStrings.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.contributionForDamageAllies(), formatter(creditsContributionIn)))
        return u' ({0:s})'.format(u'; '.join(exStrings)) if exStrings else u''

    def __makeGoldString(self, gold):
        if not gold:
            return u''
        formatter = getBWFormatter(Currency.GOLD)
        return g_settings.htmlTemplates.format(self.__goldTemplateKey, {Currency.GOLD: formatter(gold)})

    def __makeCurrencyString(self, currency, credit):
        formatter = getBWFormatter(currency)
        return formatter(credit)

    def __makeAchievementsAndBadgesStrings(self, battleResults):
        popUpRecords = []
        badges = []
        for _, vehBattleResults in battleResults.get(u'playerVehicles', {}).iteritems():
            for recordIdx, value in vehBattleResults.get(u'popUpRecords', []):
                recordName = DB_ID_TO_RECORD[recordIdx]
                if recordName in IGNORED_BY_BATTLE_RESULTS:
                    continue
                block, name = recordName
                if block == BADGES_BLOCK:
                    badges.append(name)
                achieve = getAchievementFactory(recordName).create(value=value)
                if achieve is not None and achieve not in popUpRecords:
                    popUpRecords.append(achieve)

            if u'markOfMastery' in vehBattleResults and vehBattleResults[u'markOfMastery'] > 0:
                popUpRecords.append(getAchievementFactory((ACHIEVEMENT_BLOCK.TOTAL, u'markOfMastery')).create(value=vehBattleResults[u'markOfMastery']))

        achievementsStrings = [ a.getUserName() for a in sorted(popUpRecords) ]
        raresStrings = _getRaresAchievementsStrings(battleResults)
        if raresStrings:
            achievementsStrings.extend(raresStrings)
        achievementsBlock = u''
        if achievementsStrings:
            achievementsBlock = g_settings.htmlTemplates.format(u'battleResultAchieves', {u'achieves': u', '.join(achievementsStrings)})
        badgesBlock = u''
        if badges:
            badgesStr = u', '.join([ backport.text(R.strings.badge.dyn(u'badge_{}'.format(badgeID))()) for badgeID in badges ])
            badgesBlock = u'<br/>' + g_settings.htmlTemplates.format(u'badgeAchievement', {u'badges': badgesStr})
        return (achievementsBlock, badgesBlock)

    def __makeRankedFlowStrings(self, battleResults):
        rankedProgressStrings = []
        if battleResults.get(u'guiType', 0) == ARENA_GUI_TYPE.RANKED:
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
                isWin = True if battleResults.get(u'isWinner', 0) > 0 else False
                if stateChange == RankChangeStates.NOTHING_CHANGED and isWin:
                    stateChangeStr = backport.text(shortcut.rankedState.stageNotEarned())
                shieldState = rankInfo.shieldState
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
                    stateChangeStr = backport.text(shortcut.rankedState.shieldLose())
            rankedProgressStrings.append(stateChangeStr)
        rankedProgressBlock = u''
        if rankedProgressStrings:
            rankedProgressBlock = g_settings.htmlTemplates.format(u'battleResultRankedProgress', {u'rankedProgress': u', '.join(rankedProgressStrings)})
        return rankedProgressBlock

    def __makeRankedBonusString(self, battleResults):
        bonusBattlesString = u''
        if battleResults.get(u'guiType', 0) == ARENA_GUI_TYPE.RANKED:
            rankInfo = PostBattleRankInfo.fromDict(battleResults)
            stateChange = self.__rankedController.getRankChangeStatus(rankInfo)
            bonusBattlesString = getBonusBattlesIncome(R.strings.messenger.serviceChannelMessages.battleResults.rankedBonusBattles, rankInfo.stepsBonusBattles, rankInfo.efficiencyBonusBattles, stateChange == RankChangeStates.LEAGUE_EARNED)
        dailyBattles = battleResults.get(u'rankedDailyBattles', 0)
        persistBattles = battleResults.get(u'rankedBonusBattles', 0)
        questsBonusBattlesString = InvoiceReceivedFormatter.getRankedBonusBattlesString(persistBattles, dailyBattles)
        if questsBonusBattlesString:
            questsStrRes = R.strings.messenger.serviceChannelMessages.battleResults.rankedBonusBattles.quests()
            questsBonusBattlesString = backport.text(questsStrRes, bonusBattles=questsBonusBattlesString)
            bonusBattlesString = text_styles.concatStylesToSingleLine(bonusBattlesString, questsBonusBattlesString)
        rankedBonusBattlesBlock = u''
        if bonusBattlesString:
            rankedBonusBattlesBlock = g_settings.htmlTemplates.format(u'battleResultRankedBonusBattles', {u'rankedBonusBattles': bonusBattlesString})
        return rankedBonusBattlesBlock

    def __makeBattlePassProgressionString(self, guiType, battleResults):
        battlePassString = u''
        value = sum((points for points in battleResults.get(u'battlePassPoints', {}).get(u'vehicles', {}).itervalues()))
        value += battleResults.get(u'bpTopPoints', 0)
        if value > 0:
            if guiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
                bonusType = battleResults.get(u'bonusType', 0)
                if self.__battleRoyaleController.isBattlePassAvailable(bonusType):
                    battlePassString = backport.text(R.strings.messenger.serviceChannelMessages.BRbattleResults.battlePass(), pointsDiff=text_styles.neutral(value))
            else:
                battlePassString = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.battlePass(), pointsDiff=text_styles.neutral(value))
        return u'' if not battlePassString else g_settings.htmlTemplates.format(u'battlePass', ctx={u'battlePassProgression': battlePassString})

    def __makePiggyBankString(self, credits_):
        return u'' if not credits_ else g_settings.htmlTemplates.format(u'piggyBank', ctx={u'credits': self.__makeCurrencyString(Currency.CREDITS, credits_)})

    def __makeBRCoinString(self, battleResults):
        value = battleResults.get(u'brcoin', 0)
        if value:
            text = backport.text(R.strings.messenger.serviceChannelMessages.BRbattleResults.battleRoyaleBrCoin(), value=text_styles.neutral(value))
            return g_settings.htmlTemplates.format(u'battleResultBrcoin', ctx={u'brcoin': text})


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
    __currencyTemplates = {Currency.CREDITS: u'PurchaseForCreditsSysMessage',
     Currency.GOLD: u'PurchaseForGoldSysMessage',
     Currency.CRYSTAL: u'PurchaseForCrystalSysMessage',
     Currency.EVENT_COIN: u'PurchaseForEventCoinSysMessage',
     Currency.BPCOIN: u'PurchaseForBpcoinSysMessage'}

    def isNotify(self):
        return True

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            vehicleCompDescr = message.data.get(u'vehTypeCD', None)
            styleId = message.data.get(u'styleID', None)
            result = message.data.get(u'result', None)
            typeID = message.data.get(u'typeID', None)
            cost = Money(*message.data.get(u'cost', ()))
            if vehicleCompDescr is not None and result is not None and typeID is not None:
                vehicle = self.itemsCache.items.getItemByCD(vehicleCompDescr)
                if typeID == AUTO_MAINTENANCE_TYPE.REPAIR:
                    formatMsgType = u'RepairSysMessage'
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
                        data = {u'savedData': {u'styleIntCD': style.compactDescr,
                                        u'vehicleIntCD': vehicleCompDescr,
                                        u'toStyle': True}}
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
                        _logger.warning(u'Invalid typeID field in message: %s', message)
                        callback([MessageData(None, None)])
                    else:
                        msg = msgTmpl % msgArgs
                else:
                    msg = u''
                priorityLevel = NotificationPriorityLevel.MEDIUM
                if result == AUTO_MAINTENANCE_RESULT.OK:
                    priorityLevel = NotificationPriorityLevel.LOW
                    templateName = formatMsgType
                elif result == AUTO_MAINTENANCE_RESULT.NOT_ENOUGH_ASSETS:
                    templateName = u'ErrorSysMessage'
                elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_OVER:
                    templateName = u'RentOfStyleIsExpiredSysMessage'
                elif result == AUTO_MAINTENANCE_RESULT.RENT_IS_ALMOST_OVER:
                    if vehicle.isAutoRentStyle:
                        templateName = u'RentOfStyleIsAlmostExpiredAutoprolongationONSysMessage'
                    else:
                        templateName = u'RentOfStyleIsAlmostExpiredAutoprolongationOFFSysMessage'
                elif result == AUTO_MAINTENANCE_RESULT.DISABLED_OPTION:
                    templateName = u'ErrorSysMessage'
                else:
                    templateName = u'WarningSysMessage'
                if result == AUTO_MAINTENANCE_RESULT.OK:
                    msg += shared_fmts.formatPrice(cost.toAbs(), ignoreZeros=True) + u'.'
                formatted = g_settings.msgTemplates.format(templateName, {u'text': msg}, data=data)
                settings = self._getGuiSettings(message, priorityLevel=priorityLevel, messageType=message.type, messageSubtype=result)
                callback([MessageData(formatted, settings)])
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return

    def _getTemplateByCurrency(self, currency):
        return self.__currencyTemplates.get(currency, u'PurchaseForCreditsSysMessage')


class AchievementFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def isAsync(self):
        return True

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        achievesList, badgesList = [], []
        achieves = message.data.get(u'popUpRecords')
        if achieves is not None:
            for (block, name), value in achieves.iteritems():
                if block == BADGES_BLOCK:
                    badgesList.append(backport.text(R.strings.badge.dyn(u'badge_{}'.format(name))()))
                achieve = getAchievementFactory((block, name)).create(value)
                if achieve is not None:
                    achievesList.append(achieve.getUserName())
                achievesList.append(backport.text(R.strings.achievements.dyn(name)()))

        rares = [ rareID for rareID in message.data.get(u'rareAchievements', []) if rareID > 0 ]
        raresList = _processRareAchievements(rares)
        achievesList.extend(raresList)
        if not achievesList:
            callback([MessageData(None, None)])
            return
        else:
            formatted = g_settings.msgTemplates.format(u'achievementReceived', {u'achieves': u', '.join(achievesList)})
            if badgesList:
                badgesBlock = g_settings.htmlTemplates.format(u'badgeAchievement', {u'badges': u', '.join(badgesList)})
                formatted = EOL.join([formatted, badgesBlock])
            callback([MessageData(formatted, self._getGuiSettings(message, u'achievementReceived'))])
            return


class CurrencyUpdateFormatter(ServiceChannelFormatter):
    _EMITTER_ID_TO_TITLE = {2525: R.strings.messenger.serviceChannelMessages.currencyUpdate.integratedAuction(),
     2524: R.strings.messenger.serviceChannelMessages.currencyUpdate.battlepass()}
    _DEFAULT_TITLE = R.strings.messenger.serviceChannelMessages.currencyUpdate.financial_transaction()
    __FREE_XP_ICON = u'freeXPSmallIcon'
    __CURRENCY_ICONS = {CURRENCIES_CONSTANTS.FREE_XP: __FREE_XP_ICON}
    _CURRENCY_TO_STYLE = {CURRENCIES_CONSTANTS.FREE_XP: text_styles.expText}

    def format(self, message, *args):
        data = message.data
        currencyCode = data[u'currency_name']
        amountDelta = data[u'amount_delta']
        transactionTime = data[u'date']
        emitterID = data.get(u'emitterID')
        if currencyCode and amountDelta and transactionTime:
            xmlKey = u'currencyUpdate'
            formatted = g_settings.msgTemplates.format(xmlKey, ctx={u'title': backport.text(self._EMITTER_ID_TO_TITLE.get(emitterID, self._DEFAULT_TITLE)),
             u'date': TimeFormatter.getLongDatetimeFormat(transactionTime),
             u'currency': self.__getCurrencyString(currencyCode, amountDelta),
             u'amount': self.__getCurrencyStyle(currencyCode)(getBWFormatter(currencyCode)(abs(amountDelta)))}, data={u'icon': self.__CURRENCY_ICONS.get(currencyCode, currencyCode.title() + u'Icon')})
            return [MessageData(formatted, self._getGuiSettings(message, xmlKey))]
        else:
            return [MessageData(None, None)]

    def __ifPlatformCurrency(self, currencyCode):
        return currencyCode not in Currency.ALL + (CURRENCIES_CONSTANTS.FREE_XP,)

    def __getCurrencyString(self, currencyCode, amountDelta):
        return backport.text(R.strings.messenger.platformCurrencyMsg.dyn(u'debited' if amountDelta < 0 else u'received').dyn(currencyCode)()) if self.__ifPlatformCurrency(currencyCode) else backport.text(R.strings.messenger.serviceChannelMessages.currencyUpdate.dyn(u'debited' if amountDelta < 0 else u'received').dyn(currencyCode)())

    def __getCurrencyStyle(self, currencyCode):
        return self._CURRENCY_TO_STYLE.get(currencyCode, getStyle(currencyCode))


class GiftReceivedFormatter(ServiceChannelFormatter):
    __handlers = {u'money': (u'_GiftReceivedFormatter__formatMoneyGiftMsg', {1: u'creditsReceivedAsGift',
                 2: u'goldReceivedAsGift',
                 3: u'creditsAndGoldReceivedAsGift',
                 8: u'eventCoinReceivedAsGift'}),
     u'xp': (u'_GiftReceivedFormatter__formatXPGiftMsg', u'xpReceivedAsGift'),
     u'premium': (u'_GiftReceivedFormatter__formatPremiumGiftMsg', u'premiumReceivedAsGift'),
     u'premium_plus': (u'_GiftReceivedFormatter__formatPremiumGiftMsg', u'tankPremiumReceivedAsGift'),
     u'item': (u'_GiftReceivedFormatter__formatItemGiftMsg', u'itemReceivedAsGift'),
     u'vehicle': (u'_GiftReceivedFormatter__formatVehicleGiftMsg', u'vehicleReceivedAsGift')}

    def format(self, message, *args):
        data = message.data
        giftType = data.get(u'type')
        if giftType is not None:
            handlerName, templateKey = self.__handlers.get(giftType, (None, None))
            if handlerName is not None:
                formatted, templateKey = getattr(self, handlerName)(templateKey, data)
                return [MessageData(formatted, self._getGuiSettings(message, templateKey))]
        return [MessageData(None, None)]

    def __formatMoneyGiftMsg(self, keys, data):
        result = (None, u'')
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
        xp = data.get(u'amount', 0)
        result = None
        if xp > 0:
            result = g_settings.msgTemplates.format(key, ctx={u'freeXP': backport.getIntegralFormat(xp)})
        return (result, key)

    def __formatPremiumGiftMsg(self, key, data):
        days = data.get(u'amount', 0)
        result = None
        if days > 0:
            result = g_settings.msgTemplates.format(key, ctx={u'days': days})
        return (result, key)

    def __formatItemGiftMsg(self, key, data):
        amount = data.get(u'amount', 0)
        result = None
        itemTypeIdx = data.get(u'itemTypeIdx')
        itemCompactDesc = data.get(u'itemCD')
        if amount > 0 and itemTypeIdx is not None and itemCompactDesc is not None:
            result = g_settings.msgTemplates.format(key, ctx={u'typeName': getTypeInfoByIndex(itemTypeIdx)[u'userString'],
             u'itemName': vehicles_core.getItemByCompactDescr(itemCompactDesc).i18n.userString,
             u'amount': amount})
        return (result, key)

    def __formatVehicleGiftMsg(self, key, data):
        vCompDesc = data.get(u'typeCD', None)
        result = None
        if vCompDesc is not None:
            result = g_settings.msgTemplates.format(key, ctx={u'vehicleName': getUserName(vehicles_core.getVehicleType(vCompDesc))})
        return (result, key)


class InvoiceReceivedFormatter(WaitItemsSyncFormatter):
    __purchaseCache = dependency.descriptor(IPurchaseCache)
    __emitterAssetHandlers = {constants.INVOICE_EMITTER.WOTRP_CASHBACK: {INVOICE_ASSET.GOLD: u'_formatWOTRPCashbackGold',
                                                INVOICE_ASSET.DATA: u'_formatWOTRPCashbackData'}}
    __assetHandlers = {INVOICE_ASSET.GOLD: u'_formatAmount',
     INVOICE_ASSET.CREDITS: u'_formatAmount',
     INVOICE_ASSET.CRYSTAL: u'_formatAmount',
     INVOICE_ASSET.EVENT_COIN: u'_formatAmount',
     INVOICE_ASSET.BPCOIN: u'_formatAmount',
     INVOICE_ASSET.PREMIUM: u'_formatAmount',
     INVOICE_ASSET.FREE_XP: u'_formatAmount',
     INVOICE_ASSET.DATA: u'_formatData',
     INVOICE_ASSET.PURCHASE: u'_formatPurchase'}
    __currencyToInvoiceAsset = {Currency.GOLD: INVOICE_ASSET.GOLD,
     Currency.CREDITS: INVOICE_ASSET.CREDITS,
     Currency.CRYSTAL: INVOICE_ASSET.CRYSTAL,
     Currency.EVENT_COIN: INVOICE_ASSET.EVENT_COIN,
     Currency.BPCOIN: INVOICE_ASSET.BPCOIN,
     Currency.EQUIP_COIN: INVOICE_ASSET.EQUIP_COIN}
    __operationTemplateKeys = {INVOICE_ASSET.GOLD: u'goldAccruedInvoiceReceived',
     INVOICE_ASSET.CREDITS: u'creditsAccruedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: u'crystalAccruedInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN: u'eventCoinAccruedInvoiceReceived',
     INVOICE_ASSET.BPCOIN: u'bpcoinAccruedInvoiceReceived',
     INVOICE_ASSET.PREMIUM: u'premiumAccruedInvoiceReceived',
     INVOICE_ASSET.FREE_XP: u'freeXpAccruedInvoiceReceived',
     INVOICE_ASSET.EQUIP_COIN: u'equipCoinAccruedInvoiceReceived',
     INVOICE_ASSET.GOLD | 16: u'goldDebitedInvoiceReceived',
     INVOICE_ASSET.CREDITS | 16: u'creditsDebitedInvoiceReceived',
     INVOICE_ASSET.CRYSTAL | 16: u'crystalDebitedInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN | 16: u'eventCoinDebitedInvoiceReceived',
     INVOICE_ASSET.BPCOIN | 16: u'bpcoinDebitedInvoiceReceived',
     INVOICE_ASSET.PREMIUM | 16: u'premiumDebitedInvoiceReceived',
     INVOICE_ASSET.FREE_XP | 16: u'freeXpDebitedInvoiceReceived',
     INVOICE_ASSET.EQUIP_COIN | 16: u'equipCoinDebitedInvoiceReceived'}
    __blueprintsTemplateKeys = {BlueprintTypes.VEHICLE: (u'vehicleBlueprintsAccruedInvoiceReceived', u'vehicleBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.NATIONAL: (u'nationalBlueprintsAccruedInvoiceReceived', u'nationalBlueprintsDebitedInvoiceReceived'),
     BlueprintTypes.INTELLIGENCE_DATA: (u'intelligenceBlueprintsAccruedInvoiceReceived', u'intelligenceBlueprintsDebitedInvoiceReceived')}
    __emitterMessageTemplateKeys = {constants.INVOICE_EMITTER.WOTRP_CASHBACK: {INVOICE_ASSET.GOLD: u'WOTRPCachbackInvoiceReceived',
                                                INVOICE_ASSET.DATA: u'WOTRPCachbackInvoiceReceived'}}
    __messageTemplateKeys = {INVOICE_ASSET.GOLD: u'goldInvoiceReceived',
     INVOICE_ASSET.CREDITS: u'creditsInvoiceReceived',
     INVOICE_ASSET.CRYSTAL: u'crystalInvoiceReceived',
     INVOICE_ASSET.EVENT_COIN: u'eventCoinInvoiceReceived',
     INVOICE_ASSET.BPCOIN: u'bpcoinInvoiceReceived',
     INVOICE_ASSET.PREMIUM: u'premiumInvoiceReceived',
     INVOICE_ASSET.FREE_XP: u'freeXpInvoiceReceived',
     INVOICE_ASSET.DATA: u'dataInvoiceReceived',
     INVOICE_ASSET.PURCHASE: u'purchaseInvoiceReceived'}
    __INVALID_TYPE_ASSET = -1
    __auxMessagesHandlers = {INVOICE_ASSET.DATA: u'getInvoiceDataAuxMessages',
     INVOICE_ASSET.PURCHASE: u'getPurchaseDataAuxMessages'}
    __DESTROY_PAIR_MODIFICATIONS_MSG_TEMPLATE = u'DestroyAllPairsModifications'
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    @adisp_async
    @adisp_process
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
                emitterID = data.get(u'emitterID')
                assetType = data.get(u'assetType', self.__INVALID_TYPE_ASSET)
                handler = self._getMessageHandler(emitterID, assetType)
                if handler is not None:
                    formatted = getattr(self, handler)(emitterID, assetType, data)
                if formatted is not None:
                    settings = self._getGuiSettings(message, self._getMessageTemplateKey(emitterID, assetType))
            else:
                assetType = self.__INVALID_TYPE_ASSET
                _logger.debug(u'Message will not be shown!')
            mainMassage = MessageData(formatted, settings)
            auxMessagesHandler = self.__auxMessagesHandlers.get(assetType, None)
            if auxMessagesHandler is not None:
                auxMassages = getattr(self, auxMessagesHandler)(data)
        result = [mainMassage]
        result.extend(auxMassages)
        callback(result)
        return

    def _getMessageHandler(self, emitterId, assetType):
        return self.__emitterAssetHandlers.get(emitterId, {}).get(assetType, None) or self.__assetHandlers.get(assetType)

    @classmethod
    def getBlueprintString(cls, blueprints):
        vehicleFragments, nationFragments, universalFragments = getUniqueBlueprints(blueprints)
        blueprintsString = []
        for fragmentCD, count in vehicleFragments.iteritems():
            ctx = cls.__getBlueprintContext(count)
            vehicleName = cls.__getVehicleName(fragmentCD)
            ctx[u'vehicleName'] = vehicleName
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.VEHICLE, count, ctx))

        for nationID, count in nationFragments.iteritems():
            ctx = cls.__getBlueprintContext(count)
            localizedNationName = backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase())
            ctx[u'nationName'] = localizedNationName
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.NATIONAL, count, ctx))

        if universalFragments:
            blueprintsString.append(cls.__formatBlueprintsString(BlueprintTypes.INTELLIGENCE_DATA, universalFragments, cls.__getBlueprintContext(universalFragments)))
        return u'<br>'.join(blueprintsString)

    @classmethod
    def getVehiclesString(cls, vehicles, htmlTplPostfix=u'InvoiceReceived'):
        addVehNames, removeVehNames, rentedVehNames = cls._getVehicleNames(vehicles)
        result = []
        if addVehNames:
            result.append(g_settings.htmlTemplates.format(u'vehiclesAccrued' + htmlTplPostfix, ctx={u'vehicles': u', '.join(addVehNames)}))
        if removeVehNames:
            result.append(g_settings.htmlTemplates.format(u'vehiclesDebited' + htmlTplPostfix, ctx={u'vehicles': u', '.join(removeVehNames)}))
        if rentedVehNames:
            result.append(g_settings.htmlTemplates.format(u'vehiclesRented' + htmlTplPostfix, ctx={u'vehicles': u', '.join(rentedVehNames)}))
        return u'<br/>'.join(result)

    def canBeEmpty(self):
        return True

    @classmethod
    def _getCustomizationCompensationString(cls, compensationMoney, strItemType, strItemName, amount, htmlTplPostfix):
        htmlTemplates = g_settings.htmlTemplates
        values = []
        result = u''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            key = u'{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={u'amount': applyAll(currency, compensationMoney.get(currency))}))

        if values:
            result = htmlTemplates.format(u'customizationCompensation' + htmlTplPostfix, ctx={u'type': strItemType,
             u'name': strItemName,
             u'amount': str(amount),
             u'compensation': u', '.join(values)})
        return result

    @classmethod
    def getVehiclesCompensationString(cls, vehicles, htmlTplPostfix=u'InvoiceReceived'):
        htmlTemplates = g_settings.htmlTemplates
        result = []
        for vehicleDict in vehicles:
            for vehCompDescr, vehData in vehicleDict.iteritems():
                vehicleName = cls.__getVehicleName(vehCompDescr)
                if vehicleName is None:
                    continue
                if u'rentCompensation' in vehData:
                    comp = Money.makeFromMoneyTuple(vehData[u'rentCompensation'])
                    currency = comp.getCurrency(byWeight=True)
                    formatter = getBWFormatter(currency)
                    key = u'{}RentCompensationReceived'.format(currency)
                    ctx = {currency: formatter(comp.get(currency)),
                     u'vehicleName': vehicleName}
                    result.append(htmlTemplates.format(key, ctx=ctx))
                if u'customCompensation' in vehData:
                    itemNames = (vehicleName,)
                    comp = Money.makeFromMoneyTuple(vehData[u'customCompensation'])
                    result.append(cls._getCompensationString(comp, itemNames, htmlTplPostfix))

        return u'<br/>'.join(result) if any(result) else u''

    @classmethod
    def getCustomizationCompensationString(cls, customizationItem, htmlTplPostfix=u'InvoiceReceived'):
        result = u''
        if u'customCompensation' not in customizationItem:
            return result
        customItemData = getCustomizationItemData(customizationItem[u'id'], customizationItem[u'custType'])
        strItemType = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.compensation.dyn(customItemData.guiItemType)())
        comp = Money.makeFromMoneyTuple(customizationItem[u'customCompensation'])
        result = cls._getCustomizationCompensationString(comp, strItemType, customItemData.userName, customizationItem[u'compensatedNumber'], htmlTplPostfix)
        return result

    @classmethod
    def getTankmenString(cls, tmen, dismiss=False):
        tmanUserStrings = []
        for tmanData in tmen:
            try:
                if isinstance(tmanData, dict):
                    tankman = Tankman(tmanData[u'tmanCompDescr'])
                elif isinstance(tmanData, Tankman):
                    tankman = tmanData
                else:
                    tankman = Tankman(tmanData)
                tmanUserStrings.append(u'{0:s} {1:s} ({2:s}, {3:s}, {4:d}%)'.format(tankman.rankUserName, tankman.lastUserName, tankman.roleUserName, getUserName(tankman.vehicleNativeDescr.type), tankman.roleLevel))
            except Exception:
                _logger.error(u'Wrong tankman data: %s', tmanData)
                _logger.exception(u'getTankmenString catch exception')

        result = u''
        if dismiss:
            invoiceStr = u'tankmenInvoiceDismiss'
            tankmanStr = u'tankmenToRemove'
        else:
            invoiceStr = u'tankmenInvoiceReceived'
            tankmanStr = u'tankman'
        if tmanUserStrings:
            result = g_settings.htmlTemplates.format(invoiceStr, ctx={tankmanStr: u', '.join(tmanUserStrings)})
        return result

    @classmethod
    def getGoodiesString(cls, goodies, exclude=None):
        result = []
        boostersStrings = []
        discountsStrings = []
        equipStrings = []
        for goodieID, ginfo in goodies.iteritems():
            if exclude is not None and goodieID in exclude:
                continue
            if goodieID in cls._itemsCache.items.shop.boosters:
                booster = cls.__goodiesCache.getBooster(goodieID)
                if booster is not None and booster.enabled:
                    if ginfo.get(u'count'):
                        boostersStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=booster.userName, count=ginfo.get(u'count')))
                    else:
                        boostersStrings.append(booster.userName)
            if goodieID in cls._itemsCache.items.shop.discounts:
                discount = cls.__goodiesCache.getDiscount(goodieID)
                if discount is not None and discount.enabled:
                    discountsStrings.append(discount.description)
            if goodieID in cls._itemsCache.items.shop.demountKits:
                dk = cls.__goodiesCache.getDemountKit(goodieID)
                if dk and dk.enabled:
                    if ginfo.get(u'count'):
                        equipStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=dk.userName, count=ginfo.get(u'count')))
                    else:
                        equipStrings.append(dk.userName)
            if goodieID in cls._itemsCache.items.shop.recertificationForms:
                rf = cls.__goodiesCache.getRecertificationForm(goodieID)
                if rf and rf.enabled:
                    if ginfo.get(u'count'):
                        equipStrings.append(backport.text(R.strings.system_messages.bonuses.booster.value(), name=rf.userName, count=ginfo.get(u'count')))
                    else:
                        equipStrings.append(rf.userName)

        if boostersStrings:
            result.append(g_settings.htmlTemplates.format(u'boostersInvoiceReceived', ctx={u'boosters': u', '.join(boostersStrings)}))
        if discountsStrings:
            result.append(g_settings.htmlTemplates.format(u'discountsInvoiceReceived', ctx={u'discounts': u', '.join(discountsStrings)}))
        if equipStrings:
            result.append(g_settings.htmlTemplates.format(u'equipmentInvoiceReceived', ctx={u'equipment': u', '.join(equipStrings)}))
        return u'; '.join(result)

    @classmethod
    def getEnhancementsString(cls, enhancements):
        added = 0
        removed = 0
        result = []
        for extra in enhancements.itervalues():
            count = extra.get(u'count', 0)
            if count > 0:
                added += count
            removed += -count

        if added:
            result.append(g_settings.htmlTemplates.format(u'enhancementsAccruedInvoiceReceived', ctx={u'count': added}))
        if removed:
            result.append(g_settings.htmlTemplates.format(u'enhancementsDebitedInvoiceReceived', ctx={u'count': removed}))
        return None if not result else u'; '.join(result)

    @staticmethod
    def getEntitlementsString(entitlements):
        result = [ EntitlementBonus.getUserNameWithCount(entitlementID, count) for entitlementID, count in entitlements ]
        return u', '.join(filter(None, result))

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
        return u', '.join(result)

    def getInvoiceDataAuxMessages(self, data):
        result = []
        result.extend(self.__getDiscardPairModificationsMsg(data))
        return result

    def getPurchaseDataAuxMessages(self, data):
        result = []
        result.extend(self.__getReferralProgramMsg(data))
        return result

    def _composeOperations(self, data):
        dataEx = data.get(u'data', {})
        if not dataEx:
            return
        else:
            operations = []
            self._processCompensations(dataEx)
            for currency, invAsset in self.__currencyToInvoiceAsset.iteritems():
                if currency in dataEx:
                    operations.append(self.__getFinOperationString(invAsset, dataEx[currency], formatter=getBWFormatter(currency)))

            freeXp = dataEx.get(u'freeXP')
            if freeXp is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.FREE_XP, freeXp))
            premium = dataEx.get(PREMIUM_ENTITLEMENTS.BASIC)
            if premium is not None:
                operations.append(self.__getFinOperationString(INVOICE_ASSET.PREMIUM, premium))
            tankPremium = dataEx.get(PREMIUM_ENTITLEMENTS.PLUS)
            if tankPremium is not None:
                operations.append(self.__getTankPremiumString(tankPremium))
            items = dataEx.get(u'items', {})
            if items:
                operations.append(self.__getItemsString(items))
            tmen = dataEx.get(u'tankmen', [])
            tmenToRemove = dataEx.get(u'tmenToRemove', [])
            vehicles = dataEx.get(u'vehicles', {})
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
                        tmen.extend(v.get(u'tankmen', []))
                        items = v.get(u'items', {})
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
                tmen = [ tankmanCache[tankman] for tankman in tmenToRemove.get(u'ids', []) ]
                operations.append(self.getTankmenString(tmen, True))
            blueprints = dataEx.get(u'blueprints')
            if blueprints:
                operations.append(self.getBlueprintString(blueprints))
            slots = dataEx.get(u'slots')
            if slots:
                operations.append(self.__getSlotsString(slots))
            berths = dataEx.get(u'berths')
            if berths:
                operations.append(self.__getBerthsString(berths))
            goodies = dataEx.get(u'goodies', {})
            if goodies:
                strGoodies = self.getGoodiesString(goodies)
                if strGoodies:
                    operations.append(strGoodies)
            enhancements = dataEx.get(u'enhancements', {})
            if enhancements:
                operations.append(self.getEnhancementsString(enhancements))
            dossier = dataEx.get(u'dossier', {})
            if dossier:
                operations.append(self.__getDossierString())
            _extendCustomizationData(dataEx, operations, htmlTplPostfix=u'InvoiceReceived')
            _extendCrewSkinsData(dataEx, operations)
            tankmenFreeXP = dataEx.get(u'tankmenFreeXP', {})
            if tankmenFreeXP:
                operations.append(self.__getTankmenFreeXPString(tankmenFreeXP))
            tokensStr = self.__getTokensString(dataEx.get(u'tokens', {}))
            if tokensStr:
                operations.extend(tokensStr)
            entitlementsStr = self.__getEntitlementsString(dataEx.get(u'entitlements', {}))
            if entitlementsStr:
                operations.append(entitlementsStr)
            lootBoxStr = self.__getLootBoxString(dataEx.get(u'tokens', {}), data.get(u'assetType', self.__INVALID_TYPE_ASSET))
            if lootBoxStr:
                operations.append(lootBoxStr)
            rankedDailyBattles = dataEx.get(u'rankedDailyBattles', 0)
            rankedPersistentBattles = dataEx.get(u'rankedBonusBattles', 0)
            rankedBonusBattlesStr = self.__getRankedBonusBattlesString(rankedPersistentBattles, rankedDailyBattles)
            if rankedBonusBattlesStr:
                operations.append(rankedBonusBattlesStr)
            platformCurrenciesStr = self.__getPlatformCurrenciesString(dataEx.get(u'currencies', {}))
            if platformCurrenciesStr:
                operations.append(platformCurrenciesStr)
            return operations

    def _formatData(self, emitterID, assetType, data):
        operations = self._composeOperations(data)
        icon = u'InformationIcon'
        return None if not operations else g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx={u'at': self._getOperationTimeString(data),
         u'desc': self.__getL10nDescription(data),
         u'op': u'<br/>'.join(operations)}, data={u'icon': icon})

    def _formatAmount(self, emitterID, assetType, data):
        amount = data.get(u'amount', None)
        return None if amount is None else g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx={u'at': self._getOperationTimeString(data),
         u'desc': self.__getL10nDescription(data),
         u'op': self.__getFinOperationString(assetType, amount)})

    def _formatPurchase(self, emitterID, assetType, data):
        if u'customFormatting' in data.get(u'tags', ()):
            return None
        else:
            operations = self._composeOperations(data)
            if not operations:
                return None
            ctx = {u'at': self._getOperationTimeString(data),
             u'desc': self.__getL10nDescription(data),
             u'op': u'<br/>'.join(operations)}
            templateData = {}
            metadata = data.get(u'meta')
            title = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.invoice())
            subtitle = u''
            if metadata:
                purchase = self.__purchaseCache.getCachedPurchase(self.__purchaseCache.getProductCode(metadata))
                titleID = purchase.getTitleID()
                if titleID:
                    title = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.purchase.title.dyn(titleID)())
                else:
                    _logger.info(u'Could not find title in the purchase descriptor!')
                purchaseName = purchase.getProductName()
                if purchaseName:
                    subtitle = g_settings.htmlTemplates.format(u'purchaseSubtitle', {u'text': purchaseName})
                else:
                    _logger.info(u'Could not find name in the purchase descriptor!')
                iconID = purchase.getIconID()
                if iconID:
                    templateData[u'icon'] = iconID
                else:
                    _logger.info(u'Could not find icon in the purchase descriptor!')
            ctx[u'title'] = title
            ctx[u'subtitle'] = subtitle
            return g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx=ctx, data=templateData)

    def _formatWOTRPCashbackGold(self, emitterID, assetType, data):
        ctx = {u'amount': data.get(u'amount', 0)}
        return g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx=ctx)

    def _formatWOTRPCashbackData(self, emitterID, assetType, data):
        gold = data.get(u'data', {}).get(u'gold', 0)
        if gold == 0:
            return self._formatData(emitterID, assetType, data)
        ctx = {u'amount': gold}
        return g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx=ctx)

    def _getMessageTemplateKey(self, emitterID, assetType):
        return self.__emitterMessageTemplateKeys.get(emitterID, {}).get(assetType) or self.__messageTemplateKeys[assetType]

    @classmethod
    def _getOperationTimeString(cls, data):
        operationTime = data.get(u'at', None)
        if operationTime:
            fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
        else:
            fDatetime = u'N/A'
        return fDatetime

    @classmethod
    def _getVehicleNames(cls, vehicles):
        addVehNames = []
        removeVehNames = []
        rentedVehNames = []
        for vehicleDict in vehicles:
            for vehCompDescr, vehData in vehicleDict.iteritems():
                if u'customCompensation' in vehData:
                    continue
                isNegative = False
                if isinstance(vehCompDescr, types.IntType):
                    isNegative = vehCompDescr < 0
                isRented = u'rent' in vehData
                vehicleName = cls.__getVehicleName(vehCompDescr)
                if vehicleName is None:
                    continue
                vehicleInfo = cls.__getVehicleInfo(vehData, isNegative)
                vehicleInfoString = u' ({0:s})'.format(vehicleInfo) if vehicleInfo else u''
                vehUserString = u'{0:s}{1:s}'.format(vehicleName, vehicleInfoString)
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
        result = u''
        currencies = compensationMoney.getSetCurrencies(byWeight=True)
        for currency in currencies:
            key = u'{}Compensation'.format(currency)
            values.append(htmlTemplates.format(key + htmlTplPostfix, ctx={u'amount': applyAll(currency, compensationMoney.get(currency))}))

        if values:
            result = htmlTemplates.format(u'compensationFor' + htmlTplPostfix, ctx={u'items': u', '.join(strItemNames),
             u'compensation': u', '.join(values)})
        return result

    @classmethod
    def _processCompensations(cls, data):

        def __compensationCalc(calc, vehicleDictionary):
            for value in vehicleDictionary.itervalues():
                if u'rentCompensation' in value:
                    calc += Money.makeFromMoneyTuple(value[u'rentCompensation'])
                if u'customCompensation' in value:
                    calc += Money.makeFromMoneyTuple(value[u'customCompensation'])

        vehicles = data.get(u'vehicles')
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
        return {u'amount': backport.getIntegralFormat(abs(count))}

    @classmethod
    def __formatBlueprintsString(cls, fragmentType, count, ctx):
        if count > 0:
            template = cls.__blueprintsTemplateKeys[fragmentType][0]
        else:
            template = cls.__blueprintsTemplateKeys[fragmentType][1]
        return g_settings.htmlTemplates.format(template, ctx)

    def __prerocessRareAchievements(self, data):
        dossiers = data.get(u'data', {}).get(u'dossier', {})
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
                    if name != u'':
                        isRemoving = recData[u'value'] < 0
                        if block == BADGES_BLOCK:
                            if isRemoving:
                                removedBadgesStrings.append(backport.text(R.strings.badge.dyn(u'badge_{}'.format(name))()))
                            else:
                                addBadgesStrings.append(backport.text(R.strings.badge.dyn(u'badge_{}'.format(name))()))
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
                self.__dossierResult.append(g_settings.htmlTemplates.format(u'dossiersAccruedInvoiceReceived', ctx={u'dossiers': u', '.join(addDossierStrings)}))
            delDossiers = [ abs(rare) for rare in rares if rare < 0 ]
            if delDossiers:
                delDossierStrings += _processRareAchievements(delDossiers)
            if delDossierStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format(u'dossiersDebitedInvoiceReceived', ctx={u'dossiers': u', '.join(delDossierStrings)}))
            if addBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format(u'badgeAchievement', ctx={u'badges': u', '.join(addBadgesStrings)}))
            if removedBadgesStrings:
                self.__dossierResult.append(g_settings.htmlTemplates.format(u'removedBadgeAchievement', ctx={u'badges': u', '.join(removedBadgesStrings)}))

    def __getDossierString(self):
        return u'<br/>'.join(self.__dossierResult)

    def __getFinOperationString(self, assetType, amount, formatter=None):
        templateKey = 0 if amount > 0 else 16
        templateKey |= assetType
        ctx = {}
        if formatter is not None:
            ctx[u'amount'] = formatter(abs(amount))
        else:
            ctx[u'amount'] = backport.getIntegralFormat(abs(amount))
        return g_settings.htmlTemplates.format(self.__operationTemplateKeys[templateKey], ctx=ctx)

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
                    itemString = u'{0:s} "{1:s}" - {2:d} {3:s}'.format(getTypeInfoByName(item.itemTypeName)[u'userString'], userString, abs(count), backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.pieces()))
                    if count > 0:
                        accrued.append(itemString)
                    else:
                        debited.append(itemString)
                except Exception:
                    _logger.error(u'itemCompactDescr can not parse: %s ', itemCompactDescr)
                    _logger.exception(u'getItemsString catch exception')

        result = u''
        if accrued:
            if installed:
                templateId = u'itemsInstalledInvoiceReceived'
            else:
                templateId = u'itemsAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={u'items': u', '.join(accrued)})
        if debited:
            if result:
                result += u'<br/>'
            result += g_settings.htmlTemplates.format(u'itemsDebitedInvoiceReceived', ctx={u'items': u', '.join(debited)})
        return result

    @classmethod
    def __getSlotsString(cls, slots):
        if slots > 0:
            template = u'slotsAccruedInvoiceReceived'
        else:
            template = u'slotsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {u'amount': backport.getIntegralFormat(abs(slots))})

    @classmethod
    def __getTankPremiumString(cls, expireTime):
        if expireTime > 0:
            template = u'tankPremiumAccruedInvoiceReceived'
        else:
            template = u'tankPremiumDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {u'amount': backport.getIntegralFormat(abs(expireTime))})

    @classmethod
    def __getBerthsString(cls, berths):
        if berths > 0:
            template = u'berthsAccruedInvoiceReceived'
        else:
            template = u'berthsDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {u'amount': backport.getIntegralFormat(abs(berths))})

    @classmethod
    def __getTankmenFreeXPString(cls, data):
        freeXP = set()
        spec = []
        for tankmenDescr, xp in data.iteritems():
            freeXP.add(xp)
            tankman = Tankman(tankmenDescr)
            spec.append(u'{} {} {}'.format(tankman.fullUserName, tankman.roleUserName, getShortUserName(tankman.vehicleNativeDescr.type)))

        specStr = u' ({})'.format(u', '.join(spec)) if spec else u''
        freeXP = freeXP.pop()
        if freeXP > 0:
            template = u'tankmenFreeXpAccruedInvoiceReceived'
        else:
            template = u'tankmenFreeXpDebitedInvoiceReceived'
        return g_settings.htmlTemplates.format(template, {u'tankmenFreeXp': backport.getIntegralFormat(abs(freeXP)),
         u'spec': specStr})

    @classmethod
    def __getL10nDescription(cls, data):
        descr = u''
        lData = getLocalizedData(data.get(u'data', {}), u'localized_description', defVal=None)
        if lData:
            descr = html.escape(lData.get(u'description', u''))
            if descr:
                descr = u'<br/>' + descr
        return descr

    @classmethod
    def __getVehicleInfo(cls, vehData, isWithdrawn):
        vInfo = []
        if isWithdrawn:
            toBarracks = not vehData.get(u'dismissCrew', False)
            action = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewWithdrawn())
            if toBarracks:
                action = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewDroppedToBarracks())
            vInfo.append(i18n.makeString(action))
        else:
            if u'rent' in vehData:
                rentTypeName, rentLeftCount = cls.__processRentVehicleData(vehData[u'rent'])
                if rentTypeName is not None and rentLeftCount > 0:
                    rentLeftStr = backport.text(R.strings.tooltips.quests.awards.vehicleRent.rentLeft.dyn(rentTypeName)(), count=rentLeftCount)
                    vInfo.append(rentLeftStr)
            crewLevel = VehiclesBonus.getTmanRoleLevel(vehData)
            if crewLevel is not None and crewLevel > DEFAULT_CREW_LVL:
                if u'crewInBarracks' in vehData and vehData[u'crewInBarracks']:
                    crewWithLevelString = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewWithLvlDroppedToBarracks(), crewLevel)
                else:
                    crewWithLevelString = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewOnVehicle(), crewLevel)
                vInfo.append(crewWithLevelString)
            if u'unlockModules' in vehData:
                vInfo.append(backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.unlockedModules()))
        return u'; '.join(vInfo)

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
                if rentTypeValue > 0 and rentType != float(u'inf'):
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
            _logger.error(u'Wrong vehicle compact descriptor: %s', vehCompDescr)
            _logger.exception(u'getVehicleName catch exception')

        return vehicleName

    def __getTokensString(self, data):
        awardListcount = 0
        tokenStrings = []
        for tokenName, tokenData in data.iteritems():
            count = tokenData.get(u'count', 0)
            tankmanTokenResult = _processTankmanToken(tokenName)
            if tankmanTokenResult:
                tokenStrings.append(tankmanTokenResult)
            else:
                offerTokenResult = _processOfferToken(tokenName, count)
                if offerTokenResult:
                    tokenStrings.append(offerTokenResult)
            if tokenName == constants.PERSONAL_MISSION_FREE_TOKEN_NAME:
                awardListcount += count
            quests = self.__eventsCache.getQuestsByTokenRequirement(tokenName)
            for quest in quests:
                text = quest.getNotificationText().format(count=count)
                if text:
                    tokenStrings.append(g_settings.htmlTemplates.format(u'questTokenInvoiceReceived', {u'text': text}))

        if awardListcount != 0:
            template = u'awardListAccruedInvoiceReceived' if awardListcount > 0 else u'awardListDebitedInvoiceReceived'
            tokenStrings.append(g_settings.htmlTemplates.format(template, {u'count': awardListcount}))
        return tokenStrings

    def __getLootBoxString(self, data, assetType):
        boxesList = []
        for tokenName, tokenData in data.iteritems():
            if constants.LOOTBOX_TOKEN_PREFIX in tokenName:
                lootBox = self._itemsCache.items.tokens.getLootBoxByTokenID(tokenName)
                if lootBox is not None and (lootBox.getCategory() not in (REFERRAL_PROGRAM_CATEGORY,) or assetType != INVOICE_ASSET.PURCHASE):
                    boxesList.append(backport.text(R.strings.lootboxes.notification.lootBoxesAutoOpen.counter(), boxName=lootBox.getUserName(), count=tokenData.get(u'count', 0)))

        return g_settings.htmlTemplates.format(u'eventLootBoxesInvoiceReceived', {u'boxes': u', '.join(boxesList)}) if boxesList else u''

    def __getEntitlementsString(self, data):
        accrued = []
        debited = []
        for entitlementID, entitlementData in data.iteritems():
            count = entitlementData.get(u'count', 0)
            accrued.append((entitlementID, max(count, 0)))
            debited.append((entitlementID, max(-count, 0)))

        result = u''
        accruedStr = self.getEntitlementsString(accrued)
        debitedStr = self.getEntitlementsString(debited)
        if accruedStr:
            templateId = u'entitlementsAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={u'entitlements': accruedStr})
        if debitedStr:
            templateId = u'entitlementsDebitedInvoiceReceived'
            debitedFormatted = g_settings.htmlTemplates.format(templateId, ctx={u'entitlements': debitedStr})
            result = text_styles.concatStylesToMultiLine(result, debitedFormatted) if result else debitedFormatted
        return result

    def __getRankedBonusBattlesString(self, persistentBattles, dailyBattles):
        result = u''
        accruedStr = self.getRankedBonusBattlesString(max(persistentBattles, 0), max(dailyBattles, 0))
        debitedStr = self.getRankedBonusBattlesString(max(-persistentBattles, 0), max(-dailyBattles, 0))
        if accruedStr:
            templateId = u'rankedBonusBattlesAccruedInvoiceReceived'
            result = g_settings.htmlTemplates.format(templateId, ctx={u'bonusBattles': accruedStr})
        if debitedStr:
            templateId = u'rankedBonusBattlesDebitedInvoiceReceived'
            debitedFormatted = g_settings.htmlTemplates.format(templateId, ctx={u'bonusBattles': debitedStr})
            result = text_styles.concatStylesToMultiLine(result, debitedFormatted) if result else debitedFormatted
        return result

    def __getPlatformCurrenciesString(self, data):
        msgs = []
        for currencyName, countData in data.iteritems():
            count = countData.get(u'count', 0)
            if count == 0:
                continue
            elif count > 0:
                op = u'received'
            else:
                op = u'debited'
            msg = backport.text(R.strings.messenger.platformCurrencyMsg.dyn(op).dyn(currencyName)())
            msgs.append(g_settings.htmlTemplates.format(u'platformCurrency', {u'msg': msg,
             u'count': backport.getIntegralFormat(abs(count))}))

        return u'<br/>'.join(msgs)

    def __getDiscardPairModificationsMsg(self, data):
        dataEx = data.get(u'data', {})
        result = []
        if not dataEx:
            return result
        else:
            vehicles = dataEx.get(u'vehicles', [])
            if vehicles:
                if isinstance(vehicles, dict):
                    vehicles = [vehicles]
            for vehicleDict in vehicles:
                for vehCompDescr, vehData in vehicleDict.iteritems():
                    isNegative = False
                    if isinstance(vehCompDescr, types.IntType):
                        isNegative = vehCompDescr < 0
                    if u'customCompensation' not in vehData and isNegative and vehData.get(u'destroyPairModifications', False):
                        vehicleName = self.__getVehicleName(vehCompDescr)
                        if vehicleName is not None:
                            rMessage = R.strings.messenger.serviceChannelMessages
                            template = self.__DESTROY_PAIR_MODIFICATIONS_MSG_TEMPLATE
                            formatted = g_settings.msgTemplates.format(template, ctx={u'text': backport.text(rMessage.vehiclePostProgression.discardAllPairsModification.body(), vehicle=vehicleName)})
                            result.append(MessageData(formatted, self._getGuiSettings(formatted, template)))

            return result

    def __getReferralProgramMsg(self, data):
        dataEx = data.get(u'data', {})
        price = data.get(u'meta', {}).get(u'price', {})
        referralLootBoxCount = 0
        result = []
        if price.get(u'currency_code') == constants.RP_POINT:
            template = u'ReferralProgramFinanceOperationSysMessage'
            atStr = g_settings.htmlTemplates.format(u'transactionTime', ctx={u'at': self._getOperationTimeString(data)})
            debitedStr = g_settings.htmlTemplates.format(u'rpPointsDebited', ctx={u'points': price.get(u'amount', 0)})
            formatted = g_settings.msgTemplates.format(template, ctx={u'text': u'<br/>'.join((atStr, debitedStr)),
             u'header': backport.text(R.strings.messenger.serviceChannelMessages.referralTransaction.header())})
            result.append(MessageData(formatted, self._getGuiSettings(formatted, template)))
        for tokenName, tokenData in dataEx.get(u'tokens', {}).iteritems():
            if constants.LOOTBOX_TOKEN_PREFIX in tokenName:
                lootBox = self._itemsCache.items.tokens.getLootBoxByTokenID(tokenName)
                if lootBox is not None and lootBox.getCategory() == REFERRAL_PROGRAM_CATEGORY:
                    referralLootBoxCount += tokenData.get(u'count', 0)

        if referralLootBoxCount:
            template = u'rpLootBoxesInvoiceReceived'
            formatted = g_settings.msgTemplates.format(template, ctx={u'count': referralLootBoxCount,
             u'at': self._getOperationTimeString(data)})
            result.append(MessageData(formatted, self._getGuiSettings(formatted, template)))
        return result

    @adisp_async
    @adisp_process
    def __waitForSyncData(self, data, callback):
        yield lambda callback: callback(True)
        assetType = data.get(u'assetType', self.__INVALID_TYPE_ASSET)
        if assetType == INVOICE_ASSET.PURCHASE:
            if self.__purchaseCache.canBeRequestedFromProduct(data):
                purchaseDescrUrl = self.__purchaseCache.getProductCode(data.get(u'meta'))
                pD = yield self.__purchaseCache.requestPurchaseByID(purchaseDescrUrl)
                callback(pD.getDisplayWays().showNotification)
            else:
                _logger.debug(u'Data can not be requested from the product! System message will be shown without product data!')
                callback(True)
        else:
            callback(True)

    def __getMetaUrlData(self, data):
        meta = data.get(u'meta')
        if meta:
            productUrl = meta.get(u'product_id')
            if productUrl:
                return productUrl
            _logger.error(u'Could not find product_code in meta section of invoice!')
        else:
            _logger.error(u'Could not find meta section in purchase invoice!')
        return None


class AdminMessageFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = decompressSysMessage(message.data)
        if data:
            dataType = type(data)
            text = u''
            if dataType in types.StringTypes:
                text = data
            elif dataType is types.DictType:
                text = getLocalizedData({u'value': data}, u'value')
            if not text:
                _logger.error(u'Text of message not found: %s', message)
                return (None, None)
            formatted = g_settings.msgTemplates.format(u'adminMessage', {u'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, u'adminMessage'))]
        else:
            return [MessageData(None, None)]
            return None


class AccountTypeChangedFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        data = message.data
        isPremium = data.get(u'isPremium', None)
        expiryTime = data.get(u'expiryTime', None)
        result = [MessageData(None, None)]
        if isPremium is not None:
            accountTypeName = backport.text(R.strings.menu.accountTypes.base())
            if isPremium:
                accountTypeName = backport.text(R.strings.menu.accountTypes.premium())
            expiryDatetime = TimeFormatter.getLongDatetimeFormat(expiryTime) if expiryTime else None
            if expiryDatetime:
                templateKey = u'accountTypeChangedWithExpiration'
                ctx = {u'accType': accountTypeName,
                 u'expiryTime': expiryDatetime}
            else:
                templateKey = u'accountTypeChanged'
                ctx = {u'accType': accountTypeName}
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
        isPremium = data.get(u'isPremium')
        expiryTime = data.get(u'expiryTime', 0)
        premiumType = data.get(u'premType')
        return [MessageData(self._getMessage(isPremium, premiumType, expiryTime), self._getGuiSettings(message, self._templateKey))] if isPremium is not None and premiumType is not None else [MessageData(None, None)]


class PremiumBoughtFormatter(_PremiumActionFormatter):
    _templateKey = str(SYS_MESSAGE_TYPE.premiumBought)
    _msgTemplateKey = str(SYS_MESSAGE_TYPE.premiumChanged)

    def _getMessage(self, isPremium, premiumType, expiryTime):
        result = None
        if isPremium is True and expiryTime > 0:
            formattedText = backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey], expiryTime=text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime)))
            result = g_settings.msgTemplates.format(self._msgTemplateKey, ctx={u'text': formattedText})
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
            result = g_settings.msgTemplates.format(self._msgTemplateKey, ctx={u'text': backport.text(_PREMIUM_MESSAGES[premiumType][self._templateKey])})
        return result


class PrebattleFormatter(ServiceChannelFormatter):
    __battleTypeByPrebattleType = {PREBATTLE_TYPE.TOURNAMENT: u'tournament',
     PREBATTLE_TYPE.CLAN: u'clan'}
    _battleFinishReasonKeys = {}
    _defaultBattleFinishReasonKey = (u'base', True)

    def isNotify(self):
        return True

    def _getIconId(self, prbType):
        iconId = u'BattleResultIcon'
        if prbType == PREBATTLE_TYPE.CLAN:
            iconId = u'ClanBattleResultIcon'
        elif prbType == PREBATTLE_TYPE.TOURNAMENT:
            iconId = u'TournamentBattleResultIcon'
        return iconId

    def _makeBattleTypeString(self, prbType):
        typeString = self.__battleTypeByPrebattleType.get(prbType, u'prebattle')
        return backport.text(R.strings.messenger.serviceChannelMessages.prebattle.battleType.dyn(typeString)())

    def _makeDescriptionString(self, data, showBattlesCount=True):
        if u'localized_data' in data and data[u'localized_data']:
            description = getPrebattleFullDescription(data, escapeHtml=True)
        else:
            prbType = data.get(u'type')
            description = self._makeBattleTypeString(prbType)
        battlesLimit = data.get(u'battlesLimit', 0)
        if showBattlesCount and battlesLimit > 1:
            battlesCount = data.get(u'battlesCount')
            if battlesCount > 0:
                numberOfBattleString = backport.text(R.strings.messenger.serviceChannelMessages.prebattle.numberOfBattle(), battlesCount)
                description = u'{0:s} {1:s}'.format(description, numberOfBattleString)
            else:
                _logger.warning(u'Invalid value of battlesCount: %s', battlesCount)
        return description

    def _getOpponentsString(self, opponents):
        firstOp = opponents.get(u'1', {}).get(u'name', u'')
        secondOp = opponents.get(u'2', {}).get(u'name', u'')
        result = u''
        if firstOp and secondOp:
            result = g_settings.htmlTemplates.format(u'prebattleOpponents', ctx={u'first': html.escape(firstOp),
             u'second': html.escape(secondOp)})
        return result

    def _getBattleResultString(self, winner, team):
        result = u'undefined'
        if 3 > winner > -1 and team in (1, 2):
            if not winner:
                result = u'draftGame'
            else:
                result = u'defeat' if team != winner else u'win'
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
    _battleFinishReasonKeys = {FINISH_REASON.TECHNICAL: (u'technical', True),
     FINISH_REASON.FAILURE: (u'failure', False),
     FINISH_REASON.UNKNOWN: (u'failure', False)}

    def format(self, message, *args):
        _logger.debug(u'prbArenaFinish %s', message)
        data = message.data
        prbType = data.get(u'type')
        winner = data.get(u'winner')
        team = data.get(u'team')
        wins = data.get(u'wins')
        finishReason = data.get(u'finishReason')
        if None in [prbType,
         winner,
         team,
         wins,
         finishReason]:
            return []
        else:
            battleResult = self._makeBattleResultString(finishReason, winner, team)
            subtotal = u''
            battlesLimit = data.get(u'battlesLimit', 0)
            if battlesLimit > 1:
                battlesCount = data.get(u'battlesCount', -1)
                winsLimit = data.get(u'winsLimit', -1)
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
                    subtotal = g_settings.htmlTemplates.format(u'prebattleTotal', ctx={u'result': sessionResult,
                     u'first': wins[1],
                     u'second': wins[2]})
                else:
                    subtotal = g_settings.htmlTemplates.format(u'prebattleSubtotal', ctx={u'first': wins[1],
                     u'second': wins[2]})
            formatted = g_settings.msgTemplates.format(u'prebattleArenaFinish', ctx={u'desc': self._makeDescriptionString(data),
             u'opponents': self._getOpponentsString(data.get(u'opponents', {})),
             u'result': battleResult,
             u'subtotal': subtotal}, data={u'timestamp': _getTimeStamp(message),
             u'icon': self._getIconId(prbType)})
            return [MessageData(formatted, self._getGuiSettings(message, u'prebattleArenaFinish'))]


class PrebattleKickFormatter(PrebattleFormatter):

    def format(self, message, *args):
        data = message.data
        result = []
        prbType = data.get(u'type')
        kickReason = data.get(u'kickReason')
        if prbType > 0 and kickReason > 0:
            ctx = {}
            resID = R.strings.system_messages.prebattle.kick.type.unknown()
            if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
                resID = R.strings.system_messages.prebattle.kick.type.squad()
            ctx[u'type'] = backport.text(resID)
            kickName = KICK_REASON_NAMES[kickReason]
            resID = R.strings.system_messages.prebattle.kick.reason.dyn(kickName)()
            ctx[u'reason'] = backport.text(resID)
            formatted = g_settings.msgTemplates.format(u'prebattleKick', ctx=ctx)
            result = [MessageData(formatted, self._getGuiSettings(message, u'prebattleKick'))]
        return result


class PrebattleDestructionFormatter(PrebattleFormatter):
    _battleFinishReasonKeys = {KICK_REASON.ARENA_CREATION_FAILURE: (u'failure', False),
     KICK_REASON.AVATAR_CREATION_FAILURE: (u'failure', False),
     KICK_REASON.VEHICLE_CREATION_FAILURE: (u'failure', False),
     KICK_REASON.PREBATTLE_CREATION_FAILURE: (u'failure', False),
     KICK_REASON.BASEAPP_CRASH: (u'failure', False),
     KICK_REASON.CELLAPP_CRASH: (u'failure', False),
     KICK_REASON.UNKNOWN_FAILURE: (u'failure', False),
     KICK_REASON.CREATOR_LEFT: (u'creatorLeft', False),
     KICK_REASON.PLAYERKICK: (u'playerKick', False),
     KICK_REASON.TIMEOUT: (u'timeout', False)}

    def format(self, message, *args):
        _logger.debug(u'prbDestruction %s', message)
        data = message.data
        prbType = data.get(u'type')
        team = data.get(u'team')
        wins = data.get(u'wins')
        kickReason = data.get(u'kickReason')
        if None in [prbType,
         team,
         wins,
         kickReason]:
            return []
        else:
            playerTeamWins = wins[team]
            otherTeamWins = wins[2 if team == 1 else 1]
            winsLimit = data.get(u'winsLimit')
            if winsLimit > 0 and playerTeamWins < winsLimit and otherTeamWins < winsLimit:
                winner = None
            elif playerTeamWins == otherTeamWins:
                winner = 0
            else:
                winner = 1 if wins[1] > wins[2] else 2
            battleResult = self._makeBattleResultString(kickReason, winner, team)
            total = u''
            if data.get(u'battlesLimit', 0) > 1:
                total = u'({0:d}:{1:d})'.format(wins[1], wins[2])
            formatted = g_settings.msgTemplates.format(u'prebattleDestruction', ctx={u'desc': self._makeDescriptionString(data, showBattlesCount=False),
             u'opponents': self._getOpponentsString(data.get(u'opponents', {})),
             u'result': battleResult,
             u'total': total}, data={u'timestamp': _getTimeStamp(message),
             u'icon': self._getIconId(prbType)})
            return [MessageData(formatted, self._getGuiSettings(message, u'prebattleDestruction'))]


class VehCamouflageTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get(u'vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format(u'vehCamouflageTimedOut', ctx={u'vehicleName': getUserName(vType)})
        return [MessageData(formatted, self._getGuiSettings(message, u'vehCamouflageTimedOut'))]


class VehEmblemTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get(u'vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format(u'vehEmblemTimedOut', ctx={u'vehicleName': getUserName(vType)})
        return [MessageData(formatted, self._getGuiSettings(message, u'vehEmblemTimedOut'))]


class VehInscriptionTimedOutFormatter(ServiceChannelFormatter):

    def isNotify(self):
        return True

    def format(self, message, *args):
        data = message.data
        formatted = None
        vehTypeCompDescr = data.get(u'vehTypeCompDescr')
        if vehTypeCompDescr is not None:
            vType = vehicles_core.getVehicleType(vehTypeCompDescr)
            if vType is not None:
                formatted = g_settings.msgTemplates.format(u'vehInscriptionTimedOut', ctx={u'vehicleName': getUserName(vType)})
        return [MessageData(formatted, self._getGuiSettings(message, u'vehInscriptionTimedOut'))]


class ConverterFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __CONVERTER_BLUEPRINTS_TEMPLATE = u'ConverterBlueprintsNotify'

    def __i18nValue(self, key, isReceived, **kwargs):
        key = (u'%sReceived' if isReceived else u'%sWithdrawn') % key
        resID = R.strings.messenger.serviceChannelMessages.sysMsg.converter.dyn(key)()
        return backport.text(resID) % kwargs

    def __vehName(self, vehCompDescr):
        return getUserName(vehicles_core.getVehicleType(abs(vehCompDescr)))

    def format(self, message, *args):
        data = message.data
        text = []
        if data.get(u'inscriptions'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.inscriptions()))
        if data.get(u'emblems'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.emblems()))
        if data.get(u'camouflages'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.camouflages()))
        if data.get(u'customizations'):
            text.append(backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.converter.customizations()))
        vehicles = data.get(u'vehicles')
        if vehicles:
            vehiclesReceived = [ self.__vehName(cd) for cd in vehicles if cd > 0 and self.__itemsCache.items.doesVehicleExist(cd) ]
            if vehiclesReceived:
                text.append(self.__i18nValue(u'vehicles', True, vehicles=u', '.join(vehiclesReceived)))
            vehiclesWithdrawn = [ self.__vehName(cd) for cd in vehicles if cd < 0 and self.__itemsCache.items.doesVehicleExist(abs(cd)) ]
            if vehiclesWithdrawn:
                text.append(self.__i18nValue(u'vehicles', False, vehicles=u', '.join(vehiclesWithdrawn)))
        slots = data.get(u'slots')
        if slots:
            text.append(self.__i18nValue(u'slots', slots > 0, slots=backport.getIntegralFormat(abs(slots))))
        for currency in Currency.ALL:
            value = data.get(currency)
            if value:
                formatter = getBWFormatter(currency)
                kwargs = {currency: formatter(abs(value))}
                text.append(self.__i18nValue(currency, (value > 0), **kwargs))

        freeXP = data.get(u'freeXP')
        if freeXP:
            text.append(self.__i18nValue(u'freeXP', freeXP > 0, freeXP=backport.getIntegralFormat(abs(freeXP))))
        messagesListData = []
        if text:
            formatted = g_settings.msgTemplates.format(u'ConverterNotify', {u'text': u'<br/>'.join(text)})
            messagesListData.append(MessageData(formatted, self._getGuiSettings(message, u'ConverterNotify')))
        if data.get(u'projectionDecalsDemounted'):
            messageKey = R.strings.messenger.serviceChannelMessages.sysMsg.converter.projectionDecalsDemounted()
            messageText = backport.text(messageKey)
            templateName = u'ProjectionDecalsDemountedSysMessage'
            formatted = g_settings.msgTemplates.format(templateName, {u'text': messageText})
            messagesListData.append(MessageData(formatted, self._getGuiSettings(message, u'ProjectionDecalsDemountedSysMessage')))
        blueprints = data.get(u'blueprints')
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
            text.append(g_settings.htmlTemplates.format(u'intelligenceBlueprintReceived', {u'count': backport.getIntegralFormat(universal)}))
        for nation in GUI_NATIONS:
            if national[nation] > 0:
                text.append(g_settings.htmlTemplates.format(u'nationalBlueprintReceived', {u'count': backport.getIntegralFormat(national[nation]),
                 u'nationName': backport.text(R.strings.nations.dyn(nation).genetiveCase())}))

        return g_settings.msgTemplates.format(self.__CONVERTER_BLUEPRINTS_TEMPLATE, {u'text': u'<br/>'.join(text)}) if text else None


class ClientSysMessageFormatter(ServiceChannelFormatter):
    __templateKey = u'%sSysMessage'

    def format(self, data, *args):
        if args:
            msgType, _, messageData, savedData = args[0]
        else:
            msgType = u'Error'
            messageData = None
            savedData = None
        templateKey = self.__templateKey % msgType
        ctx = {u'text': data}
        if messageData:
            ctx.update(messageData)
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx, data={u'savedData': savedData})
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
        lifeTime = g_settings.msgTemplates.lifeTime(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData, groupID=groupID, lifeTime=lifeTime)


class PremiumAccountExpiryFormatter(ClientSysMessageFormatter):

    def format(self, data, *args):
        formatted = g_settings.msgTemplates.format(u'durationOfPremiumAccountExpires', ctx={u'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(data))})
        return [MessageData(formatted, self._getGuiSettings(args, u'durationOfPremiumAccountExpires'))]


class SessionControlFormatter(ServiceChannelFormatter):

    def _doFormat(self, text, key, auxData):
        formatted = g_settings.msgTemplates.format(key, {u'text': text})
        priorityLevel = g_settings.msgTemplates.priority(key)
        return [MessageData(formatted, NotificationGuiSettings(self.isNotify(), priorityLevel=priorityLevel, auxData=auxData))]


class AOGASNotifyFormatter(SessionControlFormatter):

    def format(self, data, *args):
        return self._doFormat(backport.text(R.strings.aogas.dyn(data.name())()), u'AOGASNotify', *args)


class KoreaParentalControlFormatter(SessionControlFormatter):

    def format(self, data, *args):
        return self._doFormat(data, (u'%sSysMessage' % SM_TYPE.Warning), *args)


class VehicleTypeLockExpired(ServiceChannelFormatter):

    def format(self, message, *args):
        result = []
        if message.data:
            ctx = {}
            vehTypeCompDescr = message.data.get(u'vehTypeCompDescr')
            if vehTypeCompDescr is None:
                templateKey = u'vehiclesAllLockExpired'
            else:
                templateKey = u'vehicleLockExpired'
                ctx[u'vehicleName'] = getUserName(vehicles_core.getVehicleType(vehTypeCompDescr))
            formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
            result = [MessageData(formatted, self._getGuiSettings(message, u'vehicleLockExpired'))]
        return result


class ServerDowntimeCompensation(ServiceChannelFormatter):
    __templateKey = u'serverDowntimeCompensation'

    def format(self, message, *args):
        result = []
        subjects = u''
        data = message.data
        if data is not None:
            for key, value in data.items():
                if value:
                    if subjects:
                        subjects += u', '
                    subjects += backport.text(R.strings.messenger.serviceChannelMessages.serverDowntimeCompensation.dyn(key)())

            if subjects:
                formatted = g_settings.msgTemplates.format(self.__templateKey, ctx={u'text': backport.text(R.strings.messenger.serviceChannelMessages.serverDowntimeCompensation.message()) % subjects})
                result = [MessageData(formatted, self._getGuiSettings(message, self.__templateKey))]
        return result


class ActionNotificationFormatter(ClientSysMessageFormatter):
    __templateKey = u'action%s'

    def format(self, message, *args):
        result = []
        data = message.get(u'data')
        if data:
            templateKey = self.__templateKey % message.get(u'state', u'')
            formatted = g_settings.msgTemplates.format(templateKey, ctx={u'text': data}, data={u'icon': message.get(u'type', u'')})
            result = [MessageData(formatted, self._getGuiSettings(args, templateKey))]
        return result


class BootcampResultsFormatter(WaitItemsSyncFormatter):

    def isNotify(self):
        return True

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        _logger.debug(u'message data: %s', message)
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            text = []
            results = message.data
            if results:
                text.append(self.__formatAwards(results))
            else:
                text.append(backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.no_awards()))
            settings = self._getGuiSettings(message, u'bootcampResults')
            formatted = g_settings.msgTemplates.format(u'bootcampResults', {u'text': u'<br/>'.join(text)}, data={u'timestamp': _getTimeStamp(message)})
        callback([MessageData(formatted, settings)])
        return None

    def __formatAwards(self, results):
        awards = backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.awards()) + u'<br/>'
        awards += self.__getAssetString(results, INVOICE_ASSET.GOLD, u'gold')
        awards += self.__getAssetString(results, INVOICE_ASSET.PREMIUM, u'premium')
        awards += self.__getAssetString(results, INVOICE_ASSET.CREDITS, u'credits')
        awards += self.__getAssetString(results, INVOICE_ASSET.FREE_XP, u'freeXP')
        tankPremiumDays = results.get(PREMIUM_ENTITLEMENTS.PLUS, 0)
        if tankPremiumDays:
            awards += u'<br/>' + g_settings.htmlTemplates.format(u'tankPremiumAccruedInvoiceReceived', {u'amount': backport.getIntegralFormat(abs(tankPremiumDays))})

        def sortVehsByLvl(vehCD):
            veh = self._itemsCache.items.getItemByCD(vehCD)
            return veh.level

        vehicles = results.get(u'vehicles', {})
        vehicleCDs = sorted(vehicles.keys(), key=sortVehsByLvl)
        vehiclesNames = []
        devicesAndCrew = u''
        for vehCD in vehicleCDs:
            vehData = vehicles[vehCD]
            vehicle = self._itemsCache.items.getItemByCD(vehCD)
            if vehicle:
                if vehData.get(u'devices', None):
                    devicesAndCrew += self.__formatDevicesAndCrew(vehicle.userName, vehData)
                else:
                    vehiclesNames.append(vehicle.userName)

        awards += u'<br/>'
        if vehiclesNames:
            awards += g_settings.htmlTemplates.format(u'vehiclesAccruedInvoiceReceived', ctx={u'vehicles': u', '.join(vehiclesNames)}) + u'<br/>'
        slots = results.get(u'slots', 0)
        if slots:
            awards += u'<br/>' + g_settings.htmlTemplates.format(u'slotsAccruedInvoiceReceived', {u'amount': backport.getIntegralFormat(abs(slots))})
        if devicesAndCrew:
            awards += devicesAndCrew
        return awards

    @staticmethod
    def __formatDevicesAndCrew(vehName, vehData):
        devices = vehData.get(u'devices', [])
        name = u'<br/><br/><b>' + vehName + u'</b>: <br/>'
        message = u''
        if devices:
            message += name
            message += backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.devices())
            itemsNames = []
            for intCD, count in devices:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                if itemDescr.i18n.userString != u'':
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=itemDescr.i18n.userString, count=backport.getIntegralFormat(count)))

            if itemsNames:
                message += u'<br/>' + u', '.join(itemsNames) + u'<br/>'
        crewInBarracks = vehData.get(u'crewInBarracks', False)
        if crewInBarracks:
            message += backport.text(R.strings.messenger.serviceChannelMessages.bootcamp.crew())
        return message

    @staticmethod
    def __getAssetString(results, assetType, amountType):
        amount = results.get(amountType, 0)
        if amount:
            templateKeys = {INVOICE_ASSET.GOLD: u'goldAccruedInvoiceReceived',
             INVOICE_ASSET.CREDITS: u'creditsAccruedInvoiceReceived',
             INVOICE_ASSET.PREMIUM: u'premiumAccruedInvoiceReceived',
             INVOICE_ASSET.FREE_XP: u'freeXpAccruedInvoiceReceived'}
            return u'<br/>' + g_settings.htmlTemplates.format(templateKeys[assetType], ctx={u'amount': backport.getIntegralFormat(abs(amount))})


class QuestAchievesFormatter(object):
    _SEPARATOR = u'<br/>'
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = cls.getFormattedAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._SEPARATOR.join(result) if result else None

    @classmethod
    def getFormattedAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = []
        tokenResult = cls._processTokens(data)
        if tokenResult and processTokens:
            result.append(tokenResult)
        if not asBattleFormatter:
            crystal = data.get(Currency.CRYSTAL, 0)
            if crystal:
                fomatter = getBWFormatter(Currency.CRYSTAL)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsCrystal', crystal=fomatter(crystal)))
            eventCoin = data.get(Currency.EVENT_COIN, 0)
            if eventCoin:
                fomatter = getBWFormatter(Currency.EVENT_COIN)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsEventCoin', eventCoin=fomatter(eventCoin)))
            equipCoin = data.get(Currency.EQUIP_COIN, 0)
            if equipCoin:
                fomatter = getBWFormatter(Currency.EQUIP_COIN)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsEquipCoin', equipCoin=fomatter(equipCoin)))
            gold = data.get(Currency.GOLD, 0)
            if gold:
                fomatter = getBWFormatter(Currency.GOLD)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsGold', gold=fomatter(gold)))
            bpcoin = data.get(Currency.BPCOIN, 0)
            if bpcoin:
                fomatter = getBWFormatter(Currency.BPCOIN)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsBpcoin', bpcoin=fomatter(bpcoin)))
            platformCurrencies = data.get(u'currencies', {})
            for currency, countDict in platformCurrencies.iteritems():
                result.append(cls.__makeQuestsAchieve(u'platformCurrency', msg=backport.text(R.strings.messenger.platformCurrencyMsg.received.dyn(currency)()), count=backport.getIntegralFormat(countDict.get(u'count', 0))))

        for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
            premium = data.get(premiumType, 0)
            if premium:
                result.append(cls.__makeQuestsAchieve(_PREMIUM_TEMPLATES[premiumType], days=premium))

        if not asBattleFormatter:
            freeXP = data.get(u'freeXP', 0)
            if freeXP:
                result.append(cls.__makeQuestsAchieve(u'battleQuestsFreeXP', freeXP=backport.getIntegralFormat(freeXP)))
        vehiclesList = data.get(u'vehicles', [])
        msg = InvoiceReceivedFormatter.getVehiclesString(vehiclesList, htmlTplPostfix=u'QuestsReceived')
        if msg:
            result.append(msg)
        comptnStr = InvoiceReceivedFormatter.getVehiclesCompensationString(vehiclesList, htmlTplPostfix=u'QuestsReceived')
        if comptnStr:
            result.append(cls._SEPARATOR + comptnStr if result else comptnStr)
        if not asBattleFormatter:
            creditsVal = data.get(Currency.CREDITS, 0)
            if creditsVal:
                fomatter = getBWFormatter(Currency.CREDITS)
                result.append(cls.__makeQuestsAchieve(u'battleQuestsCredits', credits=fomatter(creditsVal)))
        slots = data.get(u'slots', 0)
        if slots:
            result.append(cls.__makeQuestsAchieve(u'battleQuestsSlots', slots=backport.getIntegralFormat(slots)))
        if not asBattleFormatter:
            dailyBattles = data.get(u'rankedDailyBattles', 0)
            persistBattles = data.get(u'rankedBonusBattles', 0)
            rankedBonusBattlesStr = InvoiceReceivedFormatter.getRankedBonusBattlesString(persistBattles, dailyBattles)
            if rankedBonusBattlesStr:
                mainStrRes = R.strings.messenger.serviceChannelMessages.battleResults.quests.rankedBonusBattles()
                result.append(backport.text(mainStrRes, bonusBattles=rankedBonusBattlesStr))
        items = data.get(u'items', {})
        itemsNames = []
        for intCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            if itemTypeID == I_T.crewBook:
                if asBattleFormatter:
                    continue
                itemDescr = tankmen.getItemByCompactDescr(intCD)
                name = _getCrewBookUserString(itemDescr)
            else:
                itemDescr = vehicles_core.getItemByCompactDescr(intCD)
                name = itemDescr.i18n.userString
            itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(count)))

        goodies = data.get(u'goodies', {})
        excludeGoodies = set()
        for goodieID, ginfo in goodies.iteritems():
            if goodieID in cls.__itemsCache.items.shop.demountKits:
                excludeGoodies.add(goodieID)
                demountKit = cls.__goodiesCache.getDemountKit(goodieID)
                if demountKit is not None and demountKit.enabled:
                    itemsNames.append(backport.text(R.strings.demount_kit.demountKit.gained.count(), count=ginfo.get(u'count')))
            if goodieID in cls.__itemsCache.items.shop.recertificationForms:
                excludeGoodies.add(goodieID)
                rf = cls.__goodiesCache.getRecertificationForm(goodieID)
                if rf is not None and rf.enabled:
                    itemsNames.append(backport.text(R.strings.system_messages.bonuses.booster.value(), count=ginfo.get(u'count'), name=rf.userName))

        abilityPts = data.get(constants.EPIC_ABILITY_PTS_NAME)
        if abilityPts:
            name = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.epicAbilityPoints())
            itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=name, count=backport.getIntegralFormat(abilityPts)))
        tokens = data.get(u'tokens')
        if tokens:
            for tokenID, tokenData in tokens.iteritems():
                count = backport.getIntegralFormat(tokenData.get(u'count', 1))
                if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=backport.text(R.strings.quests.bonusName.battle_bonus_x5()), count=count))
                if tokenID.startswith(CREW_BONUS_X3_TOKEN):
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=backport.text(R.strings.quests.bonusName.crew_bonus_x3()), count=count))
                if tokenID == COMP7_TOKEN_WEEKLY_REWARD_ID:
                    itemsNames.append(backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.items.name(), name=backport.text(R.strings.comp7.system_messages.weeklyReward.tokens()), count=count))
                if tokenID.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                    lootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
                    if lootBox:
                        itemsNames.append(makeHtmlString(u'html_templates:lobby/quests/bonuses', u'rawLootBox', {u'name': lootBox.getUserName(),
                         u'count': int(count)}))

        entitlementsList = [ (eID, eData.get(u'count', 0)) for eID, eData in data.get(u'entitlements', {}).iteritems() ]
        entitlementsStr = InvoiceReceivedFormatter.getEntitlementsString(entitlementsList)
        if entitlementsStr:
            itemsNames.append(entitlementsStr)
        if itemsNames:
            result.append(cls.__makeQuestsAchieve(u'battleQuestsItems', names=u', '.join(itemsNames)))
        _extendCrewSkinsData(data, result)
        if processCustomizations:
            _extendCustomizationData(data, result, htmlTplPostfix=u'QuestsReceived')
        berths = data.get(u'berths', 0)
        if berths:
            result.append(cls.__makeQuestsAchieve(u'battleQuestsBerths', berths=backport.getIntegralFormat(berths)))
        tmen = data.get(u'tankmen', {})
        if tmen:
            result.append(InvoiceReceivedFormatter.getTankmenString(tmen))
        goodies = data.get(u'goodies', {})
        if goodies:
            strGoodies = InvoiceReceivedFormatter.getGoodiesString(goodies, exclude=excludeGoodies)
            if strGoodies:
                result.append(strGoodies)
        enhancements = data.get(u'enhancements', {})
        if enhancements:
            strEnhancements = InvoiceReceivedFormatter.getEnhancementsString(enhancements)
            if strEnhancements:
                result.append(strEnhancements)
        if not asBattleFormatter:
            blueprints = data.get(u'blueprints', {})
            if blueprints:
                strBlueprints = InvoiceReceivedFormatter.getBlueprintString(blueprints)
                if strBlueprints:
                    result.append(strBlueprints)
        if not asBattleFormatter:
            achievementsNames = cls._extractAchievements(data)
            if achievementsNames:
                result.append(cls.__makeQuestsAchieve(u'battleQuestsPopUps', achievements=u', '.join(achievementsNames)))
            addBadgesStrings, removedBadgesStrings = cls.__extractBadges(data)
            if addBadgesStrings:
                result.append(cls.__makeQuestsAchieve(u'badgeAchievement', badges=u', '.join(addBadgesStrings)))
            if removedBadgesStrings:
                result.append(cls.__makeQuestsAchieve(u'removedBadgeAchievement', badges=u', '.join(removedBadgesStrings)))
        if not asBattleFormatter:
            for crewbookName in data.get(u'selectableCrewbook', {}):
                result.append(backport.text(R.strings.messenger.serviceChannelMessages.selectableCrewbook.dyn(crewbookName)()))

        if not asBattleFormatter:
            strDogTags = cls._processDogTags(data.get(u'dogTagComponents', {}))
            if strDogTags:
                result.append(strDogTags)
        return result

    @classmethod
    def _processTokens(cls, tokens):
        pass

    @classmethod
    def _processDogTags(cls, dogTags):
        result = []
        for dogTag in dogTags:
            componentID = dogTag.get(u'id')
            component = componentConfigAdapter.getComponentById(componentID)
            if component is None:
                _logger.error(u'Wrong DogTag componentID: %s', componentID)
                continue
            result.append(backport.text(R.strings.messenger.serviceChannelMessages.dogTags.bonus.dyn(component.viewType.value)(), name=dogTagComposer.getComponentTitle(componentID)))

        return cls._SEPARATOR.join(result)

    @classmethod
    def _extractAchievements(cls, data):
        achieves = data.get(u'popUpRecords', [])
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
        for rec in data.get(u'dossier', {}).values():
            it = rec if not isinstance(rec, dict) else rec.iteritems()
            for (block, name), recData in it:
                if name != u'':
                    isRemoving = recData[u'value'] < 0
                    if block == BADGES_BLOCK:
                        if isRemoving:
                            removedBadgesStrings.append(backport.text(R.strings.badge.dyn(u'badge_{}'.format(name))()))
                        else:
                            addBadgesStrings.append(backport.text(R.strings.badge.dyn(u'badge_{}'.format(name))()))

        return (addBadgesStrings, removedBadgesStrings)

    @classmethod
    def __makeQuestsAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)


class TokenQuestsFormatter(WaitItemsSyncFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __MESSAGE_TEMPLATE = u'tokenQuests'

    def __init__(self, subFormatters=()):
        super(TokenQuestsFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()
        self.__subFormatters = subFormatters

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = set(data.get(u'completedQuestIDs', set()))
            completedQuestIDs.update(data.get(u'rewardsGottenQuestIDs', set()))
            popUps = set(data.get(u'popUpRecords', set()))
            for qID in completedQuestIDs:
                self.__processMetaActions(qID)

            for subFormatter in self.__collectSubFormatters():
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

    def canBeEmpty(self):
        return True

    @classmethod
    def __processMetaActions(cls, questID):
        quest = cls.__eventsCache.getAllQuests().get(questID)
        if quest is None:
            _logger.debug(u'Could not find quest with ID: %s', questID)
            return
        else:
            for bonus in quest.getBonuses():
                if not isinstance(bonus, MetaBonus):
                    continue
                for action, params in bonus.getActions():
                    bonus.handleAction(action, params)

            return

    def __collectSubFormatters(self):
        self.__subFormatters = self.__subFormatters or collectTokenQuestsSubFormatters()
        return self.__subFormatters

    def __formatSimpleTokenQuests(self, message, questIDs, popUps):
        rewards = getRewardsForQuests(message, questIDs)
        rewards[u'popUpRecords'] = popUps
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)
        if fmt is not None:
            templateParams = {u'achieves': fmt}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class NCMessageFormatter(ServiceChannelFormatter):
    __templateKeyFormat = u'notificationsCenterMessage_{0}'

    def format(self, message, *args):
        _logger.debug(u'Message has received from notification center %s', message)
        data = z_loads(message.data)
        if not data:
            return []
        if u'body' not in data or not data[u'body']:
            return []
        templateKey = self.__getTemplateKey(data)
        priority = self.__getGuiPriority(data)
        topic = self.__getTopic(data)
        body = self.__getBody(data)
        settings = self._getGuiSettings(message, templateKey, priority)
        msgType = data[u'type']
        if msgType == NC_MESSAGE_TYPE.POLL:
            if not GUI_SETTINGS.isPollEnabled:
                return []
            if not self.__fetchPollData(data, settings):
                return []
        formatted = g_settings.msgTemplates.format(templateKey, ctx={u'topic': topic,
         u'body': body})
        return [MessageData(formatted, settings)]

    def __getTemplateKey(self, data):
        if u'type' in data:
            msgType = data[u'type']
            if msgType not in NC_MESSAGE_TYPE.RANGE:
                _logger.warning(u'Type of message is not valid, uses default type %s', msgType)
                msgType = NC_MESSAGE_TYPE.INFO
        else:
            msgType = NC_MESSAGE_TYPE.INFO
        return self.__templateKeyFormat.format(msgType)

    def __getGuiPriority(self, data):
        priority = NC_MESSAGE_PRIORITY.DEFAULT
        if u'priority' in data:
            priority = data[u'priority']
            if priority not in NC_MESSAGE_PRIORITY.ORDER:
                _logger.warning(u'Priority of message is not valid, uses default priority %s', priority)
                priority = NC_MESSAGE_PRIORITY.DEFAULT
        return NotificationPriorityLevel.convertFromNC(priority)

    def __getTopic(self, data):
        topic = u''
        if u'topic' in data:
            topic = data[u'topic']
        if topic:
            topic = g_settings.htmlTemplates.format(u'notificationsCenterTopic', ctx={u'topic': topic})
        return topic

    def __getBody(self, data):
        body = data[u'body']
        if u'context' in data:
            body = body % self.__formatContext(data[u'context'])
        return body

    def __fetchPollData(self, data, settings):
        result = False
        if u'link' in data and data[u'link']:
            if u'topic' in data:
                topic = data[u'topic']
            else:
                topic = u''
            settings.auxData = [data[u'link'], topic]
            result = True
        return result

    def __formatContext(self, ctx):
        result = {}
        if not isinstance(ctx, types.DictType):
            _logger.error(u'Context is invalid %s', ctx)
            return result
        getItemFormat = NCContextItemFormatter.getItemFormat
        for key, item in ctx.iteritems():
            if len(item) > 1:
                itemType, itemValue = item[0:2]
                result[key] = getItemFormat(itemType, itemValue)
            _logger.error(u'Context item is invalid %s', item)
            result[key] = str(item)

        return result


class ClanMessageFormatter(ServiceChannelFormatter):
    __templates = {SYS_MESSAGE_CLAN_EVENT.LEFT_CLAN: u'clanMessageWarning'}

    def format(self, message, *args):
        _logger.debug(u'Message has received from clan %s', message)
        data = message.data
        if data and u'event' in data:
            event = data[u'event']
            templateKey = self.__templates.get(event)
            fullName = getClanFullName(passCensor(data[u'clanName']), passCensor(data[u'clanAbbrev']))
            message = backport.text(R.strings.messenger.serviceChannelMessages.clan.dyn(SYS_MESSAGE_CLAN_EVENT_NAMES[event])())
            formatted = g_settings.msgTemplates.format(templateKey, ctx={u'message': message,
             u'fullClanName': fullName})
            settings = self._getGuiSettings(message, templateKey)
            return [MessageData(formatted, settings)]
        return []


class StrongholdMessageFormatter(ServiceChannelFormatter):
    __templates = {constants.SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED: u'fortReserveActivatedMessage'}
    DEFAULT_WARNING = u'fortMessageWarning'

    def __init__(self):
        super(StrongholdMessageFormatter, self).__init__()
        self.__messagesFormatters = {constants.SYS_MESSAGE_FORT_EVENT.RESERVE_ACTIVATED: BoundMethodWeakref(self._reserveActivatedMessage),
         constants.SYS_MESSAGE_FORT_EVENT.RESERVE_EXPIRED: BoundMethodWeakref(self._reserveExpiredMessage)}

    def format(self, message, *args):
        _logger.debug(u'Message has received from fort %s', message)
        data = message.data
        if data and u'event' in data:
            event = data[u'event']
            templateKey = self.__templates.get(event, self.DEFAULT_WARNING)
            formatter = self.__messagesFormatters.get(event)
            if formatter is not None:
                messageSting = formatter(data)
                formatted = g_settings.msgTemplates.format(templateKey, ctx={u'message': messageSting})
                settings = self._getGuiSettings(message, templateKey)
                return [MessageData(formatted, settings)]
            _logger.warning(u'StrongholdMessageFormatter has no available formatters for given message type: %s', event)
        return []

    def _buildMessage(self, event, ctx=None):
        if ctx is None:
            ctx = {}
        return backport.text(R.strings.messenger.serviceChannelMessages.fort.dyn(SYS_MESSAGE_FORT_EVENT_NAMES[event])(), **ctx)

    def getOrderUserString(self, orderTypeID):
        return backport.text(R.strings.fortifications.orders.dyn(constants.FORT_ORDER_TYPE_NAMES[orderTypeID])())

    def _reserveActivatedMessage(self, data):
        event = data[u'event']
        orderTypeID = data[u'orderTypeID']
        expirationTime = data[u'timeExpiration']
        order = text_styles.neutral(self.getOrderUserString(orderTypeID))
        return self._buildMessage(event, {u'order': order,
         u'timeLeft': backport.getTillTimeStringByRClass(time_utils.getTimeDeltaFromNow(expirationTime), R.strings.menu.Time.timeValueWithSecs, removeLeadingZeros=False)})

    def _reserveExpiredMessage(self, data):
        return self._buildMessage(data[u'event'], {u'order': self.getOrderUserString(data[u'orderTypeID'])})


class VehicleRentedFormatter(ServiceChannelFormatter):
    _templateKey = u'vehicleRented'

    def format(self, message, *args):
        data = message.data
        vehTypeCD = data.get(u'vehTypeCD', None)
        expiryTime = data.get(u'time', None)
        return [MessageData(self._getMessage(vehTypeCD, expiryTime), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else []

    def _getMessage(self, vehTypeCD, expiryTime):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {u'vehicleName': vehicleName,
         u'expiryTime': text_styles.titleFont(TimeFormatter.getLongDatetimeFormat(expiryTime))}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class RentalsExpiredFormatter(ServiceChannelFormatter):
    _templateKey = u'rentalsExpired'

    def format(self, message, *args):
        vehTypeCD = message.data.get(u'vehTypeCD', None)
        return [MessageData(self._getMessage(vehTypeCD), self._getGuiSettings(message, self._templateKey))] if vehTypeCD is not None else (None, None)

    def _getMessage(self, vehTypeCD):
        vehicleName = getUserName(vehicles_core.getVehicleType(vehTypeCD))
        ctx = {u'vehicleName': vehicleName}
        return g_settings.msgTemplates.format(self._templateKey, ctx=ctx)


class PersonalMissionsQuestAchievesFormatter(QuestAchievesFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def _processTokens(cls, data):
        quest = cls.__eventsCache.getPersonalMissions().getAllQuests().get(data.get(u'potapovQuestID'))
        if quest:
            result = []
            completionToken = PERSONAL_MISSION_TOKEN % (quest.getCampaignID(), quest.getOperationID())
            if completionToken in data.get(u'tokens', {}):
                bonuses = quest.getBonuses(u'tokens')
                if bonuses:
                    for b in bonuses:
                        if b.getName() == u'completionTokens' and completionToken in b.getTokens().keys():
                            tUserName = first(CompletionTokensBonusFormatter().format(b)).userName
                            result.append(g_settings.htmlTemplates.format(u'completionTokens', {u'completionToken': tUserName}))

            return u', '.join(result)


class LootBoxAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def _processTokens(cls, data):
        result = []
        for token in data.get(u'tokens', {}).iterkeys():
            tankmanTokenResult = _processTankmanToken(token)
            if tankmanTokenResult:
                result.append(tankmanTokenResult)

        return u'\n'.join(result)

    @classmethod
    def _extractAchievements(cls, data):
        return _getAchievementsFromQuestData(data)


class BattlePassQuestAchievesFormatter(QuestAchievesFormatter):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    _BULLET = u'\u2022 '
    _SEPARATOR = u'<br/>' + _BULLET

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
        for token, tokenData in data.get(u'tokens', {}).iteritems():
            if token.startswith(BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS):
                offer = cls.__offersProvider.getOfferByToken(getOfferTokenByGift(token))
                if offer is not None:
                    gift = first(offer.getAllGifts())
                    giftType = token.split(u':')[2]
                    rewardChoiceTokens.setdefault(giftType, 0)
                    rewardChoiceTokens[giftType] += gift.giftCount * tokenData.get(u'count', 1)
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
        tokens.sort(key=lambda x: (int(x.split(u':')[-2]), int(x.split(u':')[-1])))
        return [ cls.__getFormattedStyleProgress(token) for token in tokens ]

    @classmethod
    def __processRewardChoiceTokens(cls, tokens):
        result = []
        rewardSelectTemplate = u'battlePassRewardSelectToken'
        rChosenBonuses = R.strings.battle_pass.chosenBonuses.bonus
        for rewardType, count in tokens.iteritems():
            result.append(g_settings.htmlTemplates.format(rewardSelectTemplate, {u'text': backport.text(rChosenBonuses.dyn(rewardType)()),
             u'count': count}))

        return result

    @classmethod
    def __getFormattedStyleProgress(cls, token):
        from gui.battle_pass.battle_pass_helpers import getStyleForChapter
        chapter = int(token.split(u':')[3])
        level = int(token.split(u':')[4])
        style = getStyleForChapter(chapter)
        text = backport.text(R.strings.battle_pass.styleProgressBonus(), styleName=style.userName, level=int2roman(level))
        return g_settings.htmlTemplates.format(u'battlePassStyleProgressToken', {u'text': text})


class CollectionsFormatter(QuestAchievesFormatter):
    __BULLET = u'\u2022 '

    @classmethod
    def formatQuestAchieves(cls, rewards, asBattleFormatter, processCustomizations=True, processTokens=True):
        collectionEntitlements = popCollectionEntitlements(rewards)
        collectionItems = cls.__formatItems((_getCollectionItemName(entitlementName) for entitlementName in collectionEntitlements.iterkeys() if entitlementName.startswith(COLLECTION_ITEM_PREFIX_NAME)))
        ordinaryItems = super(CollectionsFormatter, cls).formatQuestAchieves(rewards, asBattleFormatter, processCustomizations, processTokens)
        if ordinaryItems is not None:
            ordinaryItemsNames = ordinaryItems.split(cls._SEPARATOR)
            ordinaryItems = cls.__formatItems(ordinaryItemsNames)
        return cls._SEPARATOR.join((collectionItems or u'', ordinaryItems or u''))

    @classmethod
    def __formatItems(cls, items):
        return cls._SEPARATOR.join((u'{} {}'.format(cls.__BULLET, itemName) for itemName in items)) if items else u''


class BattleMattersQuestAchievesFormatter(QuestAchievesFormatter):
    __battleMattersController = dependency.descriptor(IBattleMattersController)

    @classmethod
    def _processTokens(cls, tokens):
        return text_styles.stats(backport.text(R.strings.messenger.serviceChannelMessages.battleMatters.token())) if cls.isWithSelectableReward(tokens) else u''

    @classmethod
    def isWithSelectableReward(cls, awardsDict):
        if u'tokens' not in awardsDict:
            return False
        else:
            mainTokenID = cls.__battleMattersController.getDelayedRewardToken()
            isWithSelectableReward = awardsDict[u'tokens'].pop(mainTokenID, None) is not None
            if not awardsDict[u'tokens']:
                awardsDict.pop(u'tokens')
            return isWithSelectableReward


class WinbackQuestAchievesFormatter(QuestAchievesFormatter):
    __winbackController = dependency.descriptor(IWinbackController)

    @classmethod
    def getSelectableRewards(cls, awardsDict):
        if u'tokens' not in awardsDict:
            return []
        return [ SelectableBonus({tokenId: tokenData}) for tokenId, tokenData in awardsDict[u'tokens'].iteritems() if cls.__winbackController.isWinbackOfferToken(tokenId) ]

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        rewards = deepcopy(data)
        discounts = cls._formatDiscounts(rewards)
        result = super(WinbackQuestAchievesFormatter, cls).formatQuestAchieves(rewards, asBattleFormatter, processCustomizations, processTokens)
        if discounts is None:
            return result
        else:
            return discounts if result is None else cls._SEPARATOR.join((result, discounts))

    @classmethod
    def _formatDiscounts(cls, rewards):
        from gui.impl.lobby.winback.winback_bonus_packer import handleWinbackDiscounts, cutVehDiscountsFromBonuses
        descountsRes = R.strings.messenger.serviceChannelMessages.winback.awards
        results = []
        if u'blueprints' in rewards or u'goodies' in rewards:
            rewards, winbackRewards = cutVehDiscountsFromBonuses(rewards)
            winbackBonuses = handleWinbackDiscounts(winbackRewards)
            for bonus in winbackBonuses:
                for cd in bonus.getVehicleCDs():
                    vehicle = bonus.getVehicle(cd)
                    goodyID, blueprintCount = bonus.getResources(cd)
                    results.append(text_styles.rewards(backport.text(descountsRes.discountConcrete(), name=vehicle.userName, creditDiscount=getDiscountFromGoody(goodyID)[0], expDiscount=int(getDiscountFromBlueprint(cd, blueprintCount)))))

            if winbackBonuses:
                return backport.text(descountsRes.discountHeader()) + u', '.join(results)
        return None

    @classmethod
    def _processTokens(cls, tokens):
        selectableBonuses = cls.getSelectableRewards(tokens)
        selectablesList = [ (int(getLevelFromSelectableToken(first(bonus.getTokens()))), bonus.getType()) for bonus in selectableBonuses ]
        if not selectablesList:
            return u''
        selectablesList = sorted(selectablesList, key=lambda item: item[0])
        strs = []
        for selectable in selectablesList:
            level, selectableType = selectable
            strs.append(backport.text(R.strings.messenger.serviceChannelMessages.winback.awards.dyn(selectableType)(), level=int2roman(level)))

        return cls._SEPARATOR.join(strs)


class Comp7QualificationRewardsFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = u'<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(Comp7QualificationRewardsFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result


class _GoodyFormatter(WaitItemsSyncFormatter):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    _VARIETY_TO_TEMPLATE = {}

    @staticmethod
    def getBoosterAdditionalParams(message):
        obtainedValue = message.data.get(u'obtainedValues', {})
        resourceRows = []
        for bonusTypeName, value in obtainedValue.iteritems():
            resourceRows.append(g_settings.htmlTemplates.format(u'boosterExpiredRow', ctx={u'resourceName': html.escape(backport.text(R.strings.messenger.serviceChannelMessages.boosterExpiredResourceName.dyn(bonusTypeName)())),
             u'value': html.escape(str(value))}))

        if resourceRows:
            resourceRows.append(g_settings.htmlTemplates.format(u'boosterExpiredAdditionalRow'))
        return {u'boostersInformation': u''.join(resourceRows)}

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        yield lambda callback: callback(True)
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            gid = message.data.get(u'gid')
            additionalParams = {}
            goodieDescr = self.__goodiesCache.getGoodieByID(gid)
            if goodieDescr.variety == GOODIE_VARIETY.DISCOUNT:
                goodie = self.__goodiesCache.getDiscount(gid)
            elif goodieDescr.variety == GOODIE_VARIETY.BOOSTER:
                goodie = self.__goodiesCache.getBooster(gid)
                additionalParams = self.getBoosterAdditionalParams(message)
            elif goodieDescr.variety == GOODIE_VARIETY.RECERTIFICATION_FORM:
                goodie = self.__goodiesCache.getRecertificationForm(gid)
            else:
                goodie = self.__goodiesCache.getDemountKit(gid)
            if goodie:
                templateName = self._getTemplateName(goodieDescr.variety)
                if templateName:
                    ctx = {u'boosterName': goodie.userName}
                    if additionalParams:
                        ctx.update(additionalParams)
                    formatted = g_settings.msgTemplates.format(templateName, ctx=ctx)
                    callback([MessageData(formatted, self._getGuiSettings(message, templateName))])
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
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.BOOSTER: u'boosterExpired'}


class GoodyDisabledFormatter(_GoodyFormatter):
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.DEMOUNT_KIT: u'demountKitDisabled',
     GOODIE_VARIETY.BOOSTER: u'boosterDisabled'}


class GoodieEnabledFormatter(_GoodyFormatter):
    _VARIETY_TO_TEMPLATE = {GOODIE_VARIETY.DEMOUNT_KIT: u'demountKitEnabled'}


class TelecomStatusFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            try:
                template = u'telecomVehicleStatus'
                ctx = self.__getMessageContext(message.data)
                settings = self._getGuiSettings(message, template)
                formatted = g_settings.msgTemplates.format(template, ctx, data={u'timestamp': time.time()})
            except Exception:
                _logger.error(u"Can't format telecom status message %s", message)
                _logger.exception(u'TelecomStatusFormatter catches exception')

        messageData = MessageData(formatted, settings)
        callback([messageData])
        return None

    @staticmethod
    def __addProviderToRes(res, provider):
        return res.dyn(provider, res.default)

    def __getMessageContext(self, data):
        key = u'vehicleUnblocked' if data[u'orderStatus'] else u'vehicleBlocked'
        vehTypeDescrs = data[u'vehTypeCompDescrs']
        provider = u''
        if vehTypeDescrs:
            bundleId = data[u'bundleID']
            telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
            provider = telecomConfig.getInternetProvider(bundleId)
        providerLocName = u''
        if provider:
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            providerLocName = backport.text(providerLocRes.name()) if providerLocRes else u''
        msgctx = {u'vehicles': self.__getVehicleUserNames(vehTypeDescrs),
         u'provider': providerLocName}
        ctx = {}
        resShortcut = R.strings.system_messages.telecom
        for txtBlock in (u'title', u'comment', u'subcomment'):
            ctx[txtBlock] = backport.text(self.__addProviderToRes(resShortcut.notifications.dyn(key).dyn(txtBlock), provider)(), **msgctx)

        return ctx

    @classmethod
    def __getVehicleUserNames(cls, vehTypeCompDescrs):
        itemGetter = cls._itemsCache.items.getItemByCD
        return u', '.join((itemGetter(vehicleCD).userName for vehicleCD in vehTypeCompDescrs))


class TelecomReceivedInvoiceFormatter(InvoiceReceivedFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @staticmethod
    def invoiceHasCrew(data):
        dataEx = data.get(u'data', {})
        hasCrew = False
        vehicles = dataEx.get(u'vehicles', {})
        for vehicle in vehicles:
            if vehicles[vehicle].get(u'tankmen', None):
                hasCrew = True

        return hasCrew

    @staticmethod
    def invoiceHasBrotherhood(data):
        dataEx = data.get(u'data', {})
        hasBrotherhood = False
        vehicles = dataEx.get(u'vehicles', {})
        for vehicle in vehicles:
            tankmens = vehicles[vehicle].get(u'tankmen', [])
            for tman in tankmens:
                if isinstance(tman, str):
                    tankmanDecsr = tankmen.TankmanDescr(compactDescr=tman)
                    if u'brotherhood' in tankmanDecsr.freeSkills:
                        hasBrotherhood = True
                        break
                if u'brotherhood' in tman.get(u'freeSkills', []):
                    hasBrotherhood = True
                    break

        return hasBrotherhood

    @staticmethod
    def _addProviderToRes(res, provider):
        return res.dyn(provider, res.default)

    def _getProvider(self, data):
        telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
        return telecomConfig.getInternetProvider(data[u'bundleID'])

    @classmethod
    def _isValidCD(cls, vehCompDescr):
        return vehCompDescr > 0

    def _getVehicles(self, data):
        dataEx = data.get(u'data', {})
        if not dataEx:
            return
        else:
            vehicles = [dataEx.get(u'vehicles', {})]
            rentedVehNames = None
            if vehicles:
                _, _, rentedVehNames = self._getVehicleNames(vehicles)
            return rentedVehNames

    def _getMessageTemplateKey(self, emitterID, assetType):
        pass

    def _getMessageContext(self, data, vehicleNames):
        msgctx = {}
        hasCrew = self.invoiceHasCrew(data)
        if hasCrew:
            if self.invoiceHasBrotherhood(data):
                skills = u' (%s)' % backport.text(R.strings.crew_perks.brotherhood.name())
            else:
                skills = u''
            msgctx[u'crew'] = backport.text(self._addProviderToRes(R.strings.system_messages.telecom.notifications.vehicleReceived.crew, self._getProvider(data)), skills=skills)
        else:
            msgctx[u'crew'] = u''
        msgctx[u'vehicles'] = u', '.join(vehicleNames)
        msgctx[u'datetime'] = self._getOperationTimeString(data)
        ctx = {}
        resShortcut = R.strings.system_messages.telecom.notifications.vehicleReceived
        for txtBlock in (u'title', u'comment', u'subcomment'):
            ctx[txtBlock] = backport.text(self._addProviderToRes(resShortcut.dyn(txtBlock), self._getProvider(data))(), **msgctx)

        return ctx

    def _formatData(self, emitterID, assetType, data):
        vehicleNames = self._getVehicles(data)
        return None if not vehicleNames else g_settings.msgTemplates.format(self._getMessageTemplateKey(emitterID, assetType), ctx=self._getMessageContext(data, vehicleNames), data={u'timestamp': time.time()})


class TelecomRemovedInvoiceFormatter(TelecomReceivedInvoiceFormatter):

    @classmethod
    def _isValidCD(cls, vehCompDescr):
        return vehCompDescr < 0

    def _getMessageTemplateKey(self, emitterID, assetType):
        pass

    def _getVehicles(self, data):
        dataEx = data.get(u'data', {})
        if not dataEx:
            return
        else:
            vehicles = [dataEx.get(u'vehicles', {})]
            removedVehNames = None
            if vehicles:
                _, removedVehNames, _ = self._getVehicleNames(vehicles)
            return removedVehNames

    def _getMessageContext(self, data, vehicleNames):
        provider = self._getProvider(data)
        providerLocTariff = u''
        if provider != u'':
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            providerLocTariff = backport.text(providerLocRes.tariff()) if providerLocRes else u''
        msgctx = {u'vehicles': u', '.join(vehicleNames),
         u'datetime': self._getOperationTimeString(data),
         u'tariff': providerLocTariff}
        ctx = {}
        resShortcut = R.strings.system_messages.telecom.notifications.vehicleRemoved
        for txtBlock in (u'title', u'comment', u'subcomment'):
            ctx[txtBlock] = backport.text(self._addProviderToRes(resShortcut.dyn(txtBlock), provider)(), **msgctx)

        return ctx


class PrbVehicleKickFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    typeKick = u'prbVehicleKick'

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get(u'vehInvID', None)
        self.__itemsCache.items.getVehicle(vehInvID)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format(self.typeKick, ctx={u'vehName': vehicle.userName})
        return [MessageData(formatted, self._getGuiSettings(message, self.typeKick))]


class PrbVehicleKickFilterFormatter(PrbVehicleKickFormatter):
    typeKick = u'prbVehicleKickFilter'


class PrbVehicleMaxSpgKickFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get(u'vehInvID', None)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format(u'prbVehicleMaxSpgKick', ctx={u'vehName': vehicle.userName})
        return [MessageData(formatted, self._getGuiSettings(message, u'prbVehicleMaxSpgKick'))]


class PrbVehicleMaxScoutKickFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = None
        data = message.data
        vehInvID = data.get(u'vehInvID', None)
        if vehInvID:
            vehicle = self.__itemsCache.items.getVehicle(vehInvID)
            if vehicle:
                formatted = g_settings.msgTemplates.format(u'prbVehicleMaxScoutKick', ctx={u'vehName': vehicle.userName})
        return [MessageData(formatted, self._getGuiSettings(message, u'prbVehicleMaxScoutKick'))]


class RotationGroupLockFormatter(ServiceChannelFormatter):

    def format(self, message, *args):
        templateKey = self._getMessageTemplateKey()
        if isinstance(message.data, list):
            groups = u', '.join(map(str, message.data))
        else:
            groups = message.data
        formatted = g_settings.msgTemplates.format(templateKey, ctx={u'groupNum': groups})
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
                if value and value != u'0':
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
        awardsDict.pop(u'tokens', None)
        return EOL.join(processedTokens)

    @classmethod
    def __getYearPointsAmount(cls, awardsDict):
        return awardsDict.get(u'tokens', {}).get(YEAR_POINTS_TOKEN, {}).get(u'count', 0)

    @classmethod
    def __getSelectableAwardCount(cls, awardsDict):
        awardMainTokenID = YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX
        result = 0
        for tokenID in awardsDict.get(u'tokens', {}):
            if tokenID.startswith(awardMainTokenID):
                result += int(tokenID.split(u':')[-1])

        return result

    def __packAward(self, key, value):
        return u'{} {}'.format(backport.text(R.strings.system_messages.ranked.notifications.bonusName.dyn(key)()), self.__awardsStyles.get(key, text_styles.stats)(value))


class BRQuestsFormatter(TokenQuestsFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = message.data.get(u'completedQuestIDs', set())
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
            formattedMessage = g_settings.msgTemplates.format(u'BrLevelQuest', ctx={u'levelsBlock': EOL.join([ formattedLevels[key] for key in sorted(formattedLevels) ]),
             u'awardsBlock': self._packTitleAwards(data)})
        return [formattedMessage]

    def _packTitleAwards(self, awardsDict):
        return self._achievesFormatter.formatQuestAchieves(awardsDict, asBattleFormatter=False) or u''

    @classmethod
    def __getLevel(cls, quest):
        return str(quest.getID().split(u':')[-1])


class RankedQuestFormatter(WaitItemsSyncFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedQuestFormatter, self).__init__()
        self.__achievesFormatter = RankedQuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = message.data.get(u'completedQuestIDs', set())
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
            formattedMessage = g_settings.msgTemplates.format(u'rankedRankQuest', ctx={u'ranksBlock': EOL.join([ formattedRanks[key] for key in sorted(formattedRanks) ]),
             u'awardsBlock': self.__achievesFormatter.packRankAwards(data)})
        return [formattedMessage]


class PersonalMissionFailedFormatter(WaitItemsSyncFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    _template = u'PersonalMissionFailedMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            potapovQuestIDs = data.get(u'questIDs')
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
                    ctx = {u'questID': questID,
                     u'operation': operation.getShortUserName(),
                     u'missionShortName': quest.getShortUserName(),
                     u'missionName': quest.getUserName()}
                    formatted = g_settings.msgTemplates.format(self._template, ctx=ctx, data={u'savedData': {u'questID': questID}})
                    settings = self._getGuiSettings(message, self._template, messageType=message.type)
                    settings.showAt = BigWorld.time()
                    callback([MessageData(formatted, settings)])

            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return


class CustomizationChangedFormatter(WaitItemsSyncFormatter):
    _template = u'CustomizationRemoved'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        from gui.customization.shared import SEASON_TYPE_TO_NAME, SEASONS_ORDER
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            vehicleIntCD = first(data)
            vehicleData = data[vehicleIntCD]
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            data = {u'savedData': {u'vehicleIntCD': vehicleIntCD}}
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
                    formattedSeason = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizations.map.dyn(seasonName)()) + u', '.join(items) + u'.'
                    seasonTexts[season] = u'\n' + formattedSeason

            for season in SEASONS_ORDER:
                if season in seasonTexts:
                    text += seasonTexts[season]

            formatted = g_settings.msgTemplates.format(self._template, {u'text': text}, data=data)
            settings = self._getGuiSettings(message, self._template, messageType=message.type)
            settings.showAt = BigWorld.time()
            callback([MessageData(formatted, settings)])
        else:
            callback([MessageData(None, None)])
        return


class ProgressiveRewardFormatter(WaitItemsSyncFormatter):
    _template = u'ProgressiveRewardMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        if message.data and isSynced:
            data = message.data
            if u'rewards' in data and u'level' in data:
                fmt = QuestAchievesFormatter.formatQuestAchieves(data[u'rewards'], False)
                if fmt:
                    formatted = g_settings.msgTemplates.format(self._template, ctx={u'text': fmt})
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
    _piggyBankTemplate = u'PiggyBankSmashedMessage'
    _piggyBankWotPlusTemplate = u'PiggyBankWotPlusSmashedMessage'
    _goldReserveTemplate = u'GoldReserveSmashedMessage'
    _currenciesTemplate = u'CurrenciesReservesSmashedMessage'
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def format(self, message, *args):
        if not message.data:
            return []
        credits_ = message.data.get(u'credits')
        gold = message.data.get(u'gold')
        if self.__wotPlusController.isWotPlusEnabled():
            piggyBankTemplate = self._piggyBankWotPlusTemplate
        else:
            piggyBankTemplate = self._piggyBankTemplate
        if credits_ and not gold:
            ctx = {u'credits': backport.getIntegralFormat(credits_)}
            formatted = g_settings.msgTemplates.format(piggyBankTemplate, ctx)
            return [MessageData(formatted, self._getGuiSettings(message, piggyBankTemplate))]
        if gold and not credits_:
            ctx = {u'gold': backport.getGoldFormat(gold)}
            formatted = g_settings.msgTemplates.format(self._goldReserveTemplate, ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self._goldReserveTemplate))]
        if gold and credits_:
            ctx = {u'credits': backport.getIntegralFormat(credits_),
             u'gold': backport.getGoldFormat(gold)}
            formatted = g_settings.msgTemplates.format(self._currenciesTemplate, ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self._currenciesTemplate))]
        return []


class BlackMapRemovedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'BlackMapRemovedMessage'
    __REASONS_SETTINGS = {MapRemovedFromBLReason.MAP_DISABLED: {u'text': R.strings.messenger.serviceChannelMessages.blackMapRemoved.mapDisabled(),
                                           u'priority': NC_MESSAGE_PRIORITY.MEDIUM},
     MapRemovedFromBLReason.SLOT_DISABLED: {u'text': R.strings.messenger.serviceChannelMessages.blackMapRemoved.slotDisabled(),
                                            u'priority': NC_MESSAGE_PRIORITY.LOW}}

    def format(self, message, *args):
        if message.data:
            mapIDs = message.data.get(u'mapIDs')
            reason = message.data.get(u'reason')
            if mapIDs is None or reason not in self.__REASONS_SETTINGS:
                return [MessageData(None, None)]
            mapNames = []
            for mapID in mapIDs:
                if mapID in ArenaType.g_cache:
                    mapNames.append(i18n.makeString(ArenaType.g_cache[mapID].name))

            settings = self.__REASONS_SETTINGS[reason]
            text = backport.text(settings[u'text'], mapNames=u','.join(mapNames))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=settings[u'priority'])
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementRemovedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'EnhancementRemovedMessage'

    def format(self, message, *args):
        if message.data:
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.removed())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementsWipedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'EnhancementsWipedMessage'

    def format(self, message, *args):
        if message.data:
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.wiped())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': text})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class EnhancementsWipedOnVehiclesFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'EnhancementsWipedOnVehiclesMessage'

    def format(self, message, *args):
        if message.data:
            vehCompDescriptors = message.data.get(u'vehicles', set())
            vehNames = [ getUserName(vehicles_core.getVehicleType(vehCD)) for vehCD in vehCompDescriptors ]
            vehNames = u', '.join(vehNames)
            text = backport.text(R.strings.messenger.serviceChannelMessages.enhancements.wipedOnVehicles())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': text,
             u'vehicleNames': vehNames})
            guiSettings = self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=NC_MESSAGE_PRIORITY.MEDIUM)
            return [MessageData(formatted, guiSettings)]
        else:
            return [MessageData(None, None)]


class BattlePassRewardFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __collections = dependency.descriptor(ICollectionsSystemController)
    __REWARD_TEMPLATE = u'BattlePassRewardSysMessage'
    __COLLECTION_ITEMS_TEMPLATE = u'CollectionItemsSysMessage'
    __PROGRESSION_BUTTON_TEMPLATE = u'BattlePassRewardWithProgressionButtonMessage'
    __SHOP_BUTTON_TEMPLATE = u'BattlePassRewardWithShopButtonMessage'
    __RESOURCE_AVAILABLE_TEMPLATE = u'BattlePassResourceChapterAvailableMessage'
    __CURRENCY_TEMPLATE_KEY = u'battlePassCurrency'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        collectionResultMessage = MessageData(None, None)
        messageResource = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            if u'reward' in data and u'ctx' in data:
                rewards = data.get(u'reward')
                ctx = data.get(u'ctx')
                reason = ctx.get(u'reason')
                newLevel = ctx.get(u'newLevel')
                chapterID = ctx.get(u'chapter')
                collectionEntitlements = popCollectionEntitlements(rewards)
                description = u''
                additionalText = u''
                template = self.__REWARD_TEMPLATE
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.default())
                priorityLevel = None
                savedData = None
                if reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.GIFT_CHAPTER):
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
                        if self.__battlePass.isCompleted() and self.__battlePass.isResourceCompleted():
                            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.text(), season=self.__battlePass.getSeasonNum())
                            template = self.__SHOP_BUTTON_TEMPLATE
                            additionalText = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.additionalText())
                        elif self.__battlePass.isFinalLevel(chapterID, newLevel):
                            chapterName = backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)())
                            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.chapterFinal.text(), chapter=text_styles.credits(chapterName))
                            template = self.__PROGRESSION_BUTTON_TEMPLATE
                            savedData = {u'chapterID': chapterID}
                        else:
                            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.activateChapter.text())
                        priorityLevel = NotificationPriorityLevel.LOW
                    elif reason in (BattlePassRewardReason.INVOICE, BattlePassRewardReason.BATTLE):
                        description, template, priorityLevel, additionalText, savedData = self.__makeAfterBattle(ctx)
                formattedBonuses = BattlePassQuestAchievesFormatter.formatQuestAchieves(rewards, False)
                if formattedBonuses is None:
                    formattedBonuses = u''
                if formattedBonuses and additionalText:
                    additionalText = u'<br/>' + additionalText
                formatted = g_settings.msgTemplates.format(template, ctx={u'header': header,
                 u'description': description,
                 u'text': formattedBonuses,
                 u'additionalText': additionalText}, data={u'savedData': savedData})
                settings = self._getGuiSettings(message, template, messageType=message.type)
                settings.showAt = BigWorld.time()
                if priorityLevel is not None:
                    settings.priorityLevel = priorityLevel
                resultMessage = MessageData(formatted, settings)
                if collectionEntitlements and self.__collections.isEnabled():
                    collectionResultMessage = self.__makeCollectionMessage(collectionEntitlements, message)
                if reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS,
                 BattlePassRewardReason.INVOICE,
                 BattlePassRewardReason.BATTLE,
                 BattlePassRewardReason.SELECT_CHAPTER) and self.__battlePass.isFinalLevel(chapterID, newLevel):
                    messageResource = self.__makeResourceChapterAvailableMessage(chapterID, message)
        callback([resultMessage, collectionResultMessage, messageResource])
        return

    def __makeAfterBattle(self, ctx):
        newLevel = ctx.get(u'newLevel')
        priorityLevel = None
        additionalText = u''
        chapterID = ctx.get(u'chapter')
        savedData = None
        if not (self.__battlePass.isCompleted() and self.__battlePass.isResourceCompleted()):
            chapterName = backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)())
            if not self.__battlePass.isFinalLevel(chapterID, newLevel):
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.newLevel.text(), newLevel=text_styles.credits(newLevel), chapter=text_styles.credits(chapterName))
                priorityLevel = NotificationPriorityLevel.LOW
            else:
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.chapterFinal.text(), chapter=text_styles.credits(chapterName))
            template = self.__PROGRESSION_BUTTON_TEMPLATE
            savedData = {u'chapterID': chapterID}
        else:
            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.text(), season=self.__battlePass.getSeasonNum())
            priorityLevel = NotificationPriorityLevel.LOW
            template = self.__SHOP_BUTTON_TEMPLATE
            additionalText = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.additionalText())
        return (description,
         template,
         priorityLevel,
         additionalText,
         savedData)

    def __makeAfterLevelsPurchase(self, ctx):
        chapterID = ctx.get(u'chapter')
        currentLevel = ctx.get(u'newLevel')
        prevLevel = ctx.get(u'prevLevel')
        chapter = text_styles.credits(backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)()))
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyProgress())
        levelCount = currentLevel - prevLevel
        if self.__battlePass.isFinalLevel(chapterID, currentLevel):
            if self.__battlePass.isCompleted() and self.__battlePass.isResourceCompleted():
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.final.text(), season=self.__battlePass.getSeasonNum())
            else:
                description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.battle.chapterFinal.text(), chapter=chapter)
        else:
            level = currentLevel + 1
            chapter = text_styles.credits(backport.text(R.strings.battle_pass.chapter.fullName.num(chapterID)()))
            description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyProgress.text(), levelCount=text_styles.credits(levelCount), currentLevel=text_styles.credits(level), chapter=chapter)
        price = self.__itemsCache.items.shop.getBattlePassLevelCost().get(Currency.GOLD, 0) * levelCount
        additionalText = self.__makeCurrencyString(Currency.GOLD, price)
        priorityLevel = NotificationPriorityLevel.LOW
        return (header,
         description,
         priorityLevel,
         additionalText)

    def __makeAfterBattlePassPurchase(self, ctx):
        chapterID = ctx.get(u'chapter')
        priceID = ctx.get(u'priceID')
        reason = ctx.get(u'reason')
        if reason == BattlePassRewardReason.GIFT_CHAPTER:
            header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.questGiftBP())
        else:
            header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyBP())
        description = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithRewards.text())
        additionalText = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithRewards.additionalText(), chapter=text_styles.credits(backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)())))
        if reason != BattlePassRewardReason.GIFT_CHAPTER:
            additionalText += u'<br/>' + self.__makePriceString(chapterID, priceID)
        priorityLevel = NotificationPriorityLevel.LOW
        return (header,
         description,
         priorityLevel,
         additionalText)

    def __makePriceString(self, chapterID, priceID):
        return self.__makeCurrencyString(*next(self.__battlePass.getBattlePassCost(chapterID)[priceID].iteritems()))

    def __makeCurrencyString(self, currency, amount):
        return g_settings.htmlTemplates.format(self.__CURRENCY_TEMPLATE_KEY, {u'currency': backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buy.dyn(currency)()),
         u'amount': getBWFormatter(currency)(amount)}) if amount else u''

    def __makeCollectionMessage(self, entitlements, message):
        from gui.collection.collections_helpers import getCollectionFullFeatureName
        messages = R.strings.collections.notifications
        collectionID = int(first(entitlements).split(u'_')[-2])
        collection = self.__collections.getCollection(collectionID)
        title = backport.text(messages.title.collectionName(), feature=getCollectionFullFeatureName(collection))
        text = backport.text(messages.newItemsReceived.text(), items=CollectionsFormatter.formatQuestAchieves({u'entitlements': entitlements}, False))
        formatted = g_settings.msgTemplates.format(self.__COLLECTION_ITEMS_TEMPLATE, ctx={u'title': title,
         u'text': text}, data={u'savedData': {u'collectionId': collectionID}})
        return MessageData(formatted, self._getGuiSettings(message, self.__COLLECTION_ITEMS_TEMPLATE, messageType=SYS_MESSAGE_TYPE.collectionsItems.index()))

    def __makeResourceChapterAvailableMessage(self, chapterID, message):
        resourceChID = self.__battlePass.getResourceChapterID()
        if not self.__battlePass.isMarathonChapter(chapterID) and self.__battlePass.isResourceChapterAvailable() and self.__battlePass.getChapterState(resourceChID) == ChapterState.NOT_STARTED:
            chapterName = backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(resourceChID)())
            textRes = backport.text(R.strings.system_messages.battlePass.recourseChapterUnlock.body(), chapter=chapterName)
            header = backport.text(R.strings.system_messages.battlePass.recourseChapterUnlock.header(), chapter=chapterName)
            formatted = g_settings.msgTemplates.format(self.__RESOURCE_AVAILABLE_TEMPLATE, ctx={u'header': header,
             u'text': textRes})
            settings = self._getGuiSettings(message, self.__RESOURCE_AVAILABLE_TEMPLATE)
            return MessageData(formatted, settings)


class BattlePassBoughtFormatter(WaitItemsSyncFormatter):

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced and message.data.get(u'chapter') == 0:
            template = u'BattlePassBuyMultipleMessage'
            header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyMultiple.text())
            formatted = g_settings.msgTemplates.format(template, ctx={u'header': header})
            settings = self._getGuiSettings(message, template)
            settings.showAt = BigWorld.time()
            resultMessage = MessageData(formatted, settings)
        callback([resultMessage])
        return


class BattlePassGiftByOfferFormatter(WaitItemsSyncFormatter):
    __battlePass = dependency.descriptor(IBattlePassController)

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced and self.__battlePass.isValidChapterID(message.data.get(u'chapter')):
            data = message.data
            chId = data.get(u'chapter')
            header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.questGiftBP())
            chapterName = backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chId)())
            text = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithoutRewards.text(), chapter=text_styles.credits(chapterName))
            template = u'BattlePassDefaultRewardMessage'
            templateParams = {u'text': text,
             u'header': header}
            settings = self._getGuiSettings(message, template, priorityLevel=NotificationPriorityLevel.LOW)
            formatted = g_settings.msgTemplates.format(template, templateParams)
            resultMessage = MessageData(formatted, settings)
        callback([resultMessage])
        return


class BattlePassReachedCapFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = u'BattlePassReachedCapMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            vehCD = data.get(u'vehTypeCompDescr')
            limitPoints = data.get(u'vehiclePoints')
            bonusPoints = data.get(u'bonusPoints')
            if vehCD and limitPoints and bonusPoints:
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.reachedCap.text(), vehName=self.__itemsCache.items.getItemByCD(vehCD).userName, bonusPoints=text_styles.neutral(bonusPoints))
                formatted = g_settings.msgTemplates.format(self.__template, {u'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return


class BattlePassStyleReceivedFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __template = u'BattlePassStyleReceivedMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            rewardType = self.__battlePass.getRewardType(data.get(u'chapter'))
            text = u''
            if rewardType == FinalReward.STYLE:
                styleCD = data.get(u'styleCD')
                if styleCD is not None:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.styleChosen.text(), name=self.__itemsCache.items.getItemByCD(styleCD).userName)
            elif rewardType == FinalReward.TANKMAN:
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.tankmanChosen.text())
            if text:
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.styleChosen.header())
                formatted = g_settings.msgTemplates.format(self.__template, {u'header': header,
                 u'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return


class BattlePassSeasonEndFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = u'BattlePassSeasonEndMessage'
    __rewardTemplate = u'battlePassDefaultRewardReceived'
    _BULLET = u'\u2022 '

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            rewards = data.get(u'data')
            if rewards is not None:
                description = backport.text(R.strings.system_messages.battlePass.seasonEnd.text())
                text = []
                if u'customizations' in rewards:
                    text.extend(self.__formatCustomizationStrings(rewards[u'customizations']))
                if u'items' in rewards:
                    text.extend(self.__formatItemsStrings(rewards[u'items']))
                if u'blueprints' in rewards:
                    text.extend(self.__formatBlueprintsStrings(rewards[u'blueprints']))
                formatted = g_settings.msgTemplates.format(self.__template, {u'description': description,
                 u'text': u'<br>'.join(text)})
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
        elif item.isModernized:
            textRes = R.strings.system_messages.battlePass.seasonEnd.rewards.expequipment()
        else:
            textRes = R.strings.system_messages.battlePass.seasonEnd.rewards.device()
        text = backport.text(textRes, name=item.userName)
        text = self._BULLET + text
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {u'text': text,
         u'count': count})

    def __formatCrewBookString(self, itemCD, count):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        text = backport.text(R.strings.system_messages.battlePass.seasonEnd.rewards.crewBook(), name=item.userName)
        text = self._BULLET + text
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {u'text': text,
         u'count': count})

    def __formatBlueprintsStrings(self, blueprints):
        rewardStrings = []
        for fragmentCD, count in blueprints.iteritems():
            nation = nations.NAMES[getFragmentNationID(fragmentCD)]
            nationName = backport.text(R.strings.nations.dyn(nation)())
            text = backport.text(R.strings.system_messages.battlePass.seasonEnd.rewards.blueprints(), name=nationName)
            text = self._BULLET + text
            rewardStrings.append(g_settings.htmlTemplates.format(self.__rewardTemplate, {u'text': text,
             u'count': count}))

        return rewardStrings

    def __formatCustomizationStrings(self, customizations):
        rewardStrings = []
        for item in customizations:
            guiItemType = item[u'custType']
            itemData = getCustomizationItemData(item[u'id'], guiItemType)
            typeRes = R.strings.system_messages.battlePass.seasonEnd.rewards.dyn(guiItemType)
            if typeRes.exists():
                text = backport.text(typeRes(), name=itemData.userName)
                text = self._BULLET + text
                rewardStrings.append(g_settings.htmlTemplates.format(u'battlePassDefaultStyleReceived', {u'text': text}))

        return rewardStrings


class EpicLevelUpFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __template = u'EpicLevelUpMessage'
    __iconPrefix = u'epicSysMsgLevel'
    __rewardTemplate = u'epicDefaultRewardReceived'
    __gotLevelTemplate = u'epicGotLevel'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            battleResults = message.data
            sysMsgExtraData = battleResults.get(u'sysMsgExtraData')
            newLevel, _ = sysMsgExtraData.get(u'metaLevel')
            battleResults[u'epicAbilityPoints'] = sysMsgExtraData.get(u'epicAbilityPoints')
            icon = self.__iconPrefix + str(self._getLevelUpIconId(newLevel))
            title = backport.text(R.strings.system_messages.epicBattles.levelUp.title())
            levelCongrats = backport.text(R.strings.system_messages.epicBattles.levelUp.body.levelCongrats(), tier=newLevel)
            body = g_settings.htmlTemplates.format(self.__gotLevelTemplate, {u'levelCongrats': levelCongrats})
            awards = backport.text(R.strings.system_messages.epicBattles.levelUp.awards())
            achieves = EpicQuestAchievesFormatter.formatQuestAchieves(battleResults, False)
            formatted = g_settings.msgTemplates.format(self.__template, {u'title': title,
             u'body': body,
             u'awards': awards,
             u'achieves': achieves}, data={u'icon': icon,
             u'savedData': sysMsgExtraData})
            settings = self._getGuiSettings(message, self.__template)
            settings.showAt = BigWorld.time()
            resultMessage = MessageData(formatted, settings)
        callback([resultMessage])
        return

    @staticmethod
    def _getLevelUpIconId(level):
        if level is None:
            return 0
        else:
            for index, levelRange in enumerate(EPIC_BATTLE_LEVEL_IMAGE_INDEX):
                if level in levelRange:
                    return index

            return


class EpicQuestAchievesFormatter(QuestAchievesFormatter):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    _SEPARATOR = u'<br>'
    __rEpicReward = R.strings.messenger.serviceChannelMessages.epicReward
    __rewardTemplate = u'epicLevelUpReward'

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = []
        battlePassPointsResult = cls.__processBattlePassPoints(data)
        if battlePassPointsResult:
            result.append(battlePassPointsResult)
        abilityPointsResult = cls.__processAbilityPoints(data)
        if abilityPointsResult:
            result.append(abilityPointsResult)
        crystalResult = cls.__processCrystal(data)
        if crystalResult:
            result.append(crystalResult)
        tokenResult = cls._processTokens(data)
        if tokenResult and processTokens:
            result.append(tokenResult)
        recertificationFormResult = cls.__processRecertificationForm(data)
        if recertificationFormResult:
            result.append(recertificationFormResult)
        crewBookResult = cls.__processCrewBook(data)
        if crewBookResult:
            result.append(crewBookResult)
        return cls._SEPARATOR.join(result)

    @classmethod
    def __processCrewBook(cls, data):
        items = data.get(u'items', {})
        for itemCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(itemCD)
            if itemTypeID == I_T.crewBook:
                if count > 0:
                    return cls.__makeQuestsAchieve(cls.__rewardTemplate, text=backport.text(cls.__rEpicReward.brochure_gift()), count=count)

    @classmethod
    def __processRecertificationForm(cls, data):
        goodies = data.get(u'goodies', {})
        count = 0
        for goodieID, ginfo in goodies.iteritems():
            if goodieID in cls.__itemsCache.items.shop.recertificationForms:
                recertificationForm = cls.__goodiesCache.getRecertificationForm(goodieID)
                if recertificationForm is not None and recertificationForm.enabled:
                    count += ginfo.get(u'count')

        return cls.__makeQuestsAchieve(cls.__rewardTemplate, text=backport.text(cls.__rEpicReward.recertificationForm_gift()), count=count) if count > 0 else None

    @classmethod
    def __processCrystal(cls, data):
        crystal = data.get(Currency.CRYSTAL, 0)
        return cls.__makeQuestsAchieve(cls.__rewardTemplate, text=backport.text(cls.__rEpicReward.crystal()), count=crystal) if crystal else None

    @classmethod
    def __processBattlePassPoints(cls, data):
        value = sum((points for points in data.get(u'battlePassPoints', {}).get(u'vehicles', {}).itervalues()))
        return cls.__makeQuestsAchieve(cls.__rewardTemplate, text=backport.text(cls.__rEpicReward.battlePassPoints()), count=value) if value > 0 else None

    @classmethod
    def __processAbilityPoints(cls, data):
        value = data.get(u'epicAbilityPoints', 0)
        return cls.__makeQuestsAchieve(cls.__rewardTemplate, text=backport.text(cls.__rEpicReward.epicAbilityPoints()), count=value) if value > 0 else None

    @classmethod
    def _processTokens(cls, data):
        from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift
        result = []
        rewardChoiceTokens = {}
        for token, tokenData in data.get(u'tokens', {}).iteritems():
            from epic_constants import EPIC_OFFER_TOKEN_PREFIX
            if token.startswith(EPIC_OFFER_TOKEN_PREFIX):
                offer = cls.__offersProvider.getOfferByToken(getOfferTokenByGift(token))
                if offer is None:
                    LOG_ERROR(u'Offer for {} token not found'.format(token))
                else:
                    gift = first(offer.getAllGifts())
                    giftType = token.split(u':')[2]
                    rewardChoiceTokens.setdefault(giftType, 0)
                    rewardChoiceTokens[giftType] += gift.giftCount * tokenData.get(u'count', 1)

        result.extend(cls.__processRewardChoiceTokens(rewardChoiceTokens))
        return cls._SEPARATOR.join(result)

    @classmethod
    def __processRewardChoiceTokens(cls, tokens):
        result = []
        rBonuses = R.strings.messenger.serviceChannelMessages.epicReward
        for rewardType, count in tokens.iteritems():
            result.append(g_settings.htmlTemplates.format(cls.__rewardTemplate, {u'text': backport.text(rBonuses.dyn(rewardType)()),
             u'count': count}))

        return result

    @classmethod
    def __makeQuestsAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)


class EpicSeasonEndFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __template = u'EpicSeasonEndMessage'
    __rewardTemplate = u'epicDefaultRewardReceived'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        resultMessage = MessageData(None, None)
        if message.data and isSynced:
            data = message.data
            rewards = data.get(u'data')
            if rewards is not None:
                description = backport.text(R.strings.system_messages.epicBattles.seasonEnd.text())
                title = backport.text(R.strings.system_messages.epicBattles.seasonEnd.title())
                text = []
                if u'items' in rewards:
                    text.extend(self.__formatItemsStrings(rewards[u'items']))
                formatted = g_settings.msgTemplates.format(self.__template, {u'title': title,
                 u'description': description,
                 u'text': u'<br>'.join(text)})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        callback([resultMessage])
        return

    def __formatItemsStrings(self, items):
        rewardStrings = []
        for itemCD, count in items.iteritems():
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(itemCD)
            if itemTypeID == I_T.crewBook:
                rewardStrings.append(self.__formatCrewBookString(itemCD, count))
            if itemTypeID in (I_T.equipment, I_T.optionalDevice):
                rewardStrings.append(self.__formatRewardChoiceTokenString(itemCD, count, itemTypeID))

        return rewardStrings

    def __formatRewardChoiceTokenString(self, itemCD, count, itemTypeID):
        typeName = ITEM_TYPE_NAMES[itemTypeID]
        item = self.__itemsCache.items.getItemByCD(itemCD)
        textRes = R.strings.system_messages.epicBattles.seasonEnd.rewards.dyn(typeName)()
        text = backport.text(textRes, name=item.userName)
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {u'text': text,
         u'count': count})

    def __formatCrewBookString(self, itemCD, count):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        text = backport.text(R.strings.system_messages.epicBattles.seasonEnd.rewards.crewBook(), name=item.userName)
        return g_settings.htmlTemplates.format(self.__rewardTemplate, {u'text': text,
         u'count': count})


class BattlePassFreePointsUsedFormatter(ServiceChannelFormatter):
    __template = u'BattlePassFreePointsUsedMessage'
    __battlePassController = dependency.descriptor(IBattlePassController)

    def format(self, message, *args):
        resultMessage = MessageData(None, None)
        if message.data:
            data = message.data
            chapterID = data.get(u'chapter')
            pointsDiff = data.get(u'diffPoints')
            if not (chapterID is None or pointsDiff is None):
                header = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.freePointsUsed.header())
                chapterName = backport.text(R.strings.battle_pass.chapter.fullName.quoted.num(chapterID)())
                text = backport.text(R.strings.messenger.serviceChannelMessages.battlePass.freePointsUsed.text(), chapter=text_styles.credits(chapterName), points=pointsDiff)
                formatted = g_settings.msgTemplates.format(self.__template, {u'header': header,
                 u'text': text})
                resultMessage = MessageData(formatted, self._getGuiSettings(message, self.__template))
        return [resultMessage]


class CollectibleVehiclesUnlockedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'UnlockedCollectibleVehiclesMessage'

    def format(self, message, *args):
        data = message.data
        if data:
            nationID = data.get(u'nationID')
            level = data.get(u'level')
            if nationID is not None and nationID < len(NAMES):
                formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'header': backport.text(R.strings.messenger.serviceChannelMessages.vehicleCollector.unlockLevel.header()),
                 u'text': backport.text(R.strings.messenger.serviceChannelMessages.vehicleCollector.unlockLevel.text(), level=int2roman(level), nation=backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase()))})
                return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
        return [MessageData(None, None)]


class TechTreeActionDiscountFormatter(ServiceChannelFormatter):
    __template = u'TechTreeActionDiscountMessage'

    def format(self, message, *args):
        actionName = message.get(u'actionName', None)
        timeLeft = message.get(u'timeLeft', None)
        single = message.get(u'single', True)
        textKey = R.strings.system_messages.techtree.action.text
        if actionName is not None and timeLeft is not None:
            formatted = g_settings.msgTemplates.format(self.__template, {u'header': backport.text(R.strings.system_messages.techtree.action.header(), actionName=actionName),
             u'text': backport.text(textKey() if single else textKey.closest()),
             u'timeLeft': getTillTimeByResource(timeLeft, R.strings.menu.Time.timeLeftShort, useRoundUp=True)})
            return [MessageData(formatted, self._getGuiSettings(message, self.__template))]
        else:
            return [MessageData(None, None)]


class BlueprintsConvertSaleFormatter(ServiceChannelFormatter):
    __templates = {BCSActionState.STARTED: u'BlueprintsConvertSaleStartMessage',
     BCSActionState.PAUSED: u'BlueprintsConvertSalePauseMessage',
     BCSActionState.RESTORE: u'BlueprintsConvertSaleRestoreMessage',
     BCSActionState.END: u'BlueprintsConvertSaleEndMessage'}

    def format(self, message, *args):
        actionName = message.get(u'state', None)
        if actionName is not None and actionName in self.__templates:
            formatted = g_settings.msgTemplates.format(self.__templates[actionName], {u'header': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.header()),
             u'text': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.dyn(actionName.value)()),
             u'button': backport.text(R.strings.messenger.serviceChannelMessages.blueprintsConvertSale.button())})
            return [MessageData(formatted, self._getGuiSettings(message, self.__templates[actionName]))]
        else:
            return [MessageData(None, None)]


class CustomizationProgressFormatter(WaitItemsSyncFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        from gui.customization.shared import checkIsFirstProgressionDecalOnVehicle
        priorityLevel = NotificationPriorityLevel.MEDIUM
        isSynced = yield self._waitForSyncItems()
        if isSynced and message.data:
            messageData = []
            for vehicleCD, items in message.data.iteritems():
                vehicleName = self.itemsCache.items.getItemByCD(vehicleCD).shortUserName if vehicleCD != UNBOUND_VEH_KEY else u''
                isFirst = checkIsFirstProgressionDecalOnVehicle(vehicleCD, items.keys())
                for itemCD, level in items.iteritems():
                    itemName = self.itemsCache.items.getItemByCD(itemCD).userName
                    text = self.__getMessageText(itemName, level, vehicleName)
                    if vehicleName:
                        template = u'ProgressiveItemUpdatedMessage'
                        ctx = {u'text': text}
                    else:
                        template = u'notificationsCenterMessage_1'
                        ctx = {u'topic': u'',
                         u'body': text}
                    data = {u'savedData': {u'itemIntCD': itemCD,
                                    u'vehicleIntCD': vehicleCD,
                                    u'toProjectionDecals': True}}
                    guiSettings = self._getGuiSettings(message, template, priorityLevel=priorityLevel, messageType=message.type)
                    formatted = g_settings.msgTemplates.format(template, ctx, data=data)
                    messageData.append(MessageData(formatted, guiSettings))

                if isFirst:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customizationProgress.editStyleUnlocked(), vehicleName=vehicleName)
                    ctx = {u'text': text}
                    template = u'ProgressiveItemUpdatedMessage'
                    data = {u'savedData': {u'vehicleIntCD': vehicleCD,
                                    u'toStyle': True}}
                    guiSettings = self._getGuiSettings(message, template, priorityLevel=priorityLevel, messageType=message.type)
                    formatted = g_settings.msgTemplates.format(template, ctx, data=data)
                    messageData.append(MessageData(formatted, guiSettings))

            callback(messageData)
        else:
            callback([MessageData(None, None)])
        return

    @staticmethod
    def __getMessageText(itemName, level, vehicleName=u''):
        text = u''
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


class CustomizationProgressionChangedFormatter(WaitItemsSyncFormatter):
    REQUIRED_KEYS = {u'custType',
     u'id',
     u'prevLevel',
     u'actualLevel'}

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        result = [MessageData(None, None)]
        isSynced = yield self._waitForSyncItems()
        if isSynced and message.data and self.REQUIRED_KEYS == set(message.data.keys()):
            data = message.data
            guiItemType, itemUserName = getCustomizationItemData(data[u'id'], data[u'custType'])
            prevLevel = data[u'prevLevel']
            actualLevel = data[u'actualLevel']
            if actualLevel == 0:
                callback(result)
                return
            if actualLevel > prevLevel:
                operation = u'up'
            elif actualLevel < prevLevel:
                operation = u'down'
            else:
                callback(result)
                return
            messageR = R.strings.system_messages.customization.progression.dyn(operation).dyn(guiItemType)
            if messageR.exists():
                messageString = backport.text(messageR(), itemUserName, int2roman(actualLevel))
            else:
                _logger.warning(u"CustomizationProgressionChangedFormatter doesn't have message for custType: %s", guiItemType)
                callback(result)
                return
            formatted = g_settings.msgTemplates.format(u'CustomizationProgressionMessage', ctx={u'message': messageString})
            result = [MessageData(formatted, self._getGuiSettings(message))]
        callback(result)
        return


class PrbEventEnqueueDataFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(u'prbWrongEnqueueDataKick', ctx={})
        return [MessageData(formatted, self._getGuiSettings(message, u'prbWrongEnqueueDataKick'))]


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
            name = composer.getComponentTitle(component.componentId) or u'No name'
            lines.append(u'{} "{}"'.format(viewTypeText, name))

        messageString = u'<br/>'.join(lines)
        ctx = {u'title': title,
         u'message': messageString}
        templateKey = u'DogTagComponentUnlockMessage'
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
        return [MessageData(formatted, self._getGuiSettings(message))]


class DogTagComponentGradingFormatter(DogTagFormatter):
    grades = {0: u'I',
     1: u'II',
     2: u'III',
     3: u'IV',
     4: u'V',
     5: u'VI',
     6: u'VII',
     7: u'VIII',
     8: u'IX',
     9: u'X',
     10: u'XI',
     11: u'XII',
     12: u'XIII',
     13: u'XIV',
     14: u'XV'}

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
            name = composer.getComponentTitle(component.componentId) or u'No name'
            levelUpToText = backport.text(self.serviceMessageSource.gradingMessage.levelUpToText())
            gradingText = self.grades.get(int(grade), u'No Data')
            lines.append(u'{viewTypeText} "{name}" {levelUpToText} {gradingText}'.format(viewTypeText=viewTypeText, name=name, levelUpToText=levelUpToText, gradingText=gradingText))

        messageString = u'<br/>'.join(lines)
        ctx = {u'title': title,
         u'message': messageString}
        templateKey = u'DogTagComponentGradingMessage'
        formatted = g_settings.msgTemplates.format(templateKey, ctx=ctx)
        return [MessageData(formatted, self._getGuiSettings(message))]


class DedicationRewardFormatter(ServiceChannelFormatter):
    _template = u'DedicationRewardMessage'

    @classmethod
    def _getCountOfCustomizations(cls, rewards):
        customizations = rewards.get(u'customizations', [])
        totalCount = 0
        for customizationItem in customizations:
            totalCount += customizationItem[u'value']

        return totalCount

    def format(self, message, *args):
        result = [MessageData(None, None)]
        if message.data:
            data = message.data
            if u'ctx' in data and u'rewards' in data:
                ctx = data[u'ctx']
                rewards = data[u'rewards']
                battleCount = ctx.get(u'reason', 0)
                medalName = _getAchievementsFromQuestData(rewards)
                decalsCount = self._getCountOfCustomizations(rewards)
                if battleCount and medalName and decalsCount:
                    text = backport.text(R.strings.messenger.serviceChannelMessages.dedicationReward.text(), battlesCount=battleCount, medalName=medalName[0], decalsCount=decalsCount)
                    formatted = g_settings.msgTemplates.format(self._template, {u'text': text})
                    result = [MessageData(formatted, self._getGuiSettings(message, self._template))]
        return result


class MapboxStartedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'MapboxStartedMessage'

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE)
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class MapboxEndedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'Mapbox{}Message'
    __REWARDS_LEFT_MSG = u'Ended'
    __NO_REWARDS_LEFT_MSG = u'EndedNoRewards'

    def format(self, message, *args):
        rewards = message.get(u'rewards')
        if rewards is not None:
            template = self.__TEMPLATE.format(self.__REWARDS_LEFT_MSG)
            resultRewards = {}
            mergeRewards(resultRewards, {reward[u'name']:reward[u'value'] for reward in rewards})
            formatted = g_settings.msgTemplates.format(template, {u'header': backport.text(R.strings.messenger.serviceChannelMessages.mapbox.congrats.title()),
             u'text': backport.text(R.strings.messenger.serviceChannelMessages.mapbox.eventEnded.text()),
             u'achieves': QuestAchievesFormatter.formatQuestAchieves(resultRewards, False)})
        else:
            template = self.__TEMPLATE.format(self.__NO_REWARDS_LEFT_MSG)
            formatted = g_settings.msgTemplates.format(template)
        return [MessageData(formatted, self._getGuiSettings(message, template))]


class BattleMattersTokenAward(ServiceChannelFormatter):
    __TEMPLATE = u'BattleMattersTokenAward'

    def format(self, message, *args):
        achievesFormatter = BattleMattersQuestAchievesFormatter()
        achieves = achievesFormatter.formatQuestAchieves(message, asBattleFormatter=False)
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'achieves': achieves})
        settings = self._getGuiSettings(message, self.__TEMPLATE)
        return [MessageData(formatted, settings)]


class WinbackSelectableAward(ServiceChannelFormatter):
    __TEMPLATE = u'WinbackSelectedAward'

    def format(self, message, *args):
        achievesFormatter = WinbackQuestAchievesFormatter()
        achieves = achievesFormatter.formatQuestAchieves(message, asBattleFormatter=False)
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'achieves': achieves})
        settings = self._getGuiSettings(message, self.__TEMPLATE)
        return [MessageData(formatted, settings)]


class MapboxSurveyAvailableFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'MapboxSurveyAvailableMessage'
    __STR_PATH = R.strings.messenger.serviceChannelMessages.mapbox

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            mapName = message.get(u'map')
            header = backport.text(self.__STR_PATH.surveyAvailable.header())
            if mapName in ArenaType.g_geometryNamesToIDs:
                arenaType = ArenaType.g_cache[ArenaType.g_geometryNamesToIDs[mapName]]
                text = backport.text(self.__STR_PATH.surveyAvailable.singleMap(), mapName=arenaType.name)
            else:
                text = backport.text(self.__STR_PATH.surveyAvailable.allMaps())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'header': header,
             u'text': text}, data={u'savedData': mapName})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, messageSubtype=message.get(u'msgType')))]


class MapboxRewardReceivedFormatter(ServiceChannelFormatter):
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __TEMPLATE = u'MapboxRewardReceivedMessage'
    __STR_PATH = R.strings.messenger.serviceChannelMessages.mapbox

    def format(self, message, *args):
        rewards = message.get(u'rewards')
        if rewards is None:
            return [MessageData(None, None)]
        else:
            resultRewards = {}
            textItems = []
            battles = message.get(u'battles')
            if battles is not None:
                textItems.append(backport.text(self.__STR_PATH.progressionStageCompleted(), battles=battles))
            isFinal = message.get(u'isFinal', False) and battles is not None
            if isFinal:
                textItems.append(backport.text(self.__STR_PATH.progressionFinalRewardReceived()))
            else:
                textItems.append(backport.text(self.__STR_PATH.rewardReceived()))
            rewards = {item[u'name']:item[u'value'] for item in formatMapboxRewards(rewards)}
            mergeRewards(resultRewards, rewards)
            textItems.append(LootBoxAchievesFormatter.formatQuestAchieves(resultRewards, False))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'header': backport.text(self.__STR_PATH.congrats.title()),
             u'text': u'<br>'.join(textItems)}, data={u'savedData': {u'rewards': rewards,
                            u'battles': battles}})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, messageSubtype=message.get(u'msgType')))]


class TelecomMergeResultsFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = u'telecomMergeResultsMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        data = message.data
        if data and isSynced:
            debitedVehIDs = data.get(u'debitedVehIDs')
            mergedVehID = data.get(u'mergedVehID')
            crewVehIDs = data.get(u'crewVehIDs')
            creditsCompens = data.get(u'creditsCompens')
            xpCompens = data.get(u'xpCompens')
            goldCompens = data.get(u'goldCompens')
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
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': u'<br>'.join(textItems)})
            callback([MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))])
        else:
            callback([MessageData(None, None)])
        return


class RecertificationResetUsedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'RecertificationResetUsedSysMessage'
    __messageData = {u'blanks': {u'priority': NotificationPriorityLevel.LOW,
                 u'header': R.strings.recertification_form.serviceChannelMessages.Reset.header(),
                 u'currency': R.strings.recertification_form.serviceChannelMessages.currencyBlanks(),
                 u'icon': u'RecertificationIcon'}}

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            data = message.data
            currencyType = data.get(u'currencyType')
            messageData = self.__messageData.get(currencyType, {})
            if not messageData:
                return [MessageData(None, None)]
            textItems = [backport.text(R.strings.recertification_form.serviceChannelMessages.Reset.body()), backport.text(R.strings.recertification_form.serviceChannelMessages.ResetUsed.body(), currency=backport.text(messageData[u'currency']), count=getNiceNumberFormat(data.get(u'count')))]
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'header': backport.text(messageData[u'header']),
             u'text': u'<br>'.join(textItems)}, data={u'icon': messageData[u'icon'],
             u'savedData': data})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, priorityLevel=messageData[u'priority']))]


class RecertificationResetFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'RecertificationInformationSysMessage'

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            text = backport.text(R.strings.recertification_form.serviceChannelMessages.Reset.body())
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class RecertificationAvailabilityFormatter(ServiceChannelFormatter):
    __messageData = {SwitchState.INACTIVE.value: {u'template': u'RecertificationAvailabilityOffSysMessage',
                                  u'header': R.strings.recertification_form.serviceChannelMessages.Availability.error()},
     SwitchState.ENABLED.value: {u'template': u'RecertificationAvailabilityOnSysMessage',
                                 u'header': None}}

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            data = message.data
            state = data.get(u'state')
            messageData = self.__messageData.get(state, {})
            if not messageData:
                return [MessageData(None, None)]
            text = backport.text(R.strings.recertification_form.serviceChannelMessages.Availability.dyn(state)())
            header = messageData[u'header']
            template = messageData[u'template']
            formatted = g_settings.msgTemplates.format(template, {u'header': backport.text(header) if header else u'',
             u'text': text}, data={u'savedData': state})
            return [MessageData(formatted, self._getGuiSettings(message, template))]


class RecertificationFinancialFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'RecertificationFinancialSysMessage'
    __messageData = {u'buy': u'loss',
     u'sell': u'profit'}

    def format(self, message, *args):
        if not message:
            return [MessageData(None, None)]
        else:
            data = message.data
            operationType = data.get(u'operationType')
            operationState = self.__messageData.get(operationType, u'')
            if not operationState:
                return [MessageData(None, None)]
            header = backport.text(R.strings.recertification_form.serviceChannelMessages.Financial.dyn(operationType)())
            state = backport.text(R.strings.recertification_form.serviceChannelMessages.Financial.dyn(operationState)())
            blanksCount = data.get(u'blanksCount')
            style = text_styles.credits if operationType == u'sell' else str
            creditsCount = style(getNiceNumberFormat(data.get(u'creditsCount')))
            text = backport.text(R.strings.recertification_form.serviceChannelMessages.Financial.text(), blanksCount=blanksCount, state=state, creditsCount=creditsCount)
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {u'header': header,
             u'text': text}, data={u'savedData': data})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class ResourceWellOperationFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'ResourceWellOperationMessage'
    __RESOURCE_WELL_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __BULLET = u'\u2022 '
    __NONE_NATION_NAME = u'intelligence'
    __NO_NATION_INDEX = 0
    __NATIONS_ORDER = {name:idx for idx, name in enumerate(GUI_NATIONS, 1)}
    __NATIONS_ORDER[__NONE_NATION_NAME] = __NO_NATION_INDEX
    __CURRENCY_ORDER = {name:idx for idx, name in enumerate(Currency.GUI_ALL + (CURRENCIES_CONSTANTS.FREE_XP,))}
    __FULL_PROGRESS = 100.0
    __resourceWell = dependency.descriptor(IResourceWellController)

    def format(self, message, *args):
        data = message.data
        if u'type' not in data or u'data' not in data:
            return [MessageData(None, None)]
        else:
            operationType = data[u'type']
            title = backport.text(self.__RESOURCE_WELL_MESSAGES.dyn(operationType).title())
            text = backport.text(self.__RESOURCE_WELL_MESSAGES.dyn(operationType).text())
            resources = self.__formatResources(data[u'data'])
            if not resources:
                return [MessageData(None, None)]
            additionalText = u''
            points = data.get(u'points')
            if points is not None and operationType == u'put':
                progress = self.__FULL_PROGRESS / (self.__resourceWell.getMaxPoints() or self.__FULL_PROGRESS) * points
                additionalText = backport.text(self.__RESOURCE_WELL_MESSAGES.progress(), progress=progress) + backport.text(R.strings.common.common.percent())
            ctx = {u'resources': self.__BULLET + resources,
             u'title': title,
             u'text': text,
             u'additionalText': additionalText}
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx=ctx)
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __formatResources(self, resources):
        resourceStrings = []
        if ResourceType.CURRENCY.value in resources:
            resourceStrings.extend(self.__formatCurrencies(resources[ResourceType.CURRENCY.value]))
        if ResourceType.BLUEPRINTS.value in resources:
            resourceStrings.append(self.__formatBlueprints(resources[ResourceType.BLUEPRINTS.value]))
        return (backport.text(self.__RESOURCE_WELL_MESSAGES.breakLine()) + self.__BULLET).join(resourceStrings)

    def __formatBlueprints(self, blueprintResources):
        blueprints = []
        for fragmentCD, count in blueprintResources.iteritems():
            fragmentType = getFragmentType(fragmentCD)
            if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
                blueprints.append((self.__NONE_NATION_NAME, count))
            if fragmentType == BlueprintTypes.NATIONAL:
                blueprints.append((nations.MAP.get(getFragmentNationID(fragmentCD), nations.NONE_INDEX), count))

        blueprints.sort(cmp=lambda a, b: cmp(self.__NATIONS_ORDER.get(a), self.__NATIONS_ORDER.get(b)), key=lambda x: x[0])
        blueprintStrings = []
        for nation, count in blueprints:
            nationStr = backport.text(R.strings.blueprints.nations.dyn(nation, self.__RESOURCE_WELL_MESSAGES.intelligence)())
            blueprintStrings.append(nationStr + self.__formatBlueprintCount(count))

        return backport.text(self.__RESOURCE_WELL_MESSAGES.blueprints()) + u', '.join(blueprintStrings)

    def __formatCurrencies(self, currencyResources):
        currencies = sorted(currencyResources.items(), key=lambda x: x[0], cmp=lambda a, b: cmp(self.__CURRENCY_ORDER.get(a), self.__CURRENCY_ORDER.get(b)))
        return [ backport.text(self.__RESOURCE_WELL_MESSAGES.dyn(name)(), count=self.__formatCurrencyCount(name, count)) for name, count in currencies ]

    def __formatCurrencyCount(self, currencyName, count):
        style = getStyle(currencyName) if currencyName in Currency.ALL else text_styles.crystal
        return style(backport.getIntegralFormat(abs(count)))

    def __formatBlueprintCount(self, count):
        countStr = backport.getIntegralFormat(abs(count))
        return text_styles.crystal(backport.text(self.__RESOURCE_WELL_MESSAGES.blueprintCount(), count=countStr))


class ResourceWellRewardFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = u'ResourceWellRewardReceivedMessage'
    __RESOURCE_WELL_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __resourceWell = dependency.descriptor(IResourceWellController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            reward = message.data.get(u'reward')
            if reward is None:
                callback([MessageData(None, None)])
            callback([self.__getMainMessage(message), self.__getAdditionalMessage(message)])
        else:
            callback([MessageData(None, None)])
        return

    def __getMainMessage(self, message):
        from tutorial.control.game_vars import getVehicleByIntCD
        serialNumber = message.data.get(u'serialNumber')
        vehicle = getVehicleByIntCD(self.__resourceWell.getRewardVehicle()).userName
        additionalText = u''
        if serialNumber:
            title = backport.text(self.__RESOURCE_WELL_MESSAGES.topReward.title(), vehicle=vehicle)
            text = backport.text(self.__RESOURCE_WELL_MESSAGES.topReward.text(), vehicle=text_styles.crystal(vehicle))
            additionalText = backport.text(self.__RESOURCE_WELL_MESSAGES.topReward.additionalText(), serialNumber=serialNumber)
        else:
            title = backport.text(self.__RESOURCE_WELL_MESSAGES.regularReward.title(), vehicle=vehicle)
            text = backport.text(self.__RESOURCE_WELL_MESSAGES.regularReward.text(), vehicle=text_styles.crystal(vehicle))
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={u'title': title,
         u'text': text,
         u'additionalText': additionalText})
        return MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))

    def __getAdditionalMessage(self, message):
        rewards = self.__resourceWell.getRewards()
        reward = rewards.get(message.data[u'reward'])
        if reward is None:
            return MessageData(None, None)
        else:
            slots = reward.bonus.get(u'slots')
            if not slots:
                return MessageData(None, None)
            text = g_settings.htmlTemplates.format(u'slotsAccruedInvoiceReceived', {u'amount': backport.getIntegralFormat(slots)})
            at = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime))
            formatted = g_settings.msgTemplates.format(u'resourceWellInvoiceReceived', ctx={u'at': at,
             u'text': text})
            return MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))


class ResourceWellNoVehiclesFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = u'ResourceWellNoVehiclesMessage'
    __RETURN_TEMPLATE = u'ResourceWellNoVehiclesWithReturnMessage'
    __RESOURCE_WELL_MESSAGES = R.strings.messenger.serviceChannelMessages.resourceWell
    __itemsCache = dependency.descriptor(IItemsCache)
    __resourceWell = dependency.descriptor(IResourceWellController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            from tutorial.control.game_vars import getVehicleByIntCD
            isSerial = message.data.get(u'isSerial')
            balance = self.__itemsCache.items.resourceWell.getBalance()
            title = backport.text(self.__RESOURCE_WELL_MESSAGES.noVehicles.title())
            template = self.__TEMPLATE
            if isSerial:
                template = self.__RETURN_TEMPLATE
                vehicle = getVehicleByIntCD(self.__resourceWell.getRewardVehicle()).userName
                text = backport.text(self.__RESOURCE_WELL_MESSAGES.noSerialVehicles.text(), vehicle=vehicle)
            elif balance:
                text = backport.text(self.__RESOURCE_WELL_MESSAGES.noVehiclesWithReturn.text())
            else:
                text = backport.text(self.__RESOURCE_WELL_MESSAGES.noVehicles.text())
            formatted = g_settings.msgTemplates.format(template, ctx={u'title': title,
             u'text': text})
            callback([MessageData(formatted, self._getGuiSettings(message, template))])
        else:
            callback([MessageData(None, None)])
        return


class Customization2DProgressionChangedFormatter(WaitItemsSyncFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    REQUIRED_KEYS = {u'custType', u'id', u'2dProgression'}

    @adisp_async
    @adisp_process
    def format(self, message, callback, *args):
        result = [MessageData(None, None)]
        if not message:
            callback(result)
        isSynced = yield self._waitForSyncItems()
        data = message.data
        if isSynced and data and self.REQUIRED_KEYS == set(data.keys()):
            style = getCustomizationItem(data[u'id'], data[u'custType'])
            progression = data[u'2dProgression']
            totalItems = deque()
            rProgression = R.strings.messenger.serviceChannelMessages.progression2d
            for group, levels in progression:
                for level in list(OrderedDict.fromkeys(levels)):
                    itemsForLevel = style.descriptor.questsProgression.getUnlocks(group, level)[-1]
                    for itemType, itemIDs in itemsForLevel.iteritems():
                        for itemID in itemIDs:
                            custItem = getCustomizationItem(itemID, CustomizationTypeNames[itemType])
                            _, itemLevel = custItem.getQuestsProgressionInfo()
                            if itemType == CustomizationType.CAMOUFLAGE:
                                totalItems.appendleft((custItem, itemLevel))
                            totalItems.append((custItem, itemLevel))

            title = backport.text(rProgression.title(), name=style.userName)
            itemsStrList = [ backport.text(rProgression.item(), typeName=backport.text(rProgression.dyn(custItem.itemTypeName)()), name=custItem.userName, level=self.__getLevelText(level)) for custItem, level in islice(totalItems, 0, 3) ]
            if len(totalItems) > len(itemsStrList):
                itemsStrList += [backport.text(rProgression.itemCount(), count=len(totalItems) - len(itemsStrList))]
            itemsStr = u'<br/>'.join(itemsStrList)
            formatted = g_settings.msgTemplates.format(u'Customization2DProgressionMessage', ctx={u'title': title,
             u'itemsList': itemsStr}, data={u'savedData': {u'toStyle': True,
                            u'styleID': data[u'id']}})
            result = [MessageData(formatted, self._getGuiSettings(message, messageType=message.type))]
        callback(result)
        return

    def __getLevelText(self, level):
        return u'' if level < 1 else backport.text(R.strings.messenger.serviceChannelMessages.progression2d.level(), level=int2roman(level))


class FairplayFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'InformationHeaderSysMessage'

    def format(self, message, *args):
        data = message.data
        if not data:
            return [MessageData(None, None)]
        else:
            isStarted = message.data.get(u'isStarted', False)
            reason = message.data.get(u'reason', u'')
            extraData = message.data.get(u'extraData', {})
            resrType = message.data.get(u'restrType', 0)
            if isStarted:
                header, text = self.__getBanStartedMessage(reason, extraData, resrType)
            else:
                header, text = self.__getBanStoppedMessage(reason, extraData, resrType)
            if not header and not text:
                return [MessageData(None, None)]
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={u'text': text,
             u'header': header})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    @staticmethod
    def __isComp7DeserterBan(reason, extraData):
        return ARENA_BONUS_TYPE.COMP7 in extraData.get(u'bonusTypes', []) and FAIRPLAY_VIOLATIONS.COMP7_DESERTER in reason

    def __getBanStartedMessage(self, reason, extraData, resrType):
        header, text = (None, None)
        if resrType == RESTRICTION_TYPE.ARENA_BAN:
            if self.__isComp7DeserterBan(reason, extraData):
                penalty = extraData.get(u'penalty', 0)
                isQualification = extraData.get(u'qualActive', False)
                header = backport.text(R.strings.comp7.battleResult.message.header.deserter())
                text = backport.text(R.strings.comp7.battleResult.message.deserterQualification() if isQualification else R.strings.comp7.battleResult.message.deserter(), penalty=penalty)
        return (header, text)

    def __getBanStoppedMessage(self, reason, extraData, resrType):
        header, text = (None, None)
        if resrType == RESTRICTION_TYPE.ARENA_BAN:
            if self.__isComp7DeserterBan(reason, extraData):
                header = backport.text(R.strings.comp7.system_messages.temporaryBan.end.title())
                text = backport.text(R.strings.comp7.system_messages.temporaryBan.end.body())
        return (header, text)


class IntegratedAuctionResultFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'IntegratedAuctionResultSysMessage'
    __AUCTION_MESSAGES = R.strings.messenger.serviceChannelMessages.integratedAuction
    __CURRENCY_TO_STYLE = {Currency.CREDITS: text_styles.creditsTitle,
     Currency.GOLD: text_styles.goldTitle,
     Currency.CRYSTAL: text_styles.crystalTitle,
     CURRENCIES_CONSTANTS.FREE_XP: text_styles.expTitle}
    __FREE_XP = u'free_xp'
    __WGM_CURRENCY_TO_NAME = {__FREE_XP: CURRENCIES_CONSTANTS.FREE_XP}

    def format(self, message, *args):
        messageData = message.get(u'data', {})
        if u'currency' not in messageData or u'amount' not in messageData or u'result' not in messageData:
            return [MessageData(None, None)]
        else:
            headerResId, textResId = self.__getResIds(messageData[u'result'], messageData[u'amount'])
            headerStr = backport.text(headerResId)
            currencyStr = self.__getCurrencyString(str(messageData[u'currency']), int(messageData[u'amount']))
            header = text_styles.concatStylesWithSpace(headerStr, currencyStr)
            text = backport.text(textResId)
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={u'header': header,
             u'text': text})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]

    def __getResIds(self, result, amount):
        if result == u'win':
            if amount == 0:
                return (self.__AUCTION_MESSAGES.winRate.header(), self.__AUCTION_MESSAGES.rateEqual.text())
            return (self.__AUCTION_MESSAGES.winRate.header(), self.__AUCTION_MESSAGES.winRate.text())
        elif result == u'lost':
            return (self.__AUCTION_MESSAGES.lostRate.header(), self.__AUCTION_MESSAGES.lostRate.text())
        else:
            _logger.warning(u'Unsupported auction result type = %s', result)
            return (R.invalid(), R.invalid())

    def __getCurrencyString(self, currency, amount):
        currencyName = self.__WGM_CURRENCY_TO_NAME.get(currency, currency)
        icon = getattr(icons, currencyName + u'ExtraBig')()
        amountStr = self.__getCurrencyStyle(currency)(getBWFormatter(currency)(amount))
        return text_styles.concatStylesToSingleLine(amountStr, icon)

    def __getCurrencyStyle(self, currencyCode):
        currencyName = self.__WGM_CURRENCY_TO_NAME.get(currencyCode, currencyCode)
        return self.__CURRENCY_TO_STYLE.get(currencyName, getStyle(currencyName))


class PersonalReservesHaveBeenConvertedFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'PersonalReservesHaveBeenConverted'

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE)
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class CollectionsItemsFormatter(ServiceChannelFormatter):
    __TEMPLATE = u'CollectionItemsSysMessage'
    __collections = dependency.descriptor(ICollectionsSystemController)

    def format(self, message, *args):
        data = message.data
        if not (data and self.__collections.isEnabled()):
            return [MessageData(None, None)]
        else:
            from gui.collection.collections_helpers import getCollectionFullFeatureName
            messages = R.strings.collections.notifications
            collectionID = data[u'collectionId']
            collection = self.__collections.getCollection(collectionID)
            title = backport.text(messages.title.collectionName(), feature=getCollectionFullFeatureName(collection))
            rewards = data[u'items'] if u'items' in data else data[u'reward']
            text = backport.text(messages.newItemsReceived.text(), items=CollectionsFormatter.formatQuestAchieves(rewards, False))
            formatted = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={u'title': title,
             u'text': text}, data={u'savedData': {u'collectionId': collectionID}})
            return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]


class CollectionsRewardFormatter(ServiceChannelFormatter):
    __MESSAGES = R.strings.collections.notifications
    __ITEMS_TEMPLATE = u'CollectionItemsSysMessage'
    __REWARD_TEMPLATE = u'CollectionRewardsSysMessage'
    __collections = dependency.descriptor(ICollectionsSystemController)

    def format(self, message, *args):
        data = message.data
        if not (data and self.__collections.isEnabled()):
            return [MessageData(None, None)]
        else:
            collectionID = data[u'collectionId']
            collection = self.__collections.getCollection(collectionID)
            isFinal = data[u'requiredCount'] == self.__collections.getMaxProgressItemCount(collectionID)
            result = [self.__makeMessageData(collection, isFinal, message)]
            if isFinal:
                result.append(self.__makeFinalMessageData(collection, message))
            return result

    def __makeMessageData(self, collection, isFinal, message):
        from gui.collection.collections_helpers import getCollectionFullFeatureName
        title = backport.text(self.__MESSAGES.title.collectionName(), feature=getCollectionFullFeatureName(collection))
        text = backport.text(self.__MESSAGES.newRewardsReceived.text(), items=CollectionsFormatter.formatQuestAchieves(deepcopy(message.data[u'reward']), False))
        template = self.__REWARD_TEMPLATE
        formatted = g_settings.msgTemplates.format(template, ctx={u'title': title,
         u'text': text}, data={u'savedData': {u'collectionId': collection.collectionId,
                        u'bonuses': [message.data[u'reward']],
                        u'isFinal': isFinal}})
        return MessageData(formatted, self._getGuiSettings(message, template, messageType=SYS_MESSAGE_TYPE.collectionsReward.index()))

    def __makeFinalMessageData(self, collection, message):
        from gui.collection.collections_helpers import getCollectionFullFeatureName
        text = backport.text(self.__MESSAGES.finalReceived.text(), feature=getCollectionFullFeatureName(collection))
        formatted = g_settings.msgTemplates.format(self.__ITEMS_TEMPLATE, ctx={u'title': backport.text(self.__MESSAGES.title.congratulation()),
         u'text': text}, data={u'savedData': {u'collectionId': collection.collectionId}})
        return MessageData(formatted, self._getGuiSettings(message, self.__ITEMS_TEMPLATE, messageType=SYS_MESSAGE_TYPE.collectionsItems.index()))


class AchievementsSMFormatter(ClientSysMessageFormatter):
    __ACHIEVEMENTS_MESSAGES = R.strings.achievements_page.notifications
    __ACHIEVEMENTS_IMAGES = R.images.gui.maps.icons.achievements

    def format(self, message, *args):
        messageType = message.get(u'type')
        if messageType is None:
            return
        else:
            rank = message.get(u'rank')
            subRank = message.get(u'subRank')
            template = self.__getTemplate(messageType)
            formatted = g_settings.msgTemplates.format(template, self.__getCtx(messageType, rank, subRank), data={u'linkageData': self.__getSavedDate(messageType, rank, subRank)})
            guiSettings = self._getGuiSettings(message, template)
            return [MessageData(formatted, guiSettings)]

    def __getSavedDate(self, type, rank=None, subRank=None):
        if type == Achievements20SystemMessages.RATING_UPGRADE:
            return {u'icon': backport.image(self.__ACHIEVEMENTS_IMAGES.messenger.rating.dyn(u'rating_{}_{}'.format(rank, subRank))()),
             u'type': u'rating'}
        if type == Achievements20SystemMessages.RATING_COMPLETE:
            return {u'icon': backport.image(self.__ACHIEVEMENTS_IMAGES.messenger.rating.dyn(u'rating_{}_{}'.format(rank, subRank))()),
             u'type': u'rating'}
        return {u'icon': backport.image(self.__ACHIEVEMENTS_IMAGES.messenger.editing()),
         u'type': u'editing'} if type == Achievements20SystemMessages.EDITING_AVAILABLE else None

    def __getCtx(self, type, rank=None, subRank=None):
        if type == Achievements20SystemMessages.RATING_UPGRADE:
            return {u'title': backport.text(self.__ACHIEVEMENTS_MESSAGES.ratingUp.title()),
             u'text': backport.text(self.__ACHIEVEMENTS_MESSAGES.ratingUp.text(), level=self.__getLevel(rank, subRank))}
        if type == Achievements20SystemMessages.RATING_COMPLETE:
            return {u'title': backport.text(self.__ACHIEVEMENTS_MESSAGES.ratingCalculated.title()),
             u'text': backport.text(self.__ACHIEVEMENTS_MESSAGES.ratingCalculated.text(), level=self.__getLevel(rank, subRank))}
        return {u'title': backport.text(self.__ACHIEVEMENTS_MESSAGES.editingEnabled.title()),
         u'button': backport.text(self.__ACHIEVEMENTS_MESSAGES.editingEnabled.button())} if type == Achievements20SystemMessages.EDITING_AVAILABLE else None

    def __getTemplate(self, type):
        if type == Achievements20SystemMessages.RATING_UPGRADE or type == Achievements20SystemMessages.RATING_COMPLETE:
            return u'achievementRating'
        if type == Achievements20SystemMessages.RATING_DOWNGRADE:
            return u'achievementRatingDowngrade'
        if type == Achievements20SystemMessages.EDITING_AVAILABLE:
            return u'achievementEditing'
        if type == Achievements20SystemMessages.FIRST_ENTRY:
            return u'achievementFirstEntry'
        return u'achievementFirstEntryWithOutWTR' if type == Achievements20SystemMessages.FIRST_ENTRY_WITHOUT_WTR else None

    def __getLevel(self, rank=None, subRank=None):
        return backport.text(R.strings.achievements_page.tooltips.WTR.rating.levels.dyn(u'level_{}'.format(rank))(), level=int2roman(subRank))
