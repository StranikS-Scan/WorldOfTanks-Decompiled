# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Stats.py
import cPickle
import logging
from functools import partial, wraps
import AccountCommands
import constants
import items
from account_helpers.premium_info import PremiumInfo
from debug_utils import LOG_DEBUG_DEV, LOG_WARNING, LOG_ERROR
from helpers import time_utils
from piggy_bank_common.settings_constants import PIGGY_BANK_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from items import vehicles
from gui.shared.money import Currency
_logger = logging.getLogger(__name__)
_VEHICLE = items.ITEM_TYPE_INDICES['vehicle']
_CHASSIS = items.ITEM_TYPE_INDICES['vehicleChassis']
_TURRET = items.ITEM_TYPE_INDICES['vehicleTurret']
_GUN = items.ITEM_TYPE_INDICES['vehicleGun']
_ENGINE = items.ITEM_TYPE_INDICES['vehicleEngine']
_FUEL_TANK = items.ITEM_TYPE_INDICES['vehicleFuelTank']
_RADIO = items.ITEM_TYPE_INDICES['vehicleRadio']
_TANKMAN = items.ITEM_TYPE_INDICES['tankman']
_OPTIONALDEVICE = items.ITEM_TYPE_INDICES['optionalDevice']
_SHELL = items.ITEM_TYPE_INDICES['shell']
_EQUIPMENT = items.ITEM_TYPE_INDICES['equipment']
_SIMPLE_VALUE_STATS = ('fortResource', 'slots', 'berths', 'freeXP', 'dossier', 'clanInfo', 'accOnline', 'accOffline', 'freeTMenLeft', 'freeVehiclesLeft', 'vehicleSellsLeft', 'captchaTriesLeft', 'hasFinPassword', 'finPswdAttemptsLeft', 'tkillIsSuspected', 'denunciationsLeft', 'battlesTillCaptcha', 'dailyPlayHours', 'playLimits', 'applyAdditionalXPCount', 'applyAdditionalWoTPlusXPCount') + Currency.ALL
_DICT_STATS = ('vehTypeXP', 'vehTypeLocks', 'restrictions', 'globalVehicleLocks', 'dummySessionStats', 'maxResearchedLevelByNation', 'weeklyVehicleCrystals')
_GROWING_SET_STATS = ('unlocks', 'eliteVehicles', 'multipliedXPVehs', 'multipliedRankedBattlesVehs')
_ACCOUNT_STATS = ('clanDBID', 'attrs', 'premiumExpiryTime', 'autoBanTime', 'globalRating')
_CACHE_STATS = ('isFinPswdVerified', 'mayConsumeWalletResources', 'oldVehInvIDs', 'isSsrPlayEnabled', 'isEmergencyModeEnabled')
_CACHE_DICT_STATS = ('SPA', 'entitlements', 'dynamicCurrencies', 'comp7')
_PREFERRED_MAPS_KEY = 'preferredMaps'
_ADDITIONAL_XP_CACHE_KEY = '_additionalXPCache'
_LIMITED_UI = 'limitedUi'
_AB_FEATURE_TEST = 'abFeatureTest'

def _checkIfNonPlayer(*args):

    def _decorator(func):

        @wraps(func)
        def _wrapper(self, *func_args, **func_kwargs):
            if self.ignore:
                callback = func_kwargs.get('callback')
                if callback is not None:
                    callback(AccountCommands.RES_NON_PLAYER, *args)
                return
            else:
                return func(self, *func_args, **func_kwargs)

        return _wrapper

    return _decorator


def _get_callback_proxy(callback=None):
    return None if callback is None else (lambda requestID, resultID, errorStr, ext=None: callback(resultID))


class Stats(object):

    def __init__(self, syncData, commandsProxy):
        self.__account = None
        self.__syncData = syncData
        self.__commandsProxy = commandsProxy
        self.__cache = {}
        self.__ignore = True
        return

    @property
    def ignore(self):
        return self.__ignore

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        cache = self.__cache
        statsDiff = diff.get('stats', None)
        if statsDiff is not None:
            for stat in _SIMPLE_VALUE_STATS:
                if stat in statsDiff:
                    cache[stat] = statsDiff[stat]

            for stat in _DICT_STATS:
                stat_r = (stat, '_r')
                if stat_r in statsDiff:
                    cache[stat] = statsDiff[stat_r]
                if stat in statsDiff:
                    synchronizeDicts(statsDiff[stat], cache.setdefault(stat, dict()))

            for stat in _GROWING_SET_STATS:
                stat_r = (stat, '_r')
                if stat_r in statsDiff:
                    cache[stat] = statsDiff[stat_r]
                if stat in statsDiff:
                    cache.setdefault(stat, set()).update(statsDiff[stat])

        accountDiff = diff.get('account', None)
        if accountDiff is not None:
            for stat in _ACCOUNT_STATS:
                if stat in accountDiff:
                    cache[stat] = accountDiff[stat]

            if _ADDITIONAL_XP_CACHE_KEY in accountDiff:
                synchronizeDicts(accountDiff[_ADDITIONAL_XP_CACHE_KEY], cache.setdefault(_ADDITIONAL_XP_CACHE_KEY, {}))
        if cache.get('premiumInfo') is None:
            cache['premiumInfo'] = PremiumInfo()
        premiumDiff = diff.get('premium')
        if premiumDiff is not None:
            cache['premiumInfo'].update(premiumDiff)
        economicsDiff = diff.get('economics', None)
        if economicsDiff is not None:
            for stat in ('unlocks', 'eliteVehicles'):
                if stat in economicsDiff:
                    cache.setdefault(stat, set()).update(economicsDiff[stat])
                    cache.setdefault(('initial', stat), set()).update(economicsDiff[stat])

        cacheDiff = diff.get('cache', None)
        if cacheDiff is not None:
            for stat in _CACHE_STATS:
                if stat in cacheDiff:
                    LOG_DEBUG_DEV('CACHE stat change', stat, cacheDiff[stat])
                    cache[stat] = cacheDiff[stat]

            for stat in _CACHE_DICT_STATS:
                statDiff = cacheDiff.get(stat, None)
                if statDiff:
                    synchronizeDicts(statDiff, cache.setdefault(stat, dict()))

        piggyBankDiff = diff.get(PIGGY_BANK_PDATA_KEY, None)
        if piggyBankDiff is not None:
            synchronizeDicts(piggyBankDiff, cache.setdefault(PIGGY_BANK_PDATA_KEY, dict()))
        if _PREFERRED_MAPS_KEY in diff:
            synchronizeDicts(diff[_PREFERRED_MAPS_KEY], cache.setdefault(_PREFERRED_MAPS_KEY, {}))
        if _LIMITED_UI in diff:
            synchronizeDicts(diff[_LIMITED_UI], cache.setdefault(_LIMITED_UI, {}))
        if _AB_FEATURE_TEST in diff:
            synchronizeDicts(diff[_AB_FEATURE_TEST], cache.setdefault(_AB_FEATURE_TEST, {}))
        return

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def get(self, statName, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetResponse, statName, callback))
            return

    def unlock(self, vehTypeCompDescr, unlockIdx, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_UNLOCK, vehTypeCompDescr, unlockIdx, 0, proxy)
            return

    def setCurrentVehicle(self, vehInvID, callback=None):
        LOG_WARNING('Deprecated. setCurrentVehicle')

    def exchange(self, gold, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.getExchangeRate(partial(self.__exchange_onGetRate, gold, callback))
            return

    def convertToFreeXP(self, vehTypeCompDescrs, xp, callback=None, useDiscount=0):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.getFreeXPConversion(partial(self.__convertToFreeXP_onGetParameters, vehTypeCompDescrs, xp, callback, useDiscount))
            return

    def upgradeToPremium(self, days, arenaUniqueID, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            self.__account.shop.getPremiumCost(partial(self.__premium_onGetPremCost, days, arenaUniqueID, callback))
            return

    def buySlot(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__slot_onShopSynced, callback))
            return

    def buyBerths(self, countPacksBerths, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__berths_onShopSynced, countPacksBerths, callback))
            return

    def setMapsBlackList(self, selectedMaps, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            self.__account._doCmdIntArr(AccountCommands.CMD_SET_MAPS_BLACK_LIST, selectedMaps, None if callback is None else (lambda reqID, resID, errorStr, ext={}: callback(resID, errorStr, ext)))
            return

    def setMoney(self, credit, gold=0, freeXP=0, crystal=0, eventCoin=0, bpcoin=0, equipCoin=0, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_SET_MONEY, [credit,
             gold,
             freeXP,
             crystal,
             eventCoin,
             bpcoin,
             equipCoin], proxy)
            return

    def setPremium(self, premType=constants.PREMIUM_TYPE.PLUS, seconds=time_utils.ONE_DAY, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_SET_PREMIUM, [premType, seconds], proxy)
            return

    def addExperience(self, vehTypeName, xp, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName(vehTypeName))
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_ADD_XP, vehTypeCompDescr, xp, 0, proxy)
            return

    def setDossierField(self, path, value, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdIntStr(AccountCommands.CMD_SET_DOSSIER_FIELD, value, path, proxy)
        return

    def addTokens(self, token, tokenCount=1, limit=0, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt2Str(AccountCommands.CMD_ADD_TOKENS, tokenCount, limit, token, proxy)
        return

    def drawTokens(self, token, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdStr(AccountCommands.CMD_DRAW_TOKENS, token, proxy)
        return

    def unlockAll(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_UNLOCK_ALL, 0, 0, 0, proxy)
            return

    def unlockVPPTree(self, vehTypeCDs, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_VPP_UNLOCK_TREE, vehTypeCDs, proxy)
            return

    def setRankedInfo(self, data, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            data = cPickle.dumps(data)
            self.__account._doCmdStr(AccountCommands.CMD_SET_RANKED_INFO, data, proxy)
            return

    def addFreeAwardLists(self, count, season=1, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_ADD_FREE_AWARD_LISTS, [count, season], proxy)
            return

    def drawFreeAwardLists(self, count, season=1, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_DRAW_FREE_AWARD_LISTS, [count, season], proxy)
            return

    def completePersonalMission(self, questID, withAdditional=False, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_COMPLETE_PERSONAL_MISSION, [questID, int(withAdditional)], proxy)
            return

    def completeQuests(self, questIDs, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdStrArr(AccountCommands.CMD_COMPLETE_QUESTS_DEV, questIDs, proxy)
            return

    def rerollDailyQuest(self, token, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdStr(AccountCommands.CMD_REROLL_DAILY_QUEST, token, proxy)
            return

    def rerollDailyQuestDev(self, level, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdStr(AccountCommands.CMD_REROLL_DAILY_QUEST_DEV, level, proxy)
            return

    def resetRerollTimeout(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_RESET_REROLL_TIMEOUT, 0, 0, 0, proxy)
            return

    def completeDailyQuest(self, token, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdStr(AccountCommands.CMD_COMPLETE_DAILY_QUEST, token, proxy)
            return

    def setEpicRewardTokens(self, count, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_SET_EPIC_REWARD_TOKENS, count, 0, 0, proxy)
            return

    def resetBonusQuest(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_RESET_BONUS_QUEST, 0, 0, 0, proxy)
            return

    @_checkIfNonPlayer()
    def changeBRPoints(self, points, ignoreUnburnableTitles=False, callback=None):
        self.__account._doCmdInt3(AccountCommands.CMD_CHANGE_BR_POINTS, points, int(ignoreUnburnableTitles), 0, _get_callback_proxy(callback))

    @_checkIfNonPlayer()
    def updateVehiclePrestige(self, vehCD=46849, points=10, callback=None):
        if not isinstance(points, int):
            LOG_ERROR('Wrong type of points.')
            return
        elif self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0)
            return
        else:

            def response(code, errStr='', ctx=None):
                if code >= 0:
                    _logger.info('Server success response: code=%r, error=%r, ctx=%r', code, errStr, ctx)
                    return
                _logger.warning('Server fail response: code=%r, error=%r, ctx=%r', code, errStr, ctx)

            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = lambda requestID, resultID, errorStr, ext={}: response(resultID, errorStr, ext)
            self.__commandsProxy.perform(AccountCommands.CMD_RECOMPUTE_PRESTIGE_POINTS, vehCD, points, proxy)
            return

    def __onGetResponse(self, statName, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(statName, None))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __exchange_onGetRate(self, gold, callback, resultID, exchRate, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        elif exchRate is None:
            LOG_ERROR('Result of the getExchangeRate request is None')
            if callback is not None:
                callback(AccountCommands.RES_FAILURE)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_EXCHANGE, shopRev, gold, 0, proxy)
            return

    def __convertToFreeXP_onGetParameters(self, vehTypeCompDescrs, xp, callback, useDiscount, resultID, freeXPConversion, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        elif freeXPConversion is None:
            LOG_ERROR('Result of the getFreeXPConversion request is None')
            if callback is not None:
                callback(AccountCommands.RES_FAILURE)
            return
        else:
            arr = [shopRev, xp, useDiscount] + list(vehTypeCompDescrs)
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_FREE_XP_CONV, arr, proxy)
            return

    def __premium_onGetPremCost(self, days, arenaUniqueID, callback, resultID, premCost, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        elif premCost is None:
            LOG_ERROR('Result of the getPremiumCost request is None')
            if callback is not None:
                callback(AccountCommands.RES_FAILURE, None)
            return
        else:
            gold = premCost.get(days, None)
            if gold is None:
                LOG_ERROR('Wrong days number')
                if callback is not None:
                    callback(AccountCommands.RES_WRONG_ARGS, None)
                return
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_PREMIUM, shopRev, days, arenaUniqueID, proxy)
            return

    def __slot_onShopSynced(self, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_BUY_SLOT, shopRev, 0, 0, proxy)
            return

    def __berths_onShopSynced(self, countPacksBerths, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_BUY_BERTHS, shopRev, countPacksBerths, 0, proxy)
            return
