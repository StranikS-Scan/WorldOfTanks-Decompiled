# Embedded file name: scripts/client/gui/shared/utils/requesters/ShopRequester.py
import BigWorld
import weakref
from adisp import async
from collections import defaultdict
from abc import ABCMeta, abstractmethod
from constants import WIN_XP_FACTOR_MODE
from debug_utils import LOG_DEBUG
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_TARGET_TYPE
from goodies.goodie_helpers import NamedGoodieData, getPremiumCost, getPriceWithDiscount
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester

class ShopCommonStats(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getValue(self, key, defaultValue = None):
        pass

    def getPrices(self):
        return self.getItemsData().get('itemPrices', {})

    def getHiddens(self):
        return self.getItemsData().get('notInShopItems', set([]))

    def getNotToBuyVehicles(self):
        return self.getItemsData().get('vehiclesNotToBuy', set([]))

    def getVehicleRentPrices(self):
        return self.getItemsData().get('vehiclesRentPrices', {})

    def getVehiclesForGold(self):
        return self.getItemsData().get('vehiclesToSellForGold', set([]))

    def getVehiclesSellPriceFactors(self):
        return self.getItemsData().get('vehicleSellPriceFactors', {})

    def getItemPrice(self, intCD):
        return self.getPrices().get(intCD, (0, 0))

    def getItem(self, intCD):
        return (self.getItemPrice(intCD), intCD in self.getHiddens(), intCD in self.getVehiclesForGold())

    @property
    def revision(self):
        """
        @return: shop revision value
        """
        return self.getValue('rev', 0)

    @property
    def paidRemovalCost(self):
        """
        @return: cost of dismantling of non-removable optional
                                devices for gold
        """
        return self.getValue('paidRemovalCost', 10)

    @property
    def exchangeRate(self):
        """
        @return: rate of gold for credits exchanging
        """
        return self.getValue('exchangeRate', 400)

    @property
    def exchangeRateForShellsAndEqs(self):
        """
        @return: rate of gold for credits exchanging for F2W
                                premium shells and eqs action
        """
        return self.getValue('exchangeRateForShellsAndEqs', 400)

    @property
    def sellPriceModif(self):
        return self.getValue('sellPriceModif', 0.5)

    def sellPriceModifiers(self, compDescr):
        sellPriceModif = self.sellPriceModif
        sellPriceFactors = self.getVehiclesSellPriceFactors()
        sellForGold = self.getVehiclesForGold()
        return (self.revision,
         self.exchangeRate,
         self.exchangeRateForShellsAndEqs,
         sellPriceModif,
         sellPriceFactors.get(compDescr, sellPriceModif),
         compDescr in sellForGold)

    @property
    def slotsPrices(self):
        return self.getValue('slotsPrices', (0, 1, [300]))

    def getVehicleSlotsPrice(self, currentSlotsCount):
        """
        @param currentSlotsCount: current vehicle slots count
        @return: new vehicle slot price
        """
        return BigWorld.player().shop.getNextSlotPrice(currentSlotsCount, self.slotsPrices)

    @property
    def dropSkillsCost(self):
        """
        @return: drop tankman skill cost
        """
        return self.getValue('dropSkillsCost', {})

    @property
    def dailyXPFactor(self):
        """
        @return: daily experience multiplier
        """
        return self.getValue('dailyXPFactor', 2)

    @property
    def winXPFactorMode(self):
        """
        @return: mode for applying daily XP factor
        """
        return self.getValue('winXPFactorMode', WIN_XP_FACTOR_MODE.DAILY)

    @property
    def berthsPrices(self):
        return self.getValue('berthsPrices', (0, 1, [300]))

    def getTankmanBerthPrice(self, berthsCount):
        """
        @param berthsCount: current barrack's berths count
        @return: (new berths pack price, pack berths count)
        """
        prices = self.berthsPrices
        return (BigWorld.player().shop.getNextBerthPackPrice(berthsCount, prices), prices[1])

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        """
        @return: is premium shells for credits action enabled
        """
        return self.getValue('isEnabledBuyingGoldShellsForCredits', False)

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        """
        @return: is premium equipments for credits action enabled
        """
        return self.getValue('isEnabledBuyingGoldEqsForCredits', False)

    @property
    def tankmanCost(self):
        """
        @return: tankman studying cost
                        tmanCost -  ( tmanCostType, ), where
                        tmanCostType = {
                                        'roleLevel' : minimal role level after operation,
                                        'credits' : cost in credits,
                                        'gold' : cost in gold,
                                        'baseRoleLoss' : float in [0, 1], fraction of role to drop,
                                        'classChangeRoleLoss' : float in [0, 1], fraction of role to drop additionally if
                                                classes of self.vehicleTypeID and newVehicleTypeID are different,
                                        'isPremium' : tankman becomes premium,
                                        }.
                                List is sorted by role level.
        """
        return self.getValue('tankmanCost', tuple())

    @property
    def changeRoleCost(self):
        """
        @return: tankman change role cost in gold
        """
        return self.getValue('changeRoleCost', 600)

    @property
    def freeXPConversion(self):
        """
        @return: free experience to vehicle xp exchange rate and cost
                                ( discrecity, cost)
        """
        return self.getValue('freeXPConversion', (25, 1))

    @property
    def passportChangeCost(self):
        """
        @return: tankman passport replace cost in gold
        """
        return self.getValue('passportChangeCost', 50)

    @property
    def passportFemaleChangeCost(self):
        """
        @return: tankman passport replace cost in gold
        """
        return self.getValue('femalePassportChangeCost', 500)

    @property
    def freeXPToTManXPRate(self):
        """
        @return: free experience to tankman experience exchange rate
        """
        return self.getValue('freeXPToTManXPRate', 10)

    def getItemsData(self):
        return self.getValue('items', {})

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        return self.getItemsData().get('vehicleCamouflagePriceFactors', {}).get(typeCompDescr)

    def getHornPriceFactor(self, hornID):
        return self.getItemsData().get('vehicleHornPriceFactors', {}).get(hornID)

    def getEmblemsGroupPriceFactors(self):
        return self.getItemsData().get('playerEmblemGroupPriceFactors', {})

    def getEmblemsGroupHiddens(self):
        return self.getItemsData().get('notInShopPlayerEmblemGroups', set([]))

    def getInscriptionsGroupPriceFactors(self, nationID):
        return self.getItemsData().get('inscriptionGroupPriceFactors', [])[nationID]

    def getInscriptionsGroupHiddens(self, nationID):
        return self.getItemsData().get('notInShopInscriptionGroups', [])[nationID]

    def getCamouflagesPriceFactors(self, nationID):
        return self.getItemsData().get('camouflagePriceFactors', [])[nationID]

    def getCamouflagesHiddens(self, nationID):
        return self.getItemsData().get('notInShopCamouflages', [])[nationID]

    def getHornPrice(self, hornID):
        return self.getItemsData().get('hornPrices', {}).get(hornID)

    @property
    def premiumCost(self):
        return self.getValue('premiumCost', {})

    @property
    def goodies(self):
        return self.getValue('goodies', {})

    def getGoodieByID(self, discountID):
        return self.goodies.get(discountID, None)

    def getGoodiesByVariety(self, variety):
        return dict(filter(lambda (goodieID, item): item.variety == variety, self.goodies.iteritems()))

    @property
    def boosters(self):
        return self.getGoodiesByVariety(GOODIE_VARIETY.BOOSTER)

    @property
    def discounts(self):
        return self.getGoodiesByVariety(GOODIE_VARIETY.DISCOUNT)

    @property
    def premiumPacketsDiscounts(self):
        return dict(filter(lambda (discountID, item): item.targetID == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM, self.discounts.iteritems()))

    def getPremiumPacketCost(self, days):
        return self.premiumCost.get(days)

    @property
    def camouflageCost(self):
        return self.getValue('camouflageCost', {})

    def getCamouflageCost(self, days = 0):
        return self.camouflageCost.get(days)

    @property
    def playerInscriptionCost(self):
        return self.getValue('playerInscriptionCost', {})

    def getInscriptionCost(self, days = 0):
        return self.playerInscriptionCost.get(days)

    @property
    def playerEmblemCost(self):
        return self.getValue('playerEmblemCost', {})

    def getEmblemCost(self, days = 0):
        return self.playerEmblemCost.get(days)

    @property
    def refSystem(self):
        return self.getValue('refSystem', {})


class ShopRequester(AbstractSyncDataRequester, ShopCommonStats):

    def __init__(self, goodies):
        super(ShopRequester, self).__init__()
        self.defaults = DefaultShopRequester({}, self)
        self._goodies = weakref.proxy(goodies)

    def clear(self):
        self.defaults.clear()
        super(ShopRequester, self).clear()

    def getValue(self, key, defaultValue = None):
        return self.getCacheValue(key, defaultValue)

    def _response(self, resID, invData, callback):
        if invData is not None:
            self.defaults.update(invData.get('defaults'))
        super(ShopRequester, self)._response(resID, invData, callback)
        return

    @async
    def _requestCache(self, callback):
        """
        Overloaded method to request shop cache
        """
        BigWorld.player().shop.getCache(lambda resID, value, rev: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        data = dict(data)
        formattedGoodies = defaultdict(dict)
        for goodieID, goodieData in data.get('goodies', {}).iteritems():
            formattedGoodies[goodieID] = NamedGoodieData(*goodieData)

        data['goodies'] = formattedGoodies
        return data

    @property
    def personalPremiumPacketsDiscounts(self):
        return dict(filter(lambda (discountID, item): discountID in self._goodies.goodies, self.premiumPacketsDiscounts.iteritems()))

    def getPremiumCostWithDiscount(self, premiumPacketDiscounts = None):
        discounts = premiumPacketDiscounts or self.personalPremiumPacketsDiscounts
        premiumCostWithDiscount = self.premiumCost.copy()
        for discount in discounts.itervalues():
            premiumCostWithDiscount[discount.getTargetValue()] = getPremiumCost(self.premiumCost, discount)

        return premiumCostWithDiscount

    def getTankmanCostWithDefaults(self):
        """
        @return: tankman studying cost
                        tmanCost, action -  ( tmanCostType, ), ( actionData, ) where
                        tmanCostType = {
                                        'roleLevel' : minimal role level after operation,
                                        'credits' : cost in credits,
                                        'defCredits' : cost in credits,
                                        'gold' : default cost in gold,
                                        'defGold' : default cost in gold,
                                        'baseRoleLoss' : float in [0, 1], fraction of role to drop,
                                        'classChangeRoleLoss' : float in [0, 1], fraction of role to drop additionally if
                                                classes of self.vehicleTypeID and newVehicleTypeID are different,
                                        'isPremium' : tankman becomes premium,
                                        }.
                                List is sorted by role level.
                        actionData = Action data for each level of retraining
        """
        from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
        shopPrices = self.tankmanCost
        defaultPrices = self.defaults.tankmanCost
        action = []
        tmanCost = []
        for idx, price in enumerate(shopPrices):
            data = price.copy()
            default = defaultPrices[idx]
            isPremium = price['isPremium']
            shopPrice = price['gold'] if isPremium else price['credits']
            defaultPrice = default['gold'] if isPremium else default['credits']
            actionData = None
            if shopPrice != defaultPrice:
                key = 'goldTankmanCost' if isPremium else 'creditsTankmanCost'
                newPrice = (0, shopPrice) if isPremium else (shopPrice, 0)
                oldPrice = (0, defaultPrice) if isPremium else (defaultPrice, 0)
                state = (None, ACTION_TOOLTIPS_STATE.DISCOUNT) if isPremium else (ACTION_TOOLTIPS_STATE.DISCOUNT, None)
                actionData = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
                 'key': key,
                 'isBuying': True,
                 'state': state,
                 'newPrice': newPrice,
                 'oldPrice': oldPrice}
            tmanCost.append(data)
            action.append(actionData)

        return (tmanCost, action)

    def getVehicleSlotsPrice(self, currentSlotsCount):
        price = super(ShopRequester, self).getVehicleSlotsPrice(currentSlotsCount)
        slotGoodies = self.personalSlotDiscounts
        if slotGoodies:
            bestGoody = self.bestGoody(slotGoodies)
            return getPriceWithDiscount(price, bestGoody.resource)
        else:
            return price

    @property
    def tankmanCostWithGoodyDiscount(self):
        prices = self.tankmanCost
        tankmanGoodies = self.personalTankmanDiscounts
        if tankmanGoodies:
            bestGoody = self.bestGoody(tankmanGoodies)
            return self.__applyGoodyToStudyCost(prices, bestGoody)
        else:
            return prices

    @property
    def freeXPConversionLimit(self):
        goody = self.bestGoody(self.personalXPExchangeDiscounts)
        if goody:
            return goody.target[2] * self.defaults.freeXPConversion[0]
        else:
            return None
            return None

    @property
    def freeXPConversionWithDiscount(self):
        goody = self.bestGoody(self.personalXPExchangeDiscounts)
        rate = self.freeXPConversion
        if goody:
            return (getPriceWithDiscount(rate[0], goody.resource), rate[1])
        else:
            return rate

    @property
    def isXPConversionActionActive(self):
        return self.freeXPConversion[0] > self.defaults.freeXPConversion[0]

    @property
    def personalSlotDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_SLOT)

    @property
    def personalTankmanDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN)

    @property
    def personalXPExchangeDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION)

    def bestGoody(self, goodies):
        if goodies:
            _, goody = sorted(goodies.iteritems(), key=lambda (_, goody): goody.resource[1])[-1]
            return goody
        else:
            return None
            return None

    def __applyGoodyToStudyCost(self, prices, goody):

        def convert(price):
            newPrice = price.copy()
            if price['isPremium']:
                newPrice['gold'] = getPriceWithDiscount(price['gold'], goody.resource)
            return newPrice

        return tuple(map(convert, prices))

    def __personalDiscountsByTarget(self, targetID):
        discounts = filter(lambda (discountID, item): item.targetID == targetID, self.discounts.iteritems())
        return dict(filter(lambda (discountID, item): discountID in self._goodies.goodies, discounts))


class DefaultShopRequester(ShopCommonStats):

    def __init__(self, cache, proxy):
        self.__cache = cache.copy()
        self.__proxy = weakref.proxy(proxy)

    def clear(self):
        LOG_DEBUG('Clearing shop defaults.')
        self.__cache.clear()

    def update(self, cache):
        if cache is None:
            cache = {}
        self.clear()
        self.__cache = cache.copy()
        return

    def getValue(self, key, defaultValue = None):
        return self.__cache.get(key, defaultValue)

    @property
    def revision(self):
        return self.__proxy.revision

    def getPrices(self):
        return self.getItemsData().get('itemPrices', self.__proxy.getPrices())

    def getHiddens(self):
        return self.getItemsData().get('notInShopItems', self.__proxy.getHiddens())

    def getNotToBuyVehicles(self):
        return self.getItemsData().get('vehiclesNotToBuy', self.__proxy.getNotToBuyVehicles())

    def getVehicleRentPrices(self):
        return self.getItemsData().get('vehiclesRentPrices', self.__proxy.getVehicleRentPrices())

    def getVehiclesForGold(self):
        return self.getItemsData().get('vehiclesToSellForGold', {})

    def getVehiclesSellPriceFactors(self):
        return self.getItemsData().get('vehicleSellPriceFactors', {})

    def getItemPrice(self, intCD):
        return self.getPrices().get(intCD, self.__proxy.getItemPrice(intCD))

    @property
    def paidRemovalCost(self):
        """
        @return: cost of dismantling of non-removable optional
                                devices for gold
        """
        return self.getValue('paidRemovalCost', self.__proxy.paidRemovalCost)

    @property
    def exchangeRate(self):
        """
        @return: rate of gold for credits exchanging
        """
        return self.getValue('exchangeRate', self.__proxy.exchangeRate)

    @property
    def exchangeRateForShellsAndEqs(self):
        """
        @return: rate of gold for credits exchanging for F2W
                                premium shells and eqs action
        """
        return self.getValue('exchangeRateForShellsAndEqs', self.__proxy.exchangeRateForShellsAndEqs)

    @property
    def sellPriceModif(self):
        return self.getValue('sellPriceModif', self.__proxy.sellPriceModif)

    @property
    def slotsPrices(self):
        return self.getValue('slotsPrices', self.__proxy.slotsPrices)

    @property
    def dropSkillsCost(self):
        """
        @return: drop tankman skill cost
        """
        value = self.__proxy.dropSkillsCost
        defaults = self.getValue('dropSkillsCost')
        if defaults is None:
            return value
        else:
            newValue = {}
            for k, v in value.items():
                mergedValue = v.copy()
                defaultValue = defaults.get(k, {})
                mergedValue.update(defaultValue)
                newValue[k] = mergedValue

            return newValue

    @property
    def dailyXPFactor(self):
        """
        @return: daily experience multiplier
        """
        return self.getValue('dailyXPFactor', self.__proxy.dailyXPFactor)

    @property
    def winXPFactorMode(self):
        """
        @return: mode for applying daily XP factor
        """
        return self.getValue('winXPFactorMode', self.__proxy.winXPFactorMode)

    @property
    def berthsPrices(self):
        return self.getValue('berthsPrices', self.__proxy.berthsPrices)

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        """
        @return: is premium shells for credits action enabled
        """
        return self.getValue('isEnabledBuyingGoldShellsForCredits', self.__proxy.isEnabledBuyingGoldShellsForCredits)

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        """
        @return: is premium equipments for credits action enabled
        """
        return self.getValue('isEnabledBuyingGoldEqsForCredits', self.__proxy.isEnabledBuyingGoldEqsForCredits)

    @property
    def tankmanCost(self):
        """
        @return: tankman studying cost
                        tmanCost -  ( tmanCostType, ), where
                        tmanCostType = {
                                        'roleLevel' : minimal role level after operation,
                                        'credits' : cost in credits,
                                        'gold' : cost in gold,
                                        'baseRoleLoss' : float in [0, 1], fraction of role to drop,
                                        'classChangeRoleLoss' : float in [0, 1], fraction of role to drop additionally if
                                                classes of self.vehicleTypeID and newVehicleTypeID are different,
                                        'isPremium' : tankman becomes premium,
                                        }.
                                List is sorted by role level.
        """
        value = self.__proxy.tankmanCost
        defaults = self.getValue('tankmanCost')
        if defaults is None:
            return value
        else:
            newValues = []
            for idx, cost in enumerate(value):
                default = defaults[idx] if len(defaults) > idx else {}
                newValue = cost.copy()
                newValue.update(default)
                newValues.append(newValue)

            return newValues

    @property
    def changeRoleCost(self):
        """
        @return: tankman change role cost in gold
        """
        return self.getValue('changeRoleCost', self.__proxy.changeRoleCost)

    @property
    def freeXPConversion(self):
        """
        @return: free experience to vehicle xp exchange rate and cost
                                ( discrecity, cost)
        """
        return self.getValue('freeXPConversion', self.__proxy.freeXPConversion)

    @property
    def passportChangeCost(self):
        """
        @return: tankman passport replace cost in gold
        """
        return self.getValue('passportChangeCost', self.__proxy.passportChangeCost)

    @property
    def passportFemaleChangeCost(self):
        """
        @return: tankman passport replace cost in gold
        """
        return self.getValue('femalePassportChangeCost', self.__proxy.passportFemaleChangeCost)

    @property
    def freeXPToTManXPRate(self):
        """
        @return: free experience to tankman experience exchange rate
        """
        return self.getValue('freeXPToTManXPRate', self.__proxy.freeXPToTManXPRate)

    def getItemsData(self):
        return self.getValue('items', self.__proxy.getItemsData())

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        value = self.getItemsData().get('vehicleCamouflagePriceFactors', {}).get(typeCompDescr)
        if value is None:
            return self.__proxy.getVehCamouflagePriceFactor(typeCompDescr)
        else:
            return value

    def getHornPriceFactor(self, hornID):
        value = self.getItemsData().get('vehicleHornPriceFactors', {}).get(hornID)
        if value is None:
            return self.__proxy.getVehCamouflagePriceFactor(hornID)
        else:
            return value

    def getEmblemsGroupPriceFactors(self):
        return self.getItemsData().get('playerEmblemGroupPriceFactors', self.__proxy.getEmblemsGroupPriceFactors())

    def getEmblemsGroupHiddens(self):
        return self.getItemsData().get('notInShopPlayerEmblemGroups', self.__proxy.getEmblemsGroupHiddens())

    def getInscriptionsGroupPriceFactors(self, nationID):
        value = self.getItemsData().get('inscriptionGroupPriceFactors', [])
        if len(value) <= nationID:
            return self.__proxy.getInscriptionsGroupPriceFactors(nationID)
        return value[nationID]

    def getInscriptionsGroupHiddens(self, nationID):
        value = self.getItemsData().get('notInShopInscriptionGroups', [])
        if len(value) <= nationID:
            return self.__proxy.getInscriptionsGroupHiddens(nationID)
        return value[nationID]

    def getCamouflagesPriceFactors(self, nationID):
        value = self.getItemsData().get('camouflagePriceFactors', [])
        if len(value) <= nationID:
            return self.__proxy.getCamouflagesPriceFactors(nationID)
        return value[nationID]

    def getCamouflagesHiddens(self, nationID):
        value = self.getItemsData().get('notInShopCamouflages', [])
        if len(value) <= nationID:
            return self.__proxy.getCamouflagesHiddens(nationID)
        return value[nationID]

    def getHornPrice(self, hornID):
        value = self.getItemsData().get('hornPrices', {}).get(hornID)
        if value is None:
            return self.__proxy.getHornPrice(hornID)
        else:
            return value

    @property
    def premiumCost(self):
        value = self.__proxy.premiumCost.copy()
        value.update(self.getValue('premiumCost', {}))
        return value

    @property
    def goodies(self):
        value = self.__proxy.goodies.copy()
        value.update(self.getValue('goodies', {}))
        return value

    @property
    def camouflageCost(self):
        value = self.__proxy.camouflageCost.copy()
        value.update(self.getValue('camouflageCost', {}))
        return value

    @property
    def playerInscriptionCost(self):
        value = self.__proxy.playerInscriptionCost.copy()
        value.update(self.getValue('playerInscriptionCost', {}))
        return value

    @property
    def playerEmblemCost(self):
        value = self.__proxy.playerEmblemCost.copy()
        value.update(self.getValue('playerEmblemCost', {}))
        return value
