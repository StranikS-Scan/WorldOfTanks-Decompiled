# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/ShopRequester.py
import weakref
from collections import namedtuple
from abc import ABCMeta, abstractmethod
import logging
import BigWorld
from adisp import async
from constants import WIN_XP_FACTOR_MODE, ARENA_BONUS_TYPE
from items import ItemsPrices
from goodies.goodie_constants import GOODIE_VARIETY, GOODIE_TARGET_TYPE, GOODIE_RESOURCE_TYPE
from goodies.goodie_helpers import getPremiumCost, getPriceWithDiscount, GoodieData
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from items.item_price import getNextSlotPrice, getNextBerthPackPrice
from post_progression_common import CUSTOM_ROLE_SLOT_CHANGE_PRICE
from post_progression_prices_common import getPostProgressionPrice
from skeletons.gui.shared.utils.requesters import IShopCommonStats, IShopRequester
from gui.shared.gui_items.gui_item_economics import ItemPrice
_logger = logging.getLogger(__name__)
_DEFAULT_EXCHANGE_RATE = 400
_DEFAULT_CRYSTAL_EXCHANGE_RATE = 200
_DEFAULT_SELL_PRICE_MODIF = 0.5
_DEFAULT_CLAN_CREATION_COST = 2500
_VehiclesRestoreConfig = namedtuple('_VehiclesRestoreConfig', 'restoreDuration restoreCooldown restorePriceModif')
_TankmenRestoreConfig = namedtuple('_TankmenRestoreConfig', 'freeDuration billableDuration cost limit')
_TargetData = namedtuple('_TargetData', 'targetType, targetValue, limit')
_ResourceData = namedtuple('_ResourceData', 'resourceType, value, isPercentage')
_ConditionData = namedtuple('_ConditionData', 'conditionType, value')
_TradeInData = namedtuple('_TradeInData', ['sellPriceFactor',
 'allowedVehicleLevels',
 'forbiddenVehicles',
 'minAcceptableSellPrice'])
_TradeInData.__new__.__defaults__ = (0,
 (),
 (),
 0)

class _NamedGoodieData(GoodieData):

    @staticmethod
    def __new__(cls, variety, target, enabled, lifetime, useby, counter, autostart, condition, resource):
        return GoodieData.__new__(cls, variety, _TargetData(*target) if target else None, enabled, lifetime, useby, counter, autostart, _ConditionData(*condition) if condition else None, _ResourceData(*resource) if resource else None)

    def getTargetValue(self):
        return int(self.target.targetValue.split('_')[1]) if self.target.targetType == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM else self.target.targetValue


class TradeInData(_TradeInData):
    __slots__ = ()

    @property
    def isEnabled(self):
        return self.sellPriceFactor > 0


class ShopCommonStats(IShopCommonStats):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getValue(self, key, defaultValue=None):
        pass

    def getPrices(self):
        try:
            return self.getItemsData()['itemPrices']
        except KeyError:
            return ItemsPrices()

    def getBoosterPrices(self):
        try:
            return self.getGoodiesData()['prices']
        except KeyError:
            return {}

    def getHiddens(self):
        try:
            return self.getItemsData()['notInShopItems']
        except KeyError:
            return set([])

    def getHiddenBoosters(self):
        try:
            return self.getGoodiesData()['notInShop']
        except KeyError:
            return set([])

    def getNotToBuyVehicles(self):
        try:
            return self.getItemsData()['vehiclesNotToBuy']
        except KeyError:
            return set([])

    def getVehicleRentPrices(self):
        try:
            return self.getItemsData()['vehiclesRentPrices']
        except KeyError:
            return {}

    def getVehiclesForGold(self):
        try:
            return self.getItemsData()['vehiclesToSellForGold']
        except KeyError:
            return set([])

    def getVehiclesSellPriceFactors(self):
        try:
            return self.getItemsData()['vehicleSellPriceFactors']
        except KeyError:
            return {}

    def getItemPrice(self, intCD):
        prices = self.getPrices()
        return Money(**prices.getPrices(intCD)) if intCD in prices else MONEY_UNDEFINED

    def getBoosterPricesTuple(self, boosterID):
        return self.getBoosterPrices().get(boosterID, tuple())

    def getOperationPrices(self):
        try:
            return self.getItemsData()['operationPrices']
        except KeyError:
            return {}

    def getItem(self, intCD):
        return (self.getItemPrice(intCD), intCD in self.getHiddens())

    def getAchievementReward(self, achievement, arenaType=ARENA_BONUS_TYPE.REGULAR):
        return None

    @property
    def revision(self):
        return self.getValue('rev', 0)

    @property
    def paidRemovalCost(self):
        cost = self.getValue('paidRemovalCost', {})
        return cost.get(Currency.GOLD, 10)

    @property
    def paidDeluxeRemovalCost(self):
        cost = self.getValue('paidDeluxeRemovalCost', {Currency.CRYSTAL: 100})
        return Money(**cost)

    @property
    def paidTrophyBasicRemovalCost(self):
        cost = self.getValue('paidTrophyBasicRemovalCost', {Currency.GOLD: 10})
        return Money(**cost)

    @property
    def paidTrophyUpgradedRemovalCost(self):
        cost = self.getValue('paidTrophyUpgradedRemovalCost', {Currency.GOLD: 10})
        return Money(**cost)

    @property
    def exchangeRate(self):
        return self.getValue('exchangeRate', _DEFAULT_EXCHANGE_RATE)

    @property
    def clanCreationCost(self):
        return self.getValue('clanCreationCost', _DEFAULT_CLAN_CREATION_COST)

    @property
    def crystalExchangeRate(self):
        return self.getValue('crystalExchangeRate', _DEFAULT_CRYSTAL_EXCHANGE_RATE)

    @property
    def exchangeRateForShellsAndEqs(self):
        return self.getValue('exchangeRateForShellsAndEqs', _DEFAULT_EXCHANGE_RATE)

    @property
    def sellPriceModif(self):
        return self.getValue('sellPriceModif', _DEFAULT_SELL_PRICE_MODIF)

    @property
    def vehiclesRestoreConfig(self):
        config = self.__getRestoreConfig().get('vehicles', {})
        return _VehiclesRestoreConfig(config.get('premiumDuration', 0), config.get('actionCooldown', 0), config.get('sellToRestoreFactor', 1.1))

    @property
    def tankmenRestoreConfig(self):
        config = self.__getRestoreConfig().get('tankmen', {})
        return _TankmenRestoreConfig(config.get('freeDuration', 0), config.get('creditsDuration', 0), Money(credits=config.get('creditsCost', 0)), config.get('limit', 100))

    def sellPriceModifiers(self, compDescr):
        sellPriceModif = self.sellPriceModif
        sellPriceFactors = self.getVehiclesSellPriceFactors()
        if compDescr in sellPriceFactors:
            modifiers = sellPriceFactors[compDescr]
        else:
            modifiers = sellPriceModif
        return (self.revision,
         self.exchangeRate,
         self.exchangeRateForShellsAndEqs,
         sellPriceModif,
         modifiers,
         compDescr in self.getVehiclesForGold())

    @property
    def slotsPrices(self):
        return self.getValue('slotsPrices', (0, [300]))

    def getVehicleSlotsPrice(self, currentSlotsCount):
        return getNextSlotPrice(currentSlotsCount, self.slotsPrices)

    @property
    def dropSkillsCost(self):
        return self.getValue('dropSkillsCost', {})

    @property
    def dailyXPFactor(self):
        return self.getValue('dailyXPFactor', 2)

    @property
    def winXPFactorMode(self):
        return self.getValue('winXPFactorMode', WIN_XP_FACTOR_MODE.DAILY)

    @property
    def berthsPrices(self):
        return self.getValue('berthsPrices', (0, 1, [300]))

    def getBattlePassCost(self):
        return Money(**self.getValue('battlePassCost', defaultValue={Currency.GOLD: 6500}))

    def getBattlePassLevelCost(self):
        return Money(**self.getValue('battlePassLevelCost', defaultValue={Currency.GOLD: 250}))

    def getTankmanBerthPrice(self, berthsCount):
        prices = self.berthsPrices
        goldCost = getNextBerthPackPrice(berthsCount, prices)
        return (Money(gold=goldCost), prices[1])

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        return self.getValue('isEnabledBuyingGoldShellsForCredits', False)

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        return self.getValue('isEnabledBuyingGoldEqsForCredits', False)

    @property
    def tankmanCost(self):
        return self.getValue('tankmanCost', tuple())

    @property
    def changeRoleCost(self):
        return self.getValue('changeRoleCost', 600)

    @property
    def freeXPConversion(self):
        return self.getValue('freeXPConversion', (25, 1))

    @property
    def freeXPToTManXPRate(self):
        return self.getValue('freeXPToTManXPRate', 10)

    def getItemsData(self):
        return self.getValue('items', {})

    def getGoodiesData(self):
        return self.getValue('goodies', {})

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        return self.getItemsData().get('vehicleCamouflagePriceFactors', {}).get(typeCompDescr)

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

    def getNotInShopProgressionLvlItems(self):
        return self.getItemsData().get('notInShopProgressionLvlItems', {})

    @property
    def premiumCost(self):
        return self.getValue('premiumCost', {})

    @property
    def goodies(self):
        return self.getGoodiesData().get('goodies', {})

    def getGoodieByID(self, discountID):
        return self.goodies.get(discountID, None)

    def getGoodiesByVariety(self, variety):
        return dict(((goodieID, item) for goodieID, item in self.goodies.iteritems() if item.variety == variety))

    @property
    def boosters(self):
        return self.getGoodiesByVariety(GOODIE_VARIETY.BOOSTER)

    @property
    def discounts(self):
        return self.getGoodiesByVariety(GOODIE_VARIETY.DISCOUNT)

    @property
    def demountKits(self):
        return self.getGoodiesByVariety(GOODIE_VARIETY.DEMOUNT_KIT)

    def getPremiumPacketCost(self, days):
        return self.premiumCost.get(days)

    @property
    def camouflageCost(self):
        return self.getValue('camouflageCost', {})

    def getCamouflageCost(self, days=0):
        return self.camouflageCost.get(days)

    @property
    def playerInscriptionCost(self):
        return self.getValue('playerInscriptionCost', {})

    def getInscriptionCost(self, days=0):
        return self.playerInscriptionCost.get(days)

    @property
    def playerEmblemCost(self):
        return self.getValue('playerEmblemCost', {})

    def getEmblemCost(self, days=0):
        return self.playerEmblemCost.get(days)

    @property
    def tradeIn(self):
        tradeInData = self.getValue('tradeIn')
        return TradeInData(**tradeInData) if tradeInData is not None else TradeInData()

    @property
    def personalTradeIn(self):
        return self.getValue('personalTradeIn')

    def __getRestoreConfig(self):
        return self.getValue('restore_config', {})


class ShopRequester(AbstractSyncDataRequester, ShopCommonStats, IShopRequester):

    def __init__(self, goodies):
        super(ShopRequester, self).__init__()
        self.defaults = DefaultShopRequester({}, self)
        self._goodies = weakref.proxy(goodies)

    def clear(self):
        self.defaults.clear()
        super(ShopRequester, self).clear()

    def getValue(self, key, defaultValue=None):
        return self.getCacheValue(key, defaultValue)

    def _response(self, resID, invData, callback=None):
        if invData is not None:
            self.defaults.update(invData.get('defaults'))
        super(ShopRequester, self)._response(resID, invData, callback)
        return

    @async
    def _requestCache(self, callback):
        BigWorld.player().shop.getCache(lambda resID, value, rev: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        data = dict(data)
        if 'goodies' in data:
            goodies = data['goodies'].get('goodies', {})
            formattedGoodies = {}
            for goodieID, goodieData in goodies.iteritems():
                formattedGoodies[goodieID] = _NamedGoodieData(*goodieData)

            data['goodies']['goodies'] = formattedGoodies
        return data

    def getPremiumCostWithDiscount(self, premiumPacketDiscounts=None):
        discounts = premiumPacketDiscounts or self.personalPremiumPacketsDiscounts
        premiumCostWithDiscount = self.premiumCost.copy()
        for discount in discounts.itervalues():
            premiumCostWithDiscount[discount.getTargetValue()] = getPremiumCost(self.premiumCost, discount)

        return premiumCostWithDiscount

    def isActionOnPremium(self):
        premiumCost = self.premiumCost
        defaultPremiumCost = self.defaults.premiumCost
        for days, price in premiumCost.iteritems():
            if defaultPremiumCost[days] != price:
                return True

        return False

    def getTankmanCostWithDefaults(self):
        from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
        from gui.shared.tooltips.formatters import packActionTooltipData
        shopPrices = self.tankmanCost
        defaultPrices = self.defaults.tankmanCost
        action = []
        tmanCost = []
        for idx, price in enumerate(shopPrices):
            data = price.copy()
            shopPrice = Money(**price)
            defaultPrice = Money(**defaultPrices[idx])
            actionData = None
            if shopPrice != defaultPrice:
                key = '{}TankmanCost'.format(shopPrice.getCurrency(byWeight=True))
                actionData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, key, True, shopPrice, defaultPrice)
            tmanCost.append(data)
            action.append(actionData)

        return (tmanCost, action)

    def getVehicleSlotsPrice(self, currentSlotsCount):
        price = super(ShopRequester, self).getVehicleSlotsPrice(currentSlotsCount)
        slotGoodies = self.personalSlotDiscounts
        if slotGoodies:
            bestGoody = self.bestGoody(slotGoodies)
            return getPriceWithDiscount(price, bestGoody.resource)
        return price

    def getVehicleSlotsItemPrice(self, currentSlotsCount):
        defPrice = self.defaults.getVehicleSlotsPrice(currentSlotsCount)
        price = self.getVehicleSlotsPrice(currentSlotsCount)
        slotGoodies = self.personalSlotDiscounts
        if slotGoodies:
            bestGoody = self.bestGoody(slotGoodies)
            price = getPriceWithDiscount(price, bestGoody.resource)
        return ItemPrice(price=Money.makeFrom(Currency.GOLD, price), defPrice=Money.makeFrom(Currency.GOLD, defPrice))

    def getTankmanCostItemPrices(self):
        result = []
        defaultCost = self.defaults.tankmanCost
        countItems = len(defaultCost)
        if countItems == len(self.tankmanCostWithGoodyDiscount):
            for idx in xrange(countItems):
                commanderLevelsPrices = {}
                commanderLevelsDefPrices = {}
                for currency in Currency.ALL:
                    defPriceCurrency = defaultCost[idx].get(currency, None)
                    if defPriceCurrency:
                        commanderLevelsPrices[currency] = self.tankmanCostWithGoodyDiscount[idx].get(currency, None)
                        commanderLevelsDefPrices[currency] = defPriceCurrency

                price = Money(**commanderLevelsPrices)
                defPrice = Money(**commanderLevelsDefPrices)
                itemPrice = ItemPrice(price=price, defPrice=defPrice)
                result.append(itemPrice)

        else:
            _logger.error('len(self.tankmanCost) must be equal to len(self.tankmanCostWithGoodyDiscount)')
        return result

    @property
    def tankmanCostWithGoodyDiscount(self):
        prices = self.tankmanCost
        tankmanGoodies = self.personalTankmanDiscounts
        if tankmanGoodies:
            bestGoody = self.bestGoody(tankmanGoodies)
            return self.__applyGoodyToStudyCost(prices, bestGoody)
        return prices

    @property
    def freeXPConversionLimit(self):
        goody = self.bestGoody(self.personalXPExchangeDiscounts)
        return goody.target.limit * self.defaults.freeXPConversion[0] if goody else None

    @property
    def freeXPConversionWithDiscount(self):
        goody = self.bestGoody(self.personalXPExchangeDiscounts)
        rate = self.freeXPConversion
        return (rate[0], getPriceWithDiscount(rate[1], goody.resource)) if goody else rate

    @property
    def isXPConversionActionActive(self):
        goody = self.bestGoody(self.personalXPExchangeDiscounts)
        return self.freeXPConversion[0] > self.defaults.freeXPConversion[0] or goody is not None

    @property
    def isCreditsConversionActionActive(self):
        return self.exchangeRate != self.defaults.exchangeRate

    @property
    def personalPremiumPacketsDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_PREMIUM)

    @property
    def personalSlotDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_SLOT)

    @property
    def personalTankmanDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN)

    @property
    def personalXPExchangeDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION)

    @property
    def personalVehicleDiscounts(self):
        return self.__personalDiscountsByTarget(GOODIE_TARGET_TYPE.ON_BUY_VEHICLE)

    def getVehicleDiscountDescriptions(self):
        return self.__getDiscountsDescriptionsByTarget(GOODIE_TARGET_TYPE.ON_BUY_VEHICLE)

    def getPersonalVehicleDiscountPrice(self, typeCompDescr):
        defaultPrice = self.defaults.getItemPrice(typeCompDescr)
        currency = defaultPrice.getCurrency()
        personalVehicleDiscountPrice = None
        for _, discount in self.personalVehicleDiscounts.iteritems():
            if discount.getTargetValue() == typeCompDescr:
                discountPrice = self.__getPriceWithDiscount(defaultPrice, discount.resource)
                if discountPrice.isDefined() and (personalVehicleDiscountPrice is None or discountPrice.get(currency) < personalVehicleDiscountPrice.get(currency)):
                    personalVehicleDiscountPrice = discountPrice

        return personalVehicleDiscountPrice

    def bestGoody(self, goodies):
        if goodies:
            _, goody = sorted(goodies.iteritems(), key=lambda (_, goody): goody.resource[1])[-1]
            return goody
        else:
            return None

    def customRoleSlotChangeCost(self, vehType, isRaw=False):
        cost = getPostProgressionPrice(CUSTOM_ROLE_SLOT_CHANGE_PRICE, vehType, self._data)
        return cost if isRaw else Money(**cost)

    def __getDiscountsDescriptionsByTarget(self, targetType):
        return dict(((discountID, item) for discountID, item in self.discounts.iteritems() if item.target.targetType == targetType and item.enabled))

    def __applyGoodyToStudyCost(self, prices, goody):

        def convert(price):
            newPrice = price.copy()
            if price['isPremium']:
                newPrice[Currency.GOLD] = getPriceWithDiscount(price[Currency.GOLD], goody.resource)
            return newPrice

        return tuple(map(convert, prices))

    def __personalDiscountsByTarget(self, targetType):
        discounts = self.__getDiscountsDescriptionsByTarget(targetType)
        return dict(((discountID, item) for discountID, item in discounts.iteritems() if discountID in self._goodies.goodies))

    @staticmethod
    def __getPriceWithDiscount(price, resourceData):
        resourceType, _, _ = resourceData
        if resourceType == GOODIE_RESOURCE_TYPE.CREDITS:
            return Money(credits=getPriceWithDiscount(price.credits, resourceData))
        return Money(gold=getPriceWithDiscount(price.gold, resourceData)) if resourceType == GOODIE_RESOURCE_TYPE.GOLD else MONEY_UNDEFINED


class DefaultShopRequester(ShopCommonStats):

    def __init__(self, cache, proxy):
        self.__cache = cache.copy()
        self.__proxy = weakref.proxy(proxy)

    def clear(self):
        _logger.debug('Clearing shop defaults.')
        self.__cache.clear()

    def update(self, cache):
        if cache is None:
            cache = {}
        self.clear()
        self.__cache = cache.copy()
        return

    def getValue(self, key, defaultValue=None):
        return self.__cache[key] if key in self.__cache else defaultValue

    @property
    def revision(self):
        return self.__proxy.revision

    def getPrices(self):
        return self.getItemsData().get('itemPrices', self.__proxy.getPrices())

    def getBoosterPrices(self):
        return self.getGoodiesData().get('prices', self.__proxy.getBoosterPrices())

    def getHiddens(self):
        return self.getItemsData().get('notInShopItems', self.__proxy.getHiddens())

    def getHiddenBoosters(self):
        return self.getGoodiesData().get('notInShop', self.__proxy.getHiddenBoosters())

    def getNotToBuyVehicles(self):
        return self.getItemsData().get('vehiclesNotToBuy', self.__proxy.getNotToBuyVehicles())

    def getVehicleRentPrices(self):
        return self.getItemsData().get('vehiclesRentPrices', self.__proxy.getVehicleRentPrices())

    def getVehiclesForGold(self):
        return self.getItemsData().get('vehiclesToSellForGold', {})

    def getVehiclesSellPriceFactors(self):
        return self.getItemsData().get('vehicleSellPriceFactors', {})

    def getItemPrice(self, intCD):
        prices = self.getPrices()
        return Money(**prices.getPrices(intCD)) if intCD in prices else self.__proxy.getItemPrice(intCD)

    def getBoosterPricesTuple(self, boosterID):
        return self.getBoosterPrices().get(boosterID, self.__proxy.getBoosterPricesTuple(boosterID))

    def getOperationPrices(self):
        return self.getItemsData().get('operationPrices', self.__proxy.getOperationPrices())

    @property
    def paidRemovalCost(self):
        cost = self.getValue('paidRemovalCost')
        return self.__proxy.paidRemovalCost if cost is None else cost.get(Currency.GOLD, 10)

    @property
    def paidDeluxeRemovalCost(self):
        cost = self.getValue('paidDeluxeRemovalCost')
        return self.__proxy.paidDeluxeRemovalCost if cost is None else Money(**cost)

    @property
    def paidTrophyBasicRemovalCost(self):
        cost = self.getValue('paidTrophyBasicRemovalCost')
        return self.__proxy.paidTrophyBasicRemovalCost if cost is None else Money(**cost)

    @property
    def paidTrophyUpgradedRemovalCost(self):
        cost = self.getValue('paidTrophyUpgradedRemovalCost')
        return self.__proxy.paidTrophyUpgradedRemovalCost if cost is None else Money(**cost)

    @property
    def exchangeRate(self):
        return self.getValue('exchangeRate', self.__proxy.exchangeRate)

    @property
    def clanCreationCost(self):
        return self.getValue('clanCreationCost', self.__proxy.clanCreationCost)

    @property
    def exchangeRateForShellsAndEqs(self):
        return self.getValue('exchangeRateForShellsAndEqs', self.__proxy.exchangeRateForShellsAndEqs)

    @property
    def sellPriceModif(self):
        return self.getValue('sellPriceModif', self.__proxy.sellPriceModif)

    @property
    def slotsPrices(self):
        return self.getValue('slotsPrices', self.__proxy.slotsPrices)

    @property
    def dropSkillsCost(self):
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
        return self.getValue('dailyXPFactor', self.__proxy.dailyXPFactor)

    @property
    def winXPFactorMode(self):
        return self.getValue('winXPFactorMode', self.__proxy.winXPFactorMode)

    @property
    def berthsPrices(self):
        return self.getValue('berthsPrices', self.__proxy.berthsPrices)

    def getBattlePassCost(self):
        cost = self.getValue('battlePassCost')
        return self.__proxy.getBattlePassCost() if cost is None else Money(**cost)

    def getBattlePassLevelCost(self):
        cost = self.getValue('battlePassLevelCost')
        return self.__proxy.getBattlePassLevelCost() if cost is None else Money(**cost)

    @property
    def isEnabledBuyingGoldShellsForCredits(self):
        return self.getValue('isEnabledBuyingGoldShellsForCredits', self.__proxy.isEnabledBuyingGoldShellsForCredits)

    @property
    def isEnabledBuyingGoldEqsForCredits(self):
        return self.getValue('isEnabledBuyingGoldEqsForCredits', self.__proxy.isEnabledBuyingGoldEqsForCredits)

    @property
    def tankmanCost(self):
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
        return self.getValue('changeRoleCost', self.__proxy.changeRoleCost)

    @property
    def freeXPConversion(self):
        return self.getValue('freeXPConversion', self.__proxy.freeXPConversion)

    @property
    def freeXPToTManXPRate(self):
        return self.getValue('freeXPToTManXPRate', self.__proxy.freeXPToTManXPRate)

    def getItemsData(self):
        return self.getValue('items', self.__proxy.getItemsData())

    def getGoodiesData(self):
        return self.getValue('goodies', self.__proxy.getGoodiesData())

    def getVehCamouflagePriceFactor(self, typeCompDescr):
        value = self.getItemsData().get('vehicleCamouflagePriceFactors', {}).get(typeCompDescr)
        return self.__proxy.getVehCamouflagePriceFactor(typeCompDescr) if value is None else value

    def getEmblemsGroupPriceFactors(self):
        return self.getItemsData().get('playerEmblemGroupPriceFactors', self.__proxy.getEmblemsGroupPriceFactors())

    def getEmblemsGroupHiddens(self):
        return self.getItemsData().get('notInShopPlayerEmblemGroups', self.__proxy.getEmblemsGroupHiddens())

    def getInscriptionsGroupPriceFactors(self, nationID):
        value = self.getItemsData().get('inscriptionGroupPriceFactors', [])
        return self.__proxy.getInscriptionsGroupPriceFactors(nationID) if len(value) <= nationID else value[nationID]

    def getInscriptionsGroupHiddens(self, nationID):
        value = self.getItemsData().get('notInShopInscriptionGroups', [])
        return self.__proxy.getInscriptionsGroupHiddens(nationID) if len(value) <= nationID else value[nationID]

    def getCamouflagesPriceFactors(self, nationID):
        value = self.getItemsData().get('camouflagePriceFactors', [])
        return self.__proxy.getCamouflagesPriceFactors(nationID) if len(value) <= nationID else value[nationID]

    def getCamouflagesHiddens(self, nationID):
        value = self.getItemsData().get('notInShopCamouflages', [])
        return self.__proxy.getCamouflagesHiddens(nationID) if len(value) <= nationID else value[nationID]

    @property
    def premiumCost(self):
        value = self.__proxy.premiumCost.copy()
        value.update(self.getValue('premiumCost', {}))
        return value

    @property
    def goodies(self):
        return self.getGoodiesData().get('goodies', self.__proxy.goodies)

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
