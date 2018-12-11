# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/utils/requesters.py
from gui.shared.money import Money

class IRequester(object):

    def request(self, callback):
        raise NotImplementedError

    def isSynced(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class IInventoryRequester(IRequester):

    def invalidateItem(self, itemTypeID, invIdx):
        raise NotImplementedError

    def updateC11nItemsAppliedCounts(self):
        raise NotImplementedError

    def updateC11nItemAppliedCount(self, itemCD, vehicleIntCD, count):
        raise NotImplementedError

    def getC11nItemAppliedVehicles(self, itemCD):
        raise NotImplementedError

    def getC11nItemAppliedOnVehicleCount(self, itemCD, vehicleCD):
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

    def getFreeSlots(self, vehiclesSlots):
        raise NotImplementedError


class IStatsRequester(IRequester):

    @property
    def mayConsumeWalletResources(self):
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

    @property
    def premiumExpiryTime(self):
        raise NotImplementedError

    @property
    def isPremium(self):
        raise NotImplementedError

    @property
    def isIngameShopEnabled(self):
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
    def refSystem(self):
        raise NotImplementedError

    @property
    def SPA(self):
        raise NotImplementedError

    @property
    def isGoldFishBonusApplied(self):
        raise NotImplementedError

    @property
    def tutorialsCompleted(self):
        raise NotImplementedError

    @property
    def oldVehInvIDs(self):
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
    def passportChangeCost(self):
        raise NotImplementedError

    @property
    def passportFemaleChangeCost(self):
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

    @property
    def boosters(self):
        raise NotImplementedError

    @property
    def discounts(self):
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

    @property
    def refSystem(self):
        raise NotImplementedError

    @property
    def tradeIn(self):
        raise NotImplementedError


class IShopRequester(IShopCommonStats, IRequester):

    def getPremiumCostWithDiscount(self, premiumPacketDiscounts=None):
        raise NotImplementedError

    def getTankmanCostWithDefaults(self):
        raise NotImplementedError

    @property
    def tankmanCostWithGoodyDiscount(self):
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

    def getVehicleSlotsItemPrice(self, currentSlotsCount):
        raise NotImplementedError

    def getTankmanCostItemPrices(self):
        raise NotImplementedError


class IGoodiesRequester(IRequester):

    @property
    def goodies(self):
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
    def vehRanks(self):
        raise NotImplementedError

    @property
    def clientRank(self):
        raise NotImplementedError

    @property
    def clientVehRanks(self):
        raise NotImplementedError

    @property
    def season(self):
        raise NotImplementedError

    @property
    def maxRank(self):
        raise NotImplementedError

    @property
    def maxVehRanks(self):
        raise NotImplementedError

    @property
    def ladderPoints(self):
        raise NotImplementedError

    @property
    def maxRankWithAwardReceived(self):
        raise NotImplementedError

    @property
    def seasonLadderPts(self):
        raise NotImplementedError

    @property
    def stepsCount(self):
        raise NotImplementedError

    @property
    def seasonStepsCount(self):
        raise NotImplementedError

    @property
    def shields(self):
        raise NotImplementedError

    @property
    def clientShields(self):
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


class ITokensRequester(IRequester):

    def getTokens(self):
        raise NotImplementedError

    def getLootBoxes(self):
        raise NotImplementedError

    def getLootBoxByTokenID(self, tokenID):
        raise NotImplementedError

    def getFreeLootBoxes(self):
        raise NotImplementedError

    def getLootBoxesTotalCount(self):
        raise NotImplementedError

    def getLootBoxesCountByType(self):
        raise NotImplementedError
