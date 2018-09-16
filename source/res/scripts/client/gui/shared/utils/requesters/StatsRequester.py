# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/StatsRequester.py
import BigWorld
from account_helpers import isPremiumAccount
from adisp import async
from gui.shared.money import Money, Currency
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import time_utils, dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared.utils.requesters import IStatsRequester

class StatsRequester(AbstractSyncDataRequester, IStatsRequester):
    wallet = dependency.descriptor(IWalletController)

    @property
    def mayConsumeWalletResources(self):
        return bool(self.getCacheValue('mayConsumeWalletResources', 0))

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
        return self.getCacheValue('vehTypeXP', dict())

    @property
    def multipliedVehicles(self):
        return self.getCacheValue('multipliedXPVehs', list())

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

    @property
    def premiumExpiryTime(self):
        return self.getCacheValue('premiumExpiryTime', 0)

    @property
    def isPremium(self):
        return isPremiumAccount(self.attributes)

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
    def refSystem(self):
        return self.getCacheValue('refSystem', {})

    @property
    def SPA(self):
        return self.getCacheValue('SPA', {})

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

    @async
    def _requestCache(self, callback):
        BigWorld.player().stats.getCache(lambda resID, value: self._response(resID, value, callback))
