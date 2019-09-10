# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/StatsRequester.py
from collections import namedtuple
import BigWorld
from account_helpers.premium_info import PremiumInfo
from adisp import async
from gui.shared.money import Money, Currency
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import time_utils, dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils.requesters import IStatsRequester
from nation_change.nation_change_helpers import NationalGroupDataAccumulator
_ADDITIONAL_XP_DATA_KEY = '_additionalXPCache'
_ControllableXPData = namedtuple('_ControllableXPData', ('vehicleID', 'bonusType', 'extraXP', 'extraFreeXP', 'extraTmenXP', 'isXPToTMan'))

class StatsRequester(AbstractSyncDataRequester, IStatsRequester):
    wallet = dependency.descriptor(IWalletController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @property
    def mayConsumeWalletResources(self):
        return bool(self.getCacheValue('mayConsumeWalletResources', 0))

    @property
    def currencyStatuses(self):
        return self.wallet.componentsStatuses

    @property
    def credits(self):
        return max(self.actualCredits, 0)

    @property
    def gold(self):
        return max(self.actualGold, 0)

    @property
    def crystal(self):
        return max(self.actualCrystal, 0)

    @property
    def money(self):
        return Money(credits=self.credits, gold=self.gold, crystal=self.crystal)

    @property
    def actualCredits(self):
        return self.getCacheValue(Currency.CREDITS, 0)

    @property
    def actualGold(self):
        return self.getCacheValue(Currency.GOLD, 0) if self.mayConsumeWalletResources or not self.wallet.useGold else 0

    @property
    def actualCrystal(self):
        return self.getCacheValue(Currency.CRYSTAL, 0)

    @property
    def actualMoney(self):
        return Money(credits=self.actualCredits, gold=self.actualGold, crystal=self.actualCrystal)

    @property
    def freeXP(self):
        return max(self.actualFreeXP, 0)

    @property
    def actualFreeXP(self):
        return self.getCacheValue('freeXP', 0) if self.mayConsumeWalletResources or not self.wallet.useFreeXP else 0

    @property
    def vehiclesXPs(self):
        return NationalGroupDataAccumulator(self.getCacheValue('vehTypeXP', dict()))

    @property
    def multipliedVehicles(self):
        return self.getCacheValue('multipliedXPVehs', list())

    @property
    def applyAdditionalXPCount(self):
        maxCount = self.lobbyContext.getServerSettings().getAdditionalBonusConfig().get('applyCount', 0)
        return max(maxCount - self.getCacheValue('applyAdditionalXPCount', maxCount), 0)

    @property
    def multipliedRankedVehicles(self):
        return self.getCacheValue('multipliedRankedBattlesVehs', set())

    @property
    def eliteVehicles(self):
        return self.getCacheValue('eliteVehicles', list())

    @property
    def vehicleTypeLocks(self):
        return self.getCacheValue('vehTypeLocks', dict())

    @property
    def globalVehicleLocks(self):
        return self.getCacheValue('globalVehicleLocks', dict())

    @property
    def attributes(self):
        return self.getCacheValue('attrs', 0)

    def isActivePremium(self, checkPremiumType):
        return self.getCacheValue('premiumInfo', PremiumInfo()).isActivePremium(checkPremiumType)

    @property
    def activePremiumType(self):
        return self.getCacheValue('premiumInfo', PremiumInfo()).activePremiumType

    @property
    def isPremium(self):
        return self.getCacheValue('premiumInfo', PremiumInfo()).isPremium

    @property
    def totalPremiumExpiryTime(self):
        return self.getCacheValue('premiumInfo', PremiumInfo()).totalPremiumExpiryTime

    @property
    def activePremiumExpiryTime(self):
        return self.getCacheValue('premiumInfo', PremiumInfo()).activePremiumExpiryTime

    @property
    def premiumInfo(self):
        return self.getCacheValue('premiumInfo', PremiumInfo()).data

    @property
    def isIngameShopEnabled(self):
        shopMode = self.lobbyContext.getServerSettings().ingameShop.shopMode
        shopFeatureKey = '/wot/game/apply_feature/shop2_0'
        return shopMode == 'enabled' or shopMode == 'restricted' and shopFeatureKey in self.SPA

    @property
    def isSubscriptionEnabled(self):
        subscriptionKey = '/wot/game/premium_subscription'
        return subscriptionKey in self.SPA

    @property
    def isTeamKiller(self):
        return self.getCacheValue('tkillIsSuspected', False)

    @property
    def restrictions(self):
        return self.getCacheValue('restrictions', set())

    @property
    def unlocks(self):
        return self.getCacheValue('unlocks', list())

    @property
    def initialUnlocks(self):
        return self.getCacheValue(('initial', 'unlocks'), list())

    @property
    def vehicleSlots(self):
        return self.getCacheValue('slots', 0)

    @property
    def dailyPlayHours(self):
        return self.getCacheValue('dailyPlayHours', [0])

    @property
    def todayPlayHours(self):
        return self.dailyPlayHours[0]

    @property
    def playLimits(self):
        return self.getCacheValue('playLimits', ((time_utils.ONE_DAY, ''), (time_utils.ONE_WEEK, '')))

    def getDailyTimeLimits(self):
        return self.playLimits[0][0]

    def getWeeklyTimeLimits(self):
        return self.playLimits[1][0]

    def getPlayTimeLimits(self):
        return (self.getDailyTimeLimits(), self.getWeeklyTimeLimits())

    @property
    def tankmenBerthsCount(self):
        return self.getCacheValue('berths', 0)

    @property
    def vehicleSellsLeft(self):
        return self.getCacheValue('vehicleSellsLeft', 0)

    @property
    def freeTankmenLeft(self):
        return self.getCacheValue('freeTMenLeft', 0)

    @property
    def accountDossier(self):
        return self.getCacheValue('dossier', '')

    @property
    def denunciationsLeft(self):
        return self.getCacheValue('denunciationsLeft', 0)

    @property
    def freeVehiclesLeft(self):
        return self.getCacheValue('freeVehiclesLeft', '')

    @property
    def clanDBID(self):
        return self.getCacheValue('clanDBID', 0)

    @property
    def clanInfo(self):
        return self.getCacheValue('clanInfo', set())

    @property
    def globalRating(self):
        return self.getCacheValue('globalRating', 0)

    @property
    def SPA(self):
        return self.getCacheValue('SPA', {})

    @property
    def piggyBank(self):
        return self.getCacheValue('piggyBank', {})

    @property
    def dummySessionStats(self):
        return self.getCacheValue('dummySessionStats', {})

    @property
    def additionalXPCache(self):
        return self.getCacheValue(_ADDITIONAL_XP_DATA_KEY, {})

    @property
    def isGoldFishBonusApplied(self):
        gfKey = '/common/goldfish_bonus_applied/'
        result = False
        spaDict = self.SPA
        if gfKey in spaDict:
            result = int(spaDict[gfKey])
        return result

    @property
    def tutorialsCompleted(self):
        return self.getCacheValue('tutorialsCompleted', 0)

    @property
    def oldVehInvIDs(self):
        return self.getCacheValue('oldVehInvIDs', ())

    def getMapsBlackList(self):
        blackList = self.getCacheValue('preferredMaps', {}).get('blackList', ())
        return blackList

    @async
    def _requestCache(self, callback):
        BigWorld.player().stats.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        result = super(StatsRequester, self)._preprocessValidData(data)
        extraXPInfo = result.get(_ADDITIONAL_XP_DATA_KEY, {})
        if extraXPInfo:
            result[_ADDITIONAL_XP_DATA_KEY] = processedXP = {}
            for vehicleID, XPData in extraXPInfo.iteritems():
                if XPData:
                    arenaUniqueID = XPData[0]
                    processedXP[arenaUniqueID] = _ControllableXPData(vehicleID, *XPData[1:])

        return result
