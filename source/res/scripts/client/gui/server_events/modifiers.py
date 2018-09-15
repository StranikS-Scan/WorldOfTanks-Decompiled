# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/modifiers.py
import operator
from collections import defaultdict, namedtuple
from abc import ABCMeta, abstractmethod
import constants
from gui.shared.economics import getActionPrc
import nations
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_WARNING
from helpers import dependency
from items import vehicles, ITEM_TYPE_NAMES
from shared_utils import BoundMethodWeakref as bwr, CONST_CONTAINER
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.server_events import formatters
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
_VEH_TYPE_IDX = 1
_VEH_TYPE_NAME = ITEM_TYPE_NAMES[_VEH_TYPE_IDX]
_DT = formatters.DISCOUNT_TYPE
_MULTIPLIER = 'Multiplier'
_COMMON_CRITERIA = REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.HIDDEN

class ACTION_MODIFIER_TYPE(CONST_CONTAINER):
    DISCOUNT = 1
    SELLING = 2
    RENT = 3
    AVAILABILITY = 4


class ACTION_SECTION_TYPE(CONST_CONTAINER):
    ECONOMICS = 1
    ALL = 2
    ITEM = 3
    CUSTOMIZATION = 4
    BOOSTER = 5
    ALL_BOOSTERS = 6


_ActionDiscountValue = namedtuple('_ActionDiscountValue', 'discountName, discountValue, discountType')

def _getDiscountByValue(value, default):
    return int(default - value)


def _getPercentDiscountByValue(value, default):
    return getActionPrc(value, default)


def _getDiscountByMultiplier(mult, default):
    return int(default - default * float(mult))


def _getPercentDiscountByMultiplier(mult, default):
    price = int(round(float(mult) * default))
    return getActionPrc(price, default)


def _prepareVehData(vehsList, discounts=None):
    discounts = discounts or {}
    result = []
    for v in vehsList:
        discount, discountType = discounts.get(v, (None, None))
        result.append((v, (True, discount, discountType)))

    return result


class ActionModifier(object):

    def __init__(self, name, params, modType, section=ACTION_SECTION_TYPE.ECONOMICS, itemType=None):
        self._name = name
        self._params = params
        self._type = modType
        self._itemType = itemType
        self._section = section
        self.__extParams = []
        self.__cachedValue = None
        return

    def getName(self):
        return self._name

    def getParamName(self):
        return self.getName()

    def getParamValue(self):
        pass

    def getParams(self):
        return self._params

    def getType(self):
        return self._type

    def getItemType(self):
        return self._itemType

    def getSection(self):
        return self._section

    def getValues(self, action):
        return {}

    def parse(self):
        if not self.__cachedValue:
            self.__cachedValue = self._parse()
            for p in self.__extParams:
                self.__cachedValue.update(p)

        return self.__cachedValue

    def packDiscounts(self, sorting=True):
        """Grab all discounts obj for current modifier
        :param sorting: if value equals True than list should be sorted,
            otherwise - do not sort list of discounts. For example, if user finds
            max discount, sorting is pointless.
        """
        return {}

    def update(self, modifier):
        p = modifier.parse()
        if p is not None:
            self.__extParams.append(p)
        return

    def splitModifiers(self):
        return [self]

    def _parse(self):
        return None

    def _calcDiscountValue(self, value, default):
        return _getPercentDiscountByValue(float(value), default)

    @abstractmethod
    def getDefaultParamValue(self):
        return None

    def getDefaultDiscountType(self):
        return _DT.PERCENT

    @classmethod
    def _calculateDiscount(cls, paramName, discountVal, defaultVal, discountType, discountValueCalculator=None):
        if isinstance(discountVal, tuple):
            discountVal = discountVal[1]
        if not type(float):
            discountVal = float(discountVal)
        calculator = discountValueCalculator or cls._calcDiscountValue
        value = calculator(discountVal, defaultVal)
        return _ActionDiscountValue(discountValue=value, discountType=discountType)


class _DiscountsListAction(ActionModifier):
    __meta__ = ABCMeta
    MAX_VEH_COUNT = 10
    DEFAULT_PRICE_MULT = 1.0

    @abstractmethod
    def _getParamName(self, idx):
        pass

    @abstractmethod
    def _getMultName(self, idx):
        pass

    @abstractmethod
    def _makeResultItem(self, paramValue):
        pass

    def _parse(self):
        result = {}
        for idx in xrange(self.MAX_VEH_COUNT):
            paramName = self._getParamName(idx)
            if paramName in self._params:
                item = self._makeResultItem(self._params[paramName])
                if item is not None:
                    result[item] = float(self._params.get(self._getMultName(idx), self.DEFAULT_PRICE_MULT))

        return result

    def getValues(self, action):
        result = {}
        for veh, value in self.parse().iteritems():
            result[veh.intCD] = [(value, action.getID())]

        return result

    def getDefaultParamValue(self):
        return self.DEFAULT_PRICE_MULT

    def getDefaultDiscountType(self):
        return _DT.MULTIPLIER


class _PriceOpAbstract(object):
    __meta__ = ABCMeta
    itemsCache = dependency.descriptor(IItemsCache)

    @abstractmethod
    def _getDiscountParams(self, item, value):
        pass


class _BuyPriceSet(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        for currency in Currency.BY_WEIGHT:
            setValue = item.buyPrices.itemPrice.defPrice.get(currency)
            if setValue:
                return (_getPercentDiscountByValue(value, setValue), currency)

        return (_getPercentDiscountByValue(value, item.buyPrices.itemPrice.defPrice.credits), _DT.CREDITS)


class _RentPriceSet(_PriceOpAbstract):

    def _getRentDiscountParams(self, item, package, value):
        rentPackage = item.getRentPackage(package)
        if rentPackage:
            defaultGoldRentPrice = rentPackage.get('defaultRentPrice', MONEY_UNDEFINED).gold
            if defaultGoldRentPrice:
                return (_getPercentDiscountByValue(value, defaultGoldRentPrice), _DT.GOLD)
        return (_getPercentDiscountByValue(value, 0), _DT.CREDITS)


class _BuyPriceMul(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        return (_getPercentDiscountByMultiplier(value, item.buyPrices.itemPrice.defPrice.gold), _DT.GOLD) if item.buyPrices.itemPrice.defPrice.isSet(Currency.GOLD) else (_getPercentDiscountByMultiplier(value, item.buyPrices.itemPrice.defPrice.getSignValue(Currency.CREDITS)), _DT.PERCENT)


class _RentPriceMul(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        if item.rentPackages:
            defaultRentPrice = item.rentPackages[0].get('defaultRentPrice', MONEY_UNDEFINED)
            for currency in Currency.BY_WEIGHT:
                setValue = defaultRentPrice.get(currency)
                if setValue:
                    return (_getPercentDiscountByMultiplier(value, setValue), currency)

        return (_getPercentDiscountByMultiplier(value, 0), _DT.CREDITS)


class _SellPriceMul(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        isForGold, value = value
        if item.buyPrices.itemPrice.price.isSet(Currency.GOLD):
            if isForGold:
                return (int(item.buyPrices.itemPrice.price.gold * float(value)), _DT.GOLD)
            creditsPrice = item.buyPrices.itemPrice.price.gold * self.itemsCache.items.shop.exchangeRate
            return (int(creditsPrice * float(value)), _DT.CREDITS)
        return (int(item.buyPrices.itemPrice.price.getSignValue(Currency.CREDITS) * float(value)), _DT.CREDITS)


class _ItemsPrice(_DiscountsListAction, _PriceOpAbstract):

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.DISCOUNT, section=ACTION_SECTION_TYPE.ITEM, itemType=None):
        super(_ItemsPrice, self).__init__(name, params, modType, section, itemType)

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for item, value in items:
            dv, dt = self._getDiscountParams(item, value)
            result[item.intCD] = _ActionDiscountValue(discountName=item, discountValue=dv, discountType=_DT.PERCENT)

        return result

    def _getParamName(self, idx):
        return 'itemName%d' % idx

    def _getMultName(self, idx):
        return 'price%d' % idx


class _SplitByCurrency(ActionModifier):

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.DISCOUNT, section=ACTION_SECTION_TYPE.ITEM, itemType=None):
        super(_SplitByCurrency, self).__init__(name, params, modType, section, itemType)
        self._paramName = None
        return

    def splitModifiers(self):
        """Split economic action into single steps
        :return: list of economic steps (set_*, mul_*)
        """
        res = []
        for paramName, paramValue in self._params.iteritems():
            obj = self.__class__(self.getName(), {paramName: paramValue})
            obj.setParamName(paramName)
            res.append(obj)

        return res

    def setParamName(self, paramName):
        self._paramName = paramName

    def getParamName(self):
        if self._itemType in GUI_ITEM_TYPE.ALL() and self._paramName is not None:
            itemName = GUI_ITEM_TYPE_NAMES[self._itemType]
            return '/'.join([itemName, self._paramName])
        else:
            return self.getName()

    def getDefaultParamValue(self):
        return None


class _ItemsPriceAll(ActionModifier):
    itemsCache = dependency.descriptor(IItemsCache)
    __meta__ = ABCMeta
    DEFAULT_PRICE_MULT = 1.0

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.DISCOUNT, section=ACTION_SECTION_TYPE.ALL, itemType=None):
        super(_ItemsPriceAll, self).__init__(name, params, modType, section, itemType)

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for (_, item), value in items:
            result[item.intCD] = _ActionDiscountValue(discountName=item, discountValue=int(round((1 - float(value)) * 100)), discountType=_DT.PERCENT)

        return result

    def _parse(self):
        nation = self._params.get(self._getNationName())
        goldPriceMult = self._params.get(self._getGoldMultName())
        creditsPriceMult = self._params.get(self._getCreditsMultName())
        result = self._getConditionResult(nation, goldPriceMult, creditsPriceMult, self._getRequestCriteria())
        return result

    def _getRequestCriteria(self):
        return _COMMON_CRITERIA

    def _getConditionResult(self, nation, goldPriceMult, creditsPriceMult, criteria):
        result = {}
        for v in self.itemsCache.items.getItems(itemTypeID=self._itemType, criteria=criteria).itervalues():
            if v.buyPrices.itemPrice.price.isSet(Currency.GOLD) and goldPriceMult is not None:
                result[nation, v] = float(goldPriceMult)
            if v.buyPrices.itemPrice.price.isSet(Currency.CREDITS) and creditsPriceMult is not None:
                result[nation, v] = float(creditsPriceMult)

        return result

    def _getGoldMultName(self):
        pass

    def _getCreditsMultName(self):
        pass

    def _getNationName(self):
        pass

    def _packMultiplier(self, multName, multVal):
        return _ActionDiscountValue(discountName=multName, discountValue=int(round((1 - float(multVal)) * 100)), discountType=_DT.PERCENT)

    def getValues(self, action):
        result = defaultdict(list)
        parsedValue = self.parse()
        if parsedValue:
            for (nation, multType), value in parsedValue.iteritems():
                if nation is None:
                    nation = nations.NONE_INDEX
                else:
                    nation = nations.INDICES[nation]
                result[nation].append(((multType, value), action.getID()))

        return result


@abstractmethod
class _VehiclePrice(_ItemsPrice):

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.DISCOUNT, section=ACTION_SECTION_TYPE.ITEM):
        super(_VehiclePrice, self).__init__(name, params, modType, section, GUI_ITEM_TYPE.VEHICLE)

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for v, value in items:
            dv, dt = self._getDiscountParams(v, value)
            dt = dt if self.getType() == ACTION_MODIFIER_TYPE.SELLING else _DT.PERCENT
            result[v.intCD] = _ActionDiscountValue(discountName=v, discountValue=dv, discountType=dt)

        return result

    def _makeResultItem(self, vehName):
        try:
            if ':' in vehName:
                vehIDs = vehicles.g_list.getIDsByName(vehName)
            else:
                vehIDs = vehicles.g_list.getIDsByVehName(vehName)
            vehTypeCompDescr = vehicles.makeIntCompactDescrByID(_VEH_TYPE_NAME, *vehIDs)
            return self.itemsCache.items.getItemByCD(vehTypeCompDescr)
        except Exception:
            LOG_ERROR('There is error while getting vehicle item', vehName)
            LOG_CURRENT_EXCEPTION()

        return None

    def _getParamName(self, idx):
        return 'vehName%d' % idx


@abstractmethod
class _VehicleRentPrice(_VehiclePrice):

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.RENT, section=ACTION_SECTION_TYPE.ITEM):
        super(_VehicleRentPrice, self).__init__(name, params, modType=modType, section=section)

    def packDiscounts(self, sorting=True):
        res = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for (vehicle, package), value in items:
            dv, _ = self._getDiscountParams(vehicle, value)
            res[vehicle.intCD, package] = _ActionDiscountValue(discountName=vehicle, discountValue=dv, discountType=_DT.PERCENT)

        return res

    def _parse(self):
        result = {}
        for idx in xrange(self.MAX_VEH_COUNT):
            paramName = self._getParamName(idx)
            if paramName in self._params:
                item = self._makeResultItem(self._params[paramName])
                if item is not None:
                    for rentPackage in item.rentPackages:
                        rentDays = rentPackage['days']
                        result[item, rentDays] = float(self._params.get(self._getMultName(idx), self.DEFAULT_PRICE_MULT))

        return result

    def getValues(self, action):
        result = {}
        for (vehicle, package), value in self.parse().iteritems():
            result[vehicle.intCD, package] = [(value, action.getID())]

        return result


class _EquipmentPrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_EquipmentPrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.EQUIPMENT)

    def _makeResultItem(self, eqName):
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.equipmentIDs().get(eqName)
            if idx is not None:
                return self.itemsCache.items.getItemByCD(vehCache.equipments()[idx].compactDescr)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


class _OptDevicePrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_OptDevicePrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.OPTIONALDEVICE)

    def _makeResultItem(self, devName):
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.optionalDeviceIDs().get(devName)
            if idx is not None:
                return self.itemsCache.items.getItemByCD(vehCache.optionalDevices()[idx].compactDescr)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


class _ShellPrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_ShellPrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.SHELL)

    def _getParamName(self, idx):
        return 'shellName%d' % idx

    def _makeResultItem(self, shellName):
        shellNation, shellName = shellName.split(':')
        shellNation = nations.INDICES[shellNation]
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.shellIDs(shellNation).get(shellName)
            if idx is not None:
                return self.itemsCache.items.getItemByCD(vehCache.shells(shellNation)[idx].compactDescr)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


_ECONOMICS_SET_EXCLUDE_IN_GUI = ('dailyXPFactor', 'exchangeRateForShellsAndEqs')
_ECONOMICS_SET_EXCLUDE_IN_PARCING = ('tradeInAllowedVehicleLevels', 'tradeInForbiddenVehicles', 'freeXPConversionDiscrecitydailyXPFactor')

class EconomicsSet(ActionModifier):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, name, params, paramName='', paramValue=''):
        super(EconomicsSet, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT)
        self._paramName = paramName
        self._paramValue = paramValue
        self.__handlers = {'premiumPacket1Cost': bwr(self.handlerPremiumPacket1),
         'premiumPacket3Cost': bwr(self.handlerPremiumPacket3),
         'premiumPacket7Cost': bwr(self.handlerPremiumPacket7),
         'premiumPacket30Cost': bwr(self.handlerPremiumPacket30),
         'premiumPacket180Cost': bwr(self.handlerPremiumPacket180),
         'premiumPacket360Cost': bwr(self.handlerPremiumPacket360),
         'freeXPConversionDiscrecity': bwr(self.handlerFreeXPConversionDiscrecity),
         'exchangeRate': bwr(self.handlerExchangeRate),
         'exchangeRateForShellsAndEqs': bwr(self.handlerExchangeRateForShellsAndEqs),
         'slotsPrices': bwr(self.handlerSlotsPrices),
         'creditsTankmanCost': bwr(self.handlerCreditsTankmanCost),
         'goldTankmanCost': bwr(self.handlerGoldTankmanCost),
         'changeRoleCost': bwr(self.handlerChangeRoleCost),
         'creditsDropSkillsCost': bwr(self.handlerCreditsDropSkillsCost),
         'goldDropSkillsCost': bwr(self.handlerGoldDropSkillsCost),
         'clanCreationCost': bwr(self.handlerClanCreationCost),
         'paidRemovalCost': bwr(self.handlerPaidRemovalCost),
         'paidDeluxeRemovalCost': bwr(self.handlerPaidDeluxeRemovalCost),
         'berthsPrices': bwr(self.handlerBerthsPrices),
         'passportChangeCost': bwr(self.handlerPassportChangeCost),
         'femalePassportChangeCost': bwr(self.handlerFemalePassportChangeCost),
         'freeXPToTManXPRate': bwr(self.handlerFreeXPToTManXPRate),
         'camouflagePacketInfCost': bwr(self.handlerCamouflagePacketInfCost),
         'camouflagePacket7Cost': bwr(self.handlerCamouflagePacket7Cost),
         'camouflagePacket30Cost': bwr(self.handlerCamouflagePacket30Cost),
         'inscriptionPacketInfCost': bwr(self.handlerInscriptionPacketInfCost),
         'inscriptionPacket7Cost': bwr(self.handlerInscriptionPacket7Cost),
         'inscriptionPacket30Cost': bwr(self.handlerInscriptionPacket30Cost),
         'emblemPacketInfCost': bwr(self.handlerEmblemPacketInfCost),
         'emblemPacket7Cost': bwr(self.handlerEmblemPacket7Cost),
         'emblemPacket30Cost': bwr(self.handlerEmblemPacket30Cost),
         'tradeInSellPriceFactor': bwr(self.handlerTradeInSellPriceFactor)}

    def getParamName(self):
        return self._wrapParamName(self._paramName)

    def getParamValue(self):
        return self._paramValue

    def packDiscounts(self, sorting=True):
        """Calculate discount for specific step
        :return: _ActionDiscountValue
        """
        data = self.parse()
        for sectionName in data.keys():
            wrappedName = self._wrapParamName(sectionName)
            if wrappedName in self.__handlers:
                try:
                    fResult = self.__handlers[wrappedName](data[sectionName])
                    if fResult:
                        return {wrappedName: fResult}
                except Exception:
                    LOG_ERROR('Error while calculating economics discount', sectionName, wrappedName)
                    LOG_CURRENT_EXCEPTION()

        return None

    def splitModifiers(self):
        """Split economic action into single steps
        :return: list of economic steps (set_*, mul_*)
        """
        res = []
        for k, v in self._params.iteritems():
            if k not in _ECONOMICS_SET_EXCLUDE_IN_GUI:
                obj = self.__class__(self.getName(), {k: v}, paramName=k, paramValue=v)
                res.append(obj)

        return res

    def _parse(self):
        result = {}
        for k, v in self._params.iteritems():
            if k in _ECONOMICS_SET_EXCLUDE_IN_PARCING:
                continue
            try:
                result[k] = float(v)
            except ValueError as ex:
                LOG_WARNING('There is error while converting action set_Economics param', ex.message)

        return result

    def _wrapParamName(self, name):
        return '{}/{}'.format(name, self.getParamValue()) if name == 'winXPFactorMode' else name

    @classmethod
    def _calcCustomizationDiscountValue(cls, value, default):
        return int(100 * _getDiscountByValue(int(value), default) / default)

    def handlerSlotsPrices(self, value):
        default = self.itemsCache.items.shop.defaults.getVehicleSlotsPrice(self.itemsCache.items.stats.vehicleSlots)
        return self._calculateDiscount('slotsPrices', value, default, _DT.PERCENT)

    def handlerBerthsPrices(self, value):
        default, _ = self.itemsCache.items.shop.defaults.getTankmanBerthPrice(self.itemsCache.items.stats.tankmenBerthsCount)
        return self._calculateDiscount('berthsPrices', value, default.gold, _DT.PERCENT)

    def handlerCreditsTankmanCost(self, value):
        tankmanCost = self.itemsCache.items.shop.defaults.tankmanCost
        return self._calculateDiscount('creditsTankmanCost', value, tankmanCost[1][Currency.CREDITS], _DT.PERCENT) if tankmanCost is not None else float(value)

    def handlerGoldTankmanCost(self, value):
        tankmanCost = self.itemsCache.items.shop.defaults.tankmanCost
        return self._calculateDiscount('goldTankmanCost', value, tankmanCost[2][Currency.GOLD], _DT.PERCENT) if tankmanCost is not None else float(value)

    def handlerChangeRoleCost(self, value):
        default = self.itemsCache.items.shop.defaults.changeRoleCost
        return self._calculateDiscount('changeRoleCost', value, default, _DT.PERCENT)

    def handlerCreditsDropSkillsCost(self, value):
        dropSkillsCost = self.itemsCache.items.shop.defaults.dropSkillsCost
        return self._calculateDiscount('creditsDropSkillsCost', value, dropSkillsCost[1][Currency.CREDITS], _DT.PERCENT) if dropSkillsCost is not None else float(value)

    def handlerGoldDropSkillsCost(self, value):
        dropSkillsCost = self.itemsCache.items.shop.defaults.dropSkillsCost
        return self._calculateDiscount('goldDropSkillsCost', value, dropSkillsCost[2][Currency.GOLD], _DT.PERCENT) if dropSkillsCost is not None else float(value)

    def handlerExchangeRate(self, value):
        default = self.itemsCache.items.shop.defaults.exchangeRate
        shopValue = self.itemsCache.items.shop.exchangeRate
        return self._calculateDiscount('exchangeRate', shopValue, default, _DT.MULTIPLIER, discountValueCalculator=self._calculateModifier)

    def handlerExchangeRateForShellsAndEqs(self, value):
        default = self.itemsCache.items.shop.defaults.exchangeRateForShellsAndEqs
        return self._calculateDiscount('exchangeRateForShellsAndEqs', value, default, _DT.PERCENT)

    def handlerPaidRemovalCost(self, value):
        default = self.itemsCache.items.shop.defaults.paidRemovalCost
        return self._calculateDiscount('paidRemovalCost', value, default, _DT.PERCENT)

    def handlerPaidDeluxeRemovalCost(self, value):
        default = self.itemsCache.items.shop.defaults.paidDeluxeRemovalCost
        return self._calculateDiscount('paidDeluxeRemovalCost', value, default, _DT.PERCENT)

    def handlerPassportChangeCost(self, value):
        default = self.itemsCache.items.shop.defaults.passportChangeCost
        return self._calculateDiscount('passportChangeCost', value, default, _DT.PERCENT)

    def handlerFemalePassportChangeCost(self, value):
        default = self.itemsCache.items.shop.defaults.passportFemaleChangeCost
        return self._calculateDiscount('femalePassportChangeCost', value, default, _DT.PERCENT)

    def handlerClanCreationCost(self, value):
        default = 2500
        return self._calculateDiscount('clanCreationCost', value, default, _DT.PERCENT)

    def handlerFreeXPConversionDiscrecity(self, value):
        default = self.itemsCache.items.shop.defaults.freeXPConversion[0]
        shopValue = self.itemsCache.items.shop.freeXPConversion[0]
        return self._calculateDiscount('freeXPConversionDiscrecity', shopValue, default, _DT.MULTIPLIER, discountValueCalculator=self._calculateModifier)

    def handlerFreeXPToTManXPRate(self, value):
        default = self.itemsCache.items.shop.defaults.freeXPToTManXPRate
        shopValue = self.itemsCache.items.shop.freeXPToTManXPRate
        return self._calculateDiscount('freeXPToTManXPRate', shopValue, default, _DT.MULTIPLIER, discountValueCalculator=self._calculateModifier)

    def handlerPremiumPacket1(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(1)
        return self._calculateDiscount('premiumPacket1', value, default, _DT.PERCENT)

    def handlerPremiumPacket3(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(3)
        return self._calculateDiscount('premiumPacket3', value, default, _DT.PERCENT)

    def handlerPremiumPacket7(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(7)
        return self._calculateDiscount('premiumPacket7', value, default, _DT.PERCENT)

    def handlerPremiumPacket30(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(30)
        return self._calculateDiscount('premiumPacket30', value, default, _DT.PERCENT)

    def handlerPremiumPacket180(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(180)
        return self._calculateDiscount('premiumPacket180', value, default, _DT.PERCENT)

    def handlerPremiumPacket360(self, value):
        default = self.itemsCache.items.shop.defaults.getPremiumPacketCost(360)
        return self._calculateDiscount('premiumPacket360', value, default, _DT.PERCENT)

    def handlerCamouflagePacketInfCost(self, value):
        default = self.itemsCache.items.shop.defaults.getCamouflageCost()
        return self._calculateDiscount('camouflagePacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerCamouflagePacket7Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getCamouflageCost(7)
        return self._calculateDiscount('camouflagePacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerCamouflagePacket30Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getCamouflageCost(30)
        return self._calculateDiscount('camouflagePacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerInscriptionPacketInfCost(self, value):
        default = self.itemsCache.items.shop.defaults.getInscriptionCost()
        return self._calculateDiscount('inscriptionPacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerInscriptionPacket7Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getInscriptionCost(7)
        return self._calculateDiscount('inscriptionPacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerInscriptionPacket30Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getInscriptionCost(30)
        return self._calculateDiscount('inscriptionPacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerEmblemPacketInfCost(self, value):
        default = self.itemsCache.items.shop.defaults.getEmblemCost()
        return self._calculateDiscount('emblemPacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerEmblemPacket7Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getEmblemCost(7)
        return self._calculateDiscount('emblemPacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerEmblemPacket30Cost(self, value):
        default = self.itemsCache.items.shop.defaults.getEmblemCost(30)
        return self._calculateDiscount('emblemPacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def handlerTradeInSellPriceFactor(self, value):
        return self._calculateDiscount('tradeInSellPriceFactor', value, 1, _DT.TRADE_IN_PERCENT, discountValueCalculator=lambda v, _: int(v * 100))

    def handlerWinXPFactorMode(self):
        winXpFactor = self.itemsCache.items.shop.winXPFactorMode
        if winXpFactor == constants.WIN_XP_FACTOR_MODE.DAILY:
            return None
        else:
            dailyFactor = self.itemsCache.items.shop.dailyXPFactor
            return _ActionDiscountValue(discountName='winXPFactorMode', discountValue=dailyFactor, discountType=_DT.MULTIPLIER)

    def _calculateDiscount(self, paramName, discountVal, defaultVal, discountType, discountValueCalculator=None):
        calculator = discountValueCalculator or self._calcDiscountValue
        value = calculator(discountVal, defaultVal)
        return _ActionDiscountValue(discountName=paramName, discountValue=value, discountType=discountType)

    def _calculateModifier(self, value, defaultValue):
        return round(float(value) / defaultValue, 2) if value % defaultValue > 0 else int(value / defaultValue)

    def getValues(self, action):
        result = defaultdict(dict)
        for key, value in self.parse().iteritems():
            result[key] = [(value, action.getID())]

        return result


class EconomicsMul(EconomicsSet):

    def _wrapParamName(self, name):
        if name not in ('exchangeRateForShellsAndEqs',) and name.endswith(_MULTIPLIER):
            name = name[:-len(_MULTIPLIER)]
        elif name == 'paidRemovalCostMultiplierGold':
            name = 'paidRemovalCost'
        return name

    def _calcDiscountValue(self, value, default):
        return _getPercentDiscountByMultiplier(value, default)

    def _calcCustomizationDiscountValue(self, value, default):
        return _getDiscountByMultiplier(float(value), 100)


class CamouflagePriceMul(_VehiclePrice):

    def __init__(self, name, params):
        super(_VehiclePrice, self).__init__(name, params, section=ACTION_SECTION_TYPE.CUSTOMIZATION)

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for vehicle, priceMult in items:
            result[vehicle.intCD] = _ActionDiscountValue(discountName=vehicle, discountValue=int(round((1 - priceMult) * 100)), discountType=_DT.PERCENT)

        return result

    def _getMultName(self, idx):
        return 'priceFactorMultiplier%d' % idx


class EmblemPriceByGroupsMul(_DiscountsListAction):

    def __init__(self, name, params):
        super(EmblemPriceByGroupsMul, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT, ACTION_SECTION_TYPE.CUSTOMIZATION)

    def packDiscounts(self, sorting=True):
        result = {}
        groups, _, _ = vehicles.g_cache.playerEmblems()
        for groupName, priceMult in self.parse().iteritems():
            if groupName in groups:
                result[groupName] = _ActionDiscountValue(discountName=groupName, discountValue=int(round((1 - priceMult) * 100)), discountType=_DT.PERCENT)
            LOG_ERROR('Given group name is not available: ', groupName)

        return result

    def _makeResultItem(self, paramValue):
        return str(paramValue)

    def _getParamName(self, idx):
        return 'name%d' % idx

    def _getMultName(self, idx):
        return 'priceFactorMultiplier%d' % idx

    def getValues(self, action):
        result = {}
        for group, value in self.parse().iteritems():
            result[group] = [(value, action.getID())]

        return result


class EquipmentPriceSet(_EquipmentPrice, _BuyPriceSet):
    pass


class EquipmentPriceMul(_EquipmentPrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class EquipmentPriceAll(_SplitByCurrency, _ItemsPriceAll):

    def __init__(self, name, params):
        super(EquipmentPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.EQUIPMENT)

    def _getRequestCriteria(self):
        return _COMMON_CRITERIA


class OptDevicePriceAll(_ItemsPriceAll, _BuyPriceMul):

    def __init__(self, name, params):
        super(OptDevicePriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.OPTIONALDEVICE)

    def _getRequestCriteria(self):
        return _COMMON_CRITERIA


class OptDevicePriceSet(_OptDevicePrice, _BuyPriceSet):
    pass


class OptDevicePriceMul(_OptDevicePrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class ShellPriceAll(_SplitByCurrency, _ItemsPriceAll):

    def __init__(self, name, params):
        super(ShellPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.SHELL)

    def _getRequestCriteria(self):
        return _COMMON_CRITERIA


class ShellPriceNation(ShellPriceAll):
    pass


class ShellPriceSet(_ShellPrice, _BuyPriceSet):
    pass


class ShellPriceMul(_ShellPrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class VehPriceAll(_ItemsPriceAll):

    def __init__(self, name, params):
        super(VehPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.VEHICLE)


class VehRentPriceAll(_ItemsPriceAll):

    def __init__(self, name, params, modType=ACTION_MODIFIER_TYPE.RENT, section=ACTION_SECTION_TYPE.ALL, itemType=GUI_ITEM_TYPE.VEHICLE):
        super(VehRentPriceAll, self).__init__(name, params, modType=modType, section=section, itemType=itemType)


class VehPriceNation(_ItemsPriceAll):

    def __init__(self, name, params):
        super(VehPriceNation, self).__init__(name, params, itemType=GUI_ITEM_TYPE.VEHICLE)


class VehRentPriceNation(_ItemsPriceAll):

    def __init__(self, name, params):
        super(VehRentPriceNation, self).__init__(name, params, itemType=GUI_ITEM_TYPE.VEHICLE, section=ACTION_SECTION_TYPE.ALL, modType=ACTION_MODIFIER_TYPE.RENT)


class VehPriceSet(_VehiclePrice, _BuyPriceSet):
    pass


class VehRentPriceSet(_VehicleRentPrice, _RentPriceSet):
    MAX_RENT_PACKAGES_COUNT = 6

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for (vehicle, package), rentCost in items:
            dv, dt = self._getRentDiscountParams(vehicle, package, rentCost)
            result[vehicle.intCD] = _ActionDiscountValue(discountName=vehicle, discountValue=dv, discountType=_DT.PERCENT)

        return result

    def _getParamName(self, idx):
        return 'rentPacket%dDays' % idx

    def _getMultName(self, idx):
        return 'rentPacket%dCost' % idx

    def _parse(self):
        result = {}
        if 'vehName' in self._params:
            item = self._makeResultItem(self._params['vehName'])
            if item is not None:
                for idx in xrange(self.MAX_RENT_PACKAGES_COUNT):
                    paramName = self._getParamName(idx)
                    multName = self._getMultName(idx)
                    if paramName in self._params and multName in self._params:
                        result[item, int(self._params.get(paramName, 0))] = int(self._params.get(multName, 0))

            return result
        else:
            return


class VehPriceMul(_VehiclePrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class VehRentPriceMul(VehPriceMul, _VehicleRentPrice, _RentPriceMul):
    pass


class VehPriceCond(_VehiclePrice, _BuyPriceMul):
    DEFAULT_PRICE_MULT = 1.0

    def _getRequestCriteria(self):
        criteria = ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.HIDDEN
        if 'nation' in self._params:
            criteria |= REQ_CRITERIA.NATIONS([nations.INDICES[self._params['nation']]])
        if 'levelEqual' in self._params:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS([int(self._params['levelEqual'])])
        else:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(range(int(self._params.get('levelMoreThan', 0)) + 1, int(self._params.get('levelLessThan', constants.MAX_VEHICLE_LEVEL + 1))))
        if 'vehClass' in self._params:
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES([self._params['vehClass']])
        return criteria

    def _parse(self):
        result = {}
        try:
            goldPriceMult = self._params.get('goldPriceMultiplier')
            creditsPriceMult = self._params.get('creditsPriceMultiplier')
            result = self._getConditionResult(goldPriceMult, creditsPriceMult, self._getRequestCriteria())
        except Exception:
            LOG_ERROR('There is error while vehicles getting')
            LOG_CURRENT_EXCEPTION()

        return result

    def _getConditionResult(self, goldPriceMult, creditsPriceMult, criteria):
        result = {}
        for v in self.itemsCache.items.getVehicles(criteria).itervalues():
            if v.buyPrices.itemPrice.price.isSet(Currency.GOLD) and goldPriceMult is not None:
                result[v] = float(goldPriceMult)
            if v.buyPrices.itemPrice.price.isSet(Currency.CREDITS) and creditsPriceMult is not None:
                result[v] = float(creditsPriceMult)

        return result


class VehRentPriceCond(VehPriceCond, _VehicleRentPrice, _RentPriceMul):

    def _getConditionResult(self, goldPriceMult, creditsPriceMult, criteria):
        result = {}
        for v in self.itemsCache.items.getVehicles(criteria).itervalues():
            for rentPackage in v.rentPackages:
                rentCost = rentPackage['rentPrice']
                rentDays = rentPackage['days']
                if rentCost.isSet(Currency.GOLD) and goldPriceMult is not None:
                    result[v, rentDays] = float(goldPriceMult)
                if rentCost.isSet(Currency.CREDITS) and creditsPriceMult is not None:
                    result[v, rentDays] = float(creditsPriceMult)

        return result


class VehSellPriceSet(_VehiclePrice, _SellPriceMul):
    DEFAULT_PRICE_MULT = 0.5

    def __init__(self, name, params):
        super(VehSellPriceSet, self).__init__(name, params, ACTION_MODIFIER_TYPE.SELLING)

    def packDiscounts(self, sorting=True):
        results = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for vehicle, value in items:
            dv, dt = self._getDiscountParams(vehicle, value)
            results[vehicle.intCD] = _ActionDiscountValue(discountName=vehicle, discountValue=dv, discountType=dt)

        return results

    def _parse(self):
        isForGold = self._params.get('sellForGold', 'false') != 'false'
        result = {}
        for v, value in super(VehSellPriceSet, self)._parse().iteritems():
            result[v] = (isForGold, value)

        return result

    def _getMultName(self, idx):
        pass


class _BoosterPrice(_DiscountsListAction, _PriceOpAbstract):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, name, params):
        super(_BoosterPrice, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT, ACTION_SECTION_TYPE.BOOSTER)

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for item, value in items:
            dv, _ = self._getDiscountParams(item, value)
            result[item.boosterID] = _ActionDiscountValue(discountName=item, discountValue=dv, discountType=_DT.PERCENT)

        return result

    def getValues(self, action):
        result = {}
        for booster, value in self.parse().iteritems():
            result[booster.boosterID] = [(value, action.getID())]

        return result

    def _getParamName(self, idx):
        return 'goodieID%d' % idx

    def _getMultName(self, idx):
        return 'price%d' % idx

    def _getRequestCriteria(self):
        criteria = _COMMON_CRITERIA | REQ_CRITERIA.BOOSTER.ENABLED
        return criteria

    def _makeResultItem(self, strBoosterID):
        try:
            if strBoosterID.isdigit():
                boosterID = int(strBoosterID)
            else:
                _, boosterIdPart = strBoosterID.split('_')
                boosterID = int(boosterIdPart)
            goodies = self.goodiesCache.getBoosters(criteria=self._getRequestCriteria())
            if boosterID in goodies:
                return goodies[boosterID]
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return None


class BoosterPriceSet(_BoosterPrice, _BuyPriceSet):
    pass


class BoosterPriceMul(_BoosterPrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class BoostersPriceAll(_ItemsPriceAll):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, name, params):
        super(BoostersPriceAll, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT, ACTION_SECTION_TYPE.ALL_BOOSTERS)

    def _getRequestCriteria(self):
        criteria = _COMMON_CRITERIA | REQ_CRITERIA.BOOSTER.ENABLED
        return criteria

    def packDiscounts(self, sorting=True):
        result = {}
        items = self.parse().iteritems()
        if sorting:
            items = sorted(items, key=operator.itemgetter(0))
        for (_, booster), value in items:
            result[booster.boosterID] = _ActionDiscountValue(discountName=booster, discountValue=int(round((1 - float(value)) * 100)), discountType=_DT.PERCENT)

        return result

    def _getConditionResult(self, nation, goldPriceMult, creditsPriceMult, criteria):
        result = {}
        for booster in self.goodiesCache.getBoosters(criteria=criteria).itervalues():
            buyPrices = booster.buyPrices
            if buyPrices.hasPriceIn(Currency.GOLD) and goldPriceMult is not None:
                result[nation, booster] = float(goldPriceMult)
            if buyPrices.hasPriceIn(Currency.CREDITS) and creditsPriceMult is not None:
                result[nation, booster] = float(creditsPriceMult)

        return result


_MODIFIERS = (('mul_EconomicsParams', EconomicsMul),
 ('set_EconomicsParams', EconomicsSet),
 ('mul_EconomicsPrices', EconomicsMul),
 ('set_EconomicsPrices', EconomicsSet),
 ('set_TradeInParams', EconomicsSet),
 ('cond_VehPrice', VehPriceCond),
 ('mul_VehPrice', VehPriceMul),
 ('set_VehPrice', VehPriceSet),
 ('mul_VehPriceAll', VehPriceAll),
 ('mul_VehPriceNation', VehPriceNation),
 ('set_VehSellPrice', VehSellPriceSet),
 ('cond_VehRentPrice', VehRentPriceCond),
 ('mul_VehRentPrice', VehRentPriceMul),
 ('set_VehRentPrice', VehRentPriceSet),
 ('mul_VehRentPriceAll', VehRentPriceAll),
 ('mul_VehRentPriceNation', VehRentPriceNation),
 ('mul_EquipmentPriceAll', EquipmentPriceAll),
 ('mul_EquipmentPrice', EquipmentPriceMul),
 ('set_EquipmentPrice', EquipmentPriceSet),
 ('mul_OptionalDevicePriceAll', OptDevicePriceAll),
 ('mul_OptionalDevicePrice', OptDevicePriceMul),
 ('set_OptionalDevicePrice', OptDevicePriceSet),
 ('mul_ShellPriceAll', ShellPriceAll),
 ('mul_ShellPriceNation', ShellPriceNation),
 ('mul_ShellPrice', ShellPriceMul),
 ('set_ShellPrice', ShellPriceSet),
 ('mul_CamouflagePriceFactor', CamouflagePriceMul),
 ('mul_EmblemPriceFactorByGroups', EmblemPriceByGroupsMul),
 ('set_GoodiePrice', BoosterPriceSet),
 ('mul_GoodiePrice', BoosterPriceMul),
 ('mul_GoodiePriceAll', BoostersPriceAll))
_MODIFIERS_DICT = dict(_MODIFIERS)
_MODIFIERS_ORDER = dict(((n, idx) for idx, (n, _) in enumerate(_MODIFIERS)))

def compareModifiers(modName1, modName2):
    if modName1 not in _MODIFIERS_ORDER:
        return -1
    return 1 if modName2 not in _MODIFIERS_ORDER else _MODIFIERS_ORDER[modName1] - _MODIFIERS_ORDER[modName2]


def getModifierObj(name, params):
    return _MODIFIERS_DICT[name](name, params) if name in _MODIFIERS_DICT else None
