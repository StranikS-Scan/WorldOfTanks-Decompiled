# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/utils/requesters.py
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, Generator, List, NamedTuple, Optional, Sequence, Set, Tuple, Union
    from collections import OrderedDict
    from gui.shared.gui_items.dossier.achievements.abstract import RegularAchievement
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.money import Money, DynamicMoney
    from gui.shared.utils.requesters import InventoryRequester
    from gui.veh_post_progression.models.ext_money import ExtendedMoney
    from post_progression_common import VehicleState
    from items.vehicles import VehicleType

class IRequester(object):

    def request(self, callback):
        raise NotImplementedError

    def isSynced(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class IAnonymizerRequester(IRequester):

    @property
    def isPlayerAnonymized(self):
        raise NotImplementedError

    @property
    def contactsFeedback(self):
        raise NotImplementedError


class IInventoryRequester(IRequester):

    def invalidateItem(self, itemTypeID, invIdx):
        raise NotImplementedError

    def getC11nItemAppliedVehicles(self, itemCD):
        raise NotImplementedError

    def getC11nItemAppliedOnVehicleCount(self, itemCD, vehicleCD):
        raise NotImplementedError

    def getC11nOutfitsFromPool(self, vehicleIntCD):
        raise NotImplementedError

    def initC11nItemsNoveltyData(self):
        raise NotImplementedError

    def updateC11nItemNoveltyData(self, itemIntCD):
        raise NotImplementedError

    def getC11nItemNoveltyData(self, itemIntCD):
        raise NotImplementedError

    def getC11nItemsNoveltyCounters(self, vehicleType):
        raise NotImplementedError

    def updateC11nProgressionDataForItem(self, itemIntCD):
        raise NotImplementedError

    def updateC11nProgressionData(self):
        raise NotImplementedError

    def getC11nProgressionDataForItem(self, itemIntCD):
        raise NotImplementedError

    def getC11nProgressionDataForVehicle(self, vehicleIntCD):
        raise NotImplementedError

    def getC11nProgressionData(self, itemIntCD, vehicleIntCD):
        raise NotImplementedError

    def getItemsData(self, itemTypeID):
        raise NotImplementedError

    def getItemData(self, typeCompDescr):
        raise NotImplementedError

    def getTankmanData(self, tmanInvID):
        raise NotImplementedError

    def getVehicleData(self, vehInvID):
        raise NotImplementedError

    def getOutfitData(self, intCompactDescr, season):
        raise NotImplementedError

    def getPreviousItem(self, itemTypeID, invDataIdx):
        raise NotImplementedError

    def getItems(self, itemTypeIdx, dataIdx=None):
        raise NotImplementedError

    def getC11nSerialNumber(self, itemCD):
        raise NotImplementedError

    def getFreeSlots(self, vehiclesSlots):
        raise NotImplementedError

    def getCacheValue(self, key, defaultValue):
        raise NotImplementedError

    def getInventoryEnhancements(self):
        raise NotImplementedError

    def getInstalledEnhancements(self):
        raise NotImplementedError

    def getVehPostProgression(self, vehIntCD):
        raise NotImplementedError

    def getVehExtData(self, vehIntCD):
        raise NotImplementedError

    def getVehPostProgressionFeaturesListByCD(self, vehIntCD):
        raise NotImplementedError

    def getDynSlotTypeID(self, vehIntCD):
        raise NotImplementedError

    def getIventoryVehiclesCDs(self):
        raise NotImplementedError

    def getInvIDsIterator(self):
        raise NotImplementedError


class IStatsRequester(IRequester):

    @property
    def mayConsumeWalletResources(self):
        raise NotImplementedError

    @property
    def currencyStatuses(self):
        raise NotImplementedError

    @property
    def dynamicCurrencyStatuses(self):
        raise NotImplementedError

    @property
    def credits(self):
        raise NotImplementedError

    @property
    def gold(self):
        raise NotImplementedError

    @property
    def crystal(self):
        raise NotImplementedError

    @property
    def eventCoin(self):
        raise NotImplementedError

    @property
    def equipCoin(self):
        raise NotImplementedError

    @property
    def bpcoin(self):
        raise NotImplementedError

    @property
    def money(self):
        raise NotImplementedError

    @property
    def actualCredits(self):
        raise NotImplementedError

    @property
    def actualGold(self):
        raise NotImplementedError

    @property
    def actualCrystal(self):
        raise NotImplementedError

    @property
    def actualEventCoin(self):
        raise NotImplementedError

    @property
    def actualBpcoin(self):
        raise NotImplementedError

    @property
    def actualEquipCoin(self):
        raise NotImplementedError

    @property
    def actualMoney(self):
        raise NotImplementedError

    @property
    def freeXP(self):
        raise NotImplementedError

    @property
    def actualFreeXP(self):
        raise NotImplementedError

    @property
    def vehiclesXPs(self):
        raise NotImplementedError

    @property
    def multipliedVehicles(self):
        raise NotImplementedError

    @property
    def applyAdditionalXPCount(self):
        raise NotImplementedError

    @property
    def multipliedRankedVehicles(self):
        raise NotImplementedError

    @property
    def eliteVehicles(self):
        raise NotImplementedError

    @property
    def vehicleTypeLocks(self):
        raise NotImplementedError

    @property
    def globalVehicleLocks(self):
        raise NotImplementedError

    @property
    def attributes(self):
        raise NotImplementedError

    def isActivePremium(self, checkPremiumType):
        raise NotImplementedError

    @property
    def activePremiumType(self):
        raise NotImplementedError

    @property
    def isPremium(self):
        raise NotImplementedError

    @property
    def totalPremiumExpiryTime(self):
        raise NotImplementedError

    @property
    def activePremiumExpiryTime(self):
        raise NotImplementedError

    @property
    def premiumInfo(self):
        raise NotImplementedError

    @property
    def isTeamKiller(self):
        raise NotImplementedError

    @property
    def restrictions(self):
        raise NotImplementedError

    @property
    def unlocks(self):
        raise NotImplementedError

    @property
    def initialUnlocks(self):
        raise NotImplementedError

    @property
    def vehicleSlots(self):
        raise NotImplementedError

    @property
    def dailyPlayHours(self):
        raise NotImplementedError

    @property
    def todayPlayHours(self):
        raise NotImplementedError

    @property
    def playLimits(self):
        raise NotImplementedError

    def getDailyTimeLimits(self):
        raise NotImplementedError

    def getWeeklyTimeLimits(self):
        raise NotImplementedError

    def getPlayTimeLimits(self):
        raise NotImplementedError

    @property
    def tankmenBerthsCount(self):
        raise NotImplementedError

    @property
    def vehicleSellsLeft(self):
        raise NotImplementedError

    @property
    def freeTankmenLeft(self):
        raise NotImplementedError

    @property
    def accountDossier(self):
        raise NotImplementedError

    @property
    def denunciationsLeft(self):
        raise NotImplementedError

    @property
    def freeVehiclesLeft(self):
        raise NotImplementedError

    @property
    def clanDBID(self):
        raise NotImplementedError

    @property
    def clanInfo(self):
        raise NotImplementedError

    @property
    def globalRating(self):
        raise NotImplementedError

    @property
    def SPA(self):
        raise NotImplementedError

    @property
    def piggyBank(self):
        raise NotImplementedError

    @property
    def entitlements(self):
        raise NotImplementedError

    @property
    def dummySessionStats(self):
        raise NotImplementedError

    @property
    def additionalXPCache(self):
        raise NotImplementedError

    @property
    def isGoldFishBonusApplied(self):
        raise NotImplementedError

    @property
    def isAnonymousRestricted(self):
        raise NotImplementedError

    @property
    def isSsrPlayEnabled(self):
        raise NotImplementedError

    @property
    def comp7(self):
        raise NotImplementedError

    @property
    def tutorialsCompleted(self):
        raise NotImplementedError

    @property
    def oldVehInvIDs(self):
        raise NotImplementedError

    @property
    def dynamicCurrencies(self):
        raise NotImplementedError

    @property
    def isEmergencyModeEnabled(self):
        raise NotImplementedError

    def getMapsBlackList(self):
        raise NotImplementedError

    def getMaxResearchedLevelByNations(self):
        raise NotImplementedError

    def getMaxResearchedLevel(self, nationID):
        raise NotImplementedError

    def getMoneyExt(self, vehCD):
        raise NotImplementedError

    def getDynamicMoney(self):
        raise NotImplementedError

    def getWeeklyVehicleCrystals(self, vehCD):
        raise NotImplementedError

    @property
    def luiVersion(self):
        raise NotImplementedError

    @property
    def defaultSettingsGroup(self):
        raise NotImplementedError

    @property
    def newbieHintsGroup(self):
        raise NotImplementedError


class IDossierRequester(IRequester):

    def getVehicleDossier(self, vehTypeCompDescr):
        raise NotImplementedError

    def getVehDossiersIterator(self):
        raise NotImplementedError

    def getUserDossierRequester(self, databaseID):
        raise NotImplementedError

    def closeUserDossier(self, databaseID):
        raise NotImplementedError

    def onCenterIsLongDisconnected(self, isLongDisconnected):
        raise NotImplementedError


class IShopCommonStats(object):

    def getPrices(self):
        raise NotImplementedError

    def getBoosterPrices(self):
        raise NotImplementedError

    def getHiddens(self):
        raise NotImplementedError

    def getHiddenBoosters(self):
        raise NotImplementedError

    def getNotToBuyVehicles(self):
        raise NotImplementedError

    def getVehicleRentPrices(self):
        raise NotImplementedError

    def getVehiclesForGold(self):
        raise NotImplementedError

    def getVehiclesSellPriceFactors(self):
        raise NotImplementedError

    def getItemPrice(self, intCD):
        raise NotImplementedError

    def getBoosterPricesTuple(self, boosterID):
        raise NotImplementedError

    def getOperationPrices(self):
        raise NotImplementedError

    def getItem(self, intCD):
        raise NotImplementedError

    def getAchievementReward(self, achievement, arenaType=0):
        raise NotImplementedError

    @property
    def revision(self):
        raise NotImplementedError

    @property
    def paidRemovalCost(self):
        raise NotImplementedError

    @property
    def paidDeluxeRemovalCost(self):
        raise NotImplementedError

    def getPaidModernizedRemovalCost(self, level):
        raise NotImplementedError

    @property
    def paidTrophyBasicRemovalCost(self):
        raise NotImplementedError

    @property
    def paidTrophyUpgradedRemovalCost(self):
        raise NotImplementedError

    @property
    def exchangeRate(self):
        raise NotImplementedError

    @property
    def crystalExchangeRate(self):
        raise NotImplementedError

    @property
    def exchangeRateForShellsAndEqs(self):
        raise NotImplementedError

    @property
    def sellPriceModif(self):
        raise NotImplementedError

    @property
    def vehiclesRestoreConfig(self):
        raise NotImplementedError

    @property
    def tankmenRestoreConfig(self):
        raise NotImplementedError

    def sellPriceModifiers(self, compDescr):
        raise NotImplementedError

    @property
    def slotsPrices(self):
        raise NotImplementedError

    def getVehicleSlotsPrice(self, currentSlotsCount):
        raise NotImplementedError

    @property
    def dropSkillsCost(self):
        raise NotImplementedError

    @property
    def dailyXPFactor(self):
        raise NotImplementedError

    @property
    def winXPFactorMode(self):
        raise NotImplementedError

    @property
    def berthsPrices(self):
        raise NotImplementedError

    def getTankmanBerthPrice(self, berthsCount):
        raise NotImplementedError

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        raise NotImplementedError

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        raise NotImplementedError

    @property
    def tankmanCost(self):
        raise NotImplementedError

    @property
    def changeRoleCost(self):
        raise NotImplementedError

    @property
    def freeXPConversion(self):
        raise NotImplementedError

    @property
    def freeXPToTManXPRate(self):
        raise NotImplementedError

    def getItemsData(self):
        raise NotImplementedError

    def getGoodiesData(self):
        raise NotImplementedError

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        raise NotImplementedError

    def getEmblemsGroupPriceFactors(self):
        raise NotImplementedError

    def getEmblemsGroupHiddens(self):
        raise NotImplementedError

    def getInscriptionsGroupPriceFactors(self, nationID):
        raise NotImplementedError

    def getInscriptionsGroupHiddens(self, nationID):
        raise NotImplementedError

    def getCamouflagesPriceFactors(self, nationID):
        raise NotImplementedError

    def getCamouflagesHiddens(self, nationID):
        raise NotImplementedError

    @property
    def premiumCost(self):
        raise NotImplementedError

    @property
    def goodies(self):
        raise NotImplementedError

    def getGoodieByID(self, discountID):
        raise NotImplementedError

    def getGoodiesByVariety(self, variety):
        raise NotImplementedError

    def getBattlePassCost(self):
        raise NotImplementedError

    def getBattlePassLevelCost(self):
        raise NotImplementedError

    @property
    def boosters(self):
        raise NotImplementedError

    @property
    def discounts(self):
        raise NotImplementedError

    @property
    def demountKits(self):
        raise NotImplementedError

    @property
    def recertificationForms(self):
        raise NotImplementedError

    def getPremiumPacketCost(self, days):
        raise NotImplementedError

    @property
    def camouflageCost(self):
        raise NotImplementedError

    def getCamouflageCost(self, days=0):
        raise NotImplementedError

    @property
    def playerInscriptionCost(self):
        raise NotImplementedError

    def getInscriptionCost(self, days=0):
        raise NotImplementedError

    @property
    def playerEmblemCost(self):
        raise NotImplementedError

    def getEmblemCost(self, days=0):
        raise NotImplementedError


class IShopRequester(IShopCommonStats, IRequester):

    def getPremiumCostWithDiscount(self, premiumPacketDiscounts=None):
        raise NotImplementedError

    def isActionOnPremium(self):
        raise NotImplementedError

    def getTankmanCostWithGoodyDiscount(self, vehLevel):
        raise NotImplementedError

    @property
    def freeXPConversionLimit(self):
        raise NotImplementedError

    @property
    def freeXPConversionWithDiscount(self):
        raise NotImplementedError

    @property
    def isXPConversionActionActive(self):
        raise NotImplementedError

    @property
    def isCreditsConversionActionActive(self):
        raise NotImplementedError

    @property
    def personalPremiumPacketsDiscounts(self):
        raise NotImplementedError

    @property
    def personalSlotDiscounts(self):
        raise NotImplementedError

    @property
    def personalTankmanDiscounts(self):
        raise NotImplementedError

    @property
    def personalXPExchangeDiscounts(self):
        raise NotImplementedError

    @property
    def personalVehicleDiscounts(self):
        raise NotImplementedError

    def getVehicleDiscountDescriptions(self):
        raise NotImplementedError

    def getPersonalVehicleDiscountPrice(self, typeCompDescr):
        raise NotImplementedError

    def bestGoody(self, goodies):
        raise NotImplementedError

    def customRoleSlotChangeCost(self, vehType, isRaw=False):
        raise NotImplementedError

    def getVehicleSlotsItemPrice(self, currentSlotsCount):
        raise NotImplementedError

    def getTankmanCostItemPrices(self, vehLevel):
        raise NotImplementedError

    def getNotInShopProgressionLvlItems(self):
        raise NotImplementedError


class IGoodiesRequester(IRequester):

    @property
    def goodies(self):
        raise NotImplementedError

    @property
    def pr2ConversionResult(self):
        raise NotImplementedError

    def getActiveClanReserves(self):
        raise NotImplementedError


class IRecycleBinRequester(IRequester):

    @property
    def recycleBin(self):
        raise NotImplementedError

    @property
    def vehiclesBuffer(self):
        raise NotImplementedError

    def getVehicleRestoreInfo(self, intCD, restoreDuration, restoreCooldown):
        raise NotImplementedError

    def getVehiclesIntCDs(self):
        raise NotImplementedError

    def getTankmen(self, maxDuration):
        raise NotImplementedError

    def getTankman(self, invID, maxDuration):
        raise NotImplementedError


class IVehicleRotationRequester(IRequester):

    def getBattlesCount(self, groupNum):
        raise NotImplementedError

    def isGroupLocked(self, groupNum):
        raise NotImplementedError

    def getGroupNum(self, vehIntCD):
        raise NotImplementedError

    def isInfinite(self, groupNum):
        raise NotImplementedError


class IRankedRequester(IRequester):

    @property
    def accRank(self):
        raise NotImplementedError

    @property
    def season(self):
        raise NotImplementedError

    @property
    def maxRank(self):
        raise NotImplementedError

    @property
    def stepsCount(self):
        raise NotImplementedError

    @property
    def seasonStepsCount(self):
        raise NotImplementedError

    @property
    def seasonEfficiencyStamp(self):
        raise NotImplementedError

    @property
    def shields(self):
        raise NotImplementedError

    @property
    def persistentBonusBattles(self):
        raise NotImplementedError

    @property
    def dailyBonusBattles(self):
        raise NotImplementedError

    @property
    def divisionsStats(self):
        raise NotImplementedError


class IBattleRoyaleRequester(IRequester):

    @property
    def accTitle(self):
        raise NotImplementedError

    @property
    def battleCount(self):
        raise NotImplementedError

    @property
    def killCount(self):
        raise NotImplementedError

    @property
    def topCount(self):
        raise NotImplementedError

    @property
    def testDriveExpired(self):
        raise NotImplementedError

    @property
    def brMultipliedSTPCoinsVehs(self):
        raise NotImplementedError

    def getStats(self, arenaBonusType, playerDatabaseID=None):
        raise NotImplementedError


class IBadgesRequester(IRequester):

    @property
    def available(self):
        raise NotImplementedError

    @property
    def selected(self):
        raise NotImplementedError


class IEpicMetaGameRequester(IRequester):

    @property
    def playerLevelInfo(self):
        raise NotImplementedError

    @property
    def seasonData(self):
        raise NotImplementedError

    @property
    def skillPoints(self):
        raise NotImplementedError

    def selectedSkills(self, vehicleCD):
        raise NotImplementedError

    @property
    def skillLevels(self):
        raise NotImplementedError

    @property
    def battleCount(self):
        raise NotImplementedError

    @property
    def averageXP(self):
        raise NotImplementedError


class IBlueprintsRequester(IRequester):

    def getBlueprintCount(self, vehicleCD, vehicleLevel):
        raise NotImplementedError

    def getBlueprintData(self, vehicleCD, vehicleLevel):
        raise NotImplementedError

    def getBlueprintDiscount(self, vehicleCD, vehicleLevel, potentialFilledCount=0):
        raise NotImplementedError

    def getRequiredCountAndDiscount(self, vehicleCD, vLevel):
        raise NotImplementedError

    def getFragmentDiscountAndCost(self, vehicleCD, vehicleLevel, xpFullCost):
        raise NotImplementedError

    def getAllNationalFragmentsData(self):
        raise NotImplementedError

    def calculateCost(self, oldCost, discount):
        raise NotImplementedError

    def getNationalFragments(self, fragmentCD):
        raise NotImplementedError

    def getNationalAllianceFragments(self, fragmentCD, vehicleLevel):
        raise NotImplementedError

    def getNationalRequiredOptions(self, fragmentCD, vehicleLevel):
        raise NotImplementedError

    def getIntelligenceCount(self):
        raise NotImplementedError

    def getRequiredIntelligenceAndNational(self, vLevel):
        raise NotImplementedError

    def hasUniversalFragments(self):
        raise NotImplementedError

    def isLastFragment(self, totalCount, filledCount):
        raise NotImplementedError

    def canConvertToVehicleFragment(self, vehicleCD, vehicleLevel):
        raise NotImplementedError

    def getConvertibleFragmentCount(self, vehicleCD, vehicleLevel):
        raise NotImplementedError

    def getLayout(self, vehicleCD, vehicleLevel):
        raise NotImplementedError

    def isBlueprintsAvailable(self):
        raise NotImplementedError

    def hasBlueprintsOrFragments(self):
        raise NotImplementedError


class ITokensRequester(IRequester):

    def getTokens(self):
        raise NotImplementedError

    def getToken(self, tokenID):
        raise NotImplementedError

    def getTokenInfo(self, tokenID):
        raise NotImplementedError

    def getTokenCount(self, tokenID):
        raise NotImplementedError

    def getTokenExpiryTime(self, tokenID):
        raise NotImplementedError

    def isTokenAvailable(self, tokenID):
        raise NotImplementedError

    def getAttemptsAfterGuaranteedRewards(self, box):
        raise NotImplementedError

    def getLootBoxes(self):
        raise NotImplementedError

    def getLootBoxByTokenID(self, tokenID):
        raise NotImplementedError

    def getLootBoxByID(self, boxID):
        raise NotImplementedError

    def getFreeLootBoxes(self):
        raise NotImplementedError

    def getLootBoxesTotalCount(self):
        raise NotImplementedError

    def getLootBoxesCountByType(self):
        raise NotImplementedError

    def getLastViewedProgress(self, tokenId):
        raise NotImplementedError

    def markTokenProgressAsViewed(self, tokenId):
        raise NotImplementedError

    def hasTokenCountChanged(self, tokenId):
        raise NotImplementedError

    def onDisconnected(self):
        raise NotImplementedError


class IBaseSessionStats(object):

    @property
    def battleCnt(self):
        raise NotImplementedError

    @property
    def incomeCredits(self):
        raise NotImplementedError

    @property
    def xp(self):
        raise NotImplementedError

    @property
    def incomeCrystal(self):
        raise NotImplementedError

    @property
    def freeXP(self):
        raise NotImplementedError

    @property
    def averageXp(self):
        raise NotImplementedError

    @property
    def ratioDamage(self):
        raise NotImplementedError

    @property
    def helpDamage(self):
        raise NotImplementedError

    @property
    def ratioKill(self):
        raise NotImplementedError

    @property
    def averageDamage(self):
        raise NotImplementedError

    @property
    def blockedDamage(self):
        raise NotImplementedError

    @property
    def winRate(self):
        raise NotImplementedError

    @property
    def wins(self):
        raise NotImplementedError

    @property
    def averageFrags(self):
        raise NotImplementedError

    @property
    def survivedRatio(self):
        raise NotImplementedError

    @property
    def spotted(self):
        raise NotImplementedError


class IBaseAccountStats(IBaseSessionStats):

    @property
    def netCredits(self):
        raise NotImplementedError

    @property
    def netCrystal(self):
        raise NotImplementedError

    @property
    def averageVehicleLevel(self):
        raise NotImplementedError


class IBaseVehStats(IBaseSessionStats):
    pass


class IRandomAccountStats(IBaseAccountStats):

    @property
    def wtr(self):
        raise NotImplementedError


class IRandomVehStats(IBaseVehStats):

    @property
    def wtr(self):
        raise NotImplementedError


class ISessionStatsRequester(IRequester):

    def getAccountStats(self, arenaType):
        raise NotImplementedError

    def getVehiclesStats(self, arenaType, vehId):
        raise NotImplementedError

    def getStatsVehList(self, arenaType):
        raise NotImplementedError

    def getAccountWtr(self):
        raise NotImplementedError


class IOffersRequester(IRequester):

    def isBannerSeen(self, offerID):
        raise NotImplementedError

    def getReceivedGifts(self, offerID):
        raise NotImplementedError


class IBattlePassRequester(IRequester):

    def getSeasonID(self):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getActiveChapterID(self):
        raise NotImplementedError

    def getPointsForVehicle(self, vehicleID, default=0):
        raise NotImplementedError

    def getChapterStats(self):
        raise NotImplementedError

    def getCurrentLevelByChapterID(self, chapterID):
        raise NotImplementedError

    def getPointsByChapterID(self, chapterID):
        raise NotImplementedError

    def getNonChapterPoints(self):
        raise NotImplementedError


class IGiftSystemRequester(IRequester):

    @property
    def isHistoryReady(self):
        raise NotImplementedError


class IGameRestrictionsRequester(IRequester):

    @property
    def session(self):
        raise NotImplementedError

    @property
    def hasSessionLimit(self):
        raise NotImplementedError

    def getKickAt(self):
        raise NotImplementedError

    @property
    def settings(self):
        raise NotImplementedError


class IResourceWellRequester(IRequester):

    def getCurrentPoints(self):
        raise NotImplementedError

    def getBalance(self):
        raise NotImplementedError

    def getReward(self):
        raise NotImplementedError

    def getInitialNumberAmounts(self):
        raise NotImplementedError


class IAchievements20Requester(IRequester):

    def getLayout(self):
        raise NotImplementedError

    def getLayoutState(self):
        raise NotImplementedError

    def getAchievementBitmask(self):
        raise NotImplementedError

    def getLayoutLength(self):
        raise NotImplementedError
