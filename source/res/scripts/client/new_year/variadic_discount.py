# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/variadic_discount.py
import logging
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel
from helpers import dependency
from items import new_year
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
VARIADIC_DISCOUNT_NAME = 'variadicDiscount'

def createDiscountBonusModel(token):
    model = DiscountBonusModel()
    variadicDiscount = VariadicDiscount(token.id, useCache=True)
    model.setValue(str(token.count))
    model.setName(VARIADIC_DISCOUNT_NAME)
    model.setVariadicID(token.id)
    model.setLevel(variadicDiscount.getTankLevel())
    model.setDiscount(variadicDiscount.getDiscountValue())
    selectedVehicle = variadicDiscount.getSelectedVehicle()
    if selectedVehicle:
        model.setSelectedVehicle(selectedVehicle.name)
    return model


def updateSelectedVehicleForBonus(bonusModel):
    variadicDiscount = VariadicDiscount(bonusModel.getVariadicID())
    selectedVehicle = variadicDiscount.getSelectedVehicle()
    if selectedVehicle:
        bonusModel.setSelectedVehicle(selectedVehicle.name)
        return True
    return False


class VariadicDiscount(object):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, discountID, useCache=False):
        self.__variadicDiscount = new_year.g_cache.variadicDiscounts[discountID]
        self.__useCache = useCache
        self.__vehiclesCache = None
        return

    def getTankLevel(self):
        return self.__variadicDiscount.level

    def getID(self):
        return self.__variadicDiscount.discountId

    def getDiscountValue(self):
        leftRange, rightRange = self.__variadicDiscount.goodiesRange
        vehicleDiscounts = self.__getVehicleDiscounts()
        for discountID in xrange(leftRange, rightRange + 1):
            if discountID in vehicleDiscounts:
                discount = vehicleDiscounts[discountID]
                return discount.resource.value

        _logger.warning('Vehicle discount has not been found for %s', self.__variadicDiscount.id)
        return None

    def getSelectedVehicle(self):
        selectedDiscounts = self._itemsCache.items.festivity.getSelectedDiscounts()
        leftRange, rightRange = self.__variadicDiscount.goodiesRange
        vehicleDiscounts = self.__getVehicleDiscounts()
        for discountID in xrange(leftRange, rightRange + 1):
            if discountID in selectedDiscounts and discountID in vehicleDiscounts:
                discount = vehicleDiscounts[discountID]
                vehicle = self._itemsCache.items.getItemByCD(discount.target.targetValue)
                if self.__variadicDiscount.level == vehicle.level:
                    return vehicle

        return None

    def getVehiclesByDiscount(self):
        result = {}
        if self.__variadicDiscount is None:
            return result
        else:
            leftRange, rightRange = self.__variadicDiscount.goodiesRange
            vehicleDiscounts = self.__getVehicleDiscounts()
            personalVehicleDiscounts = self._itemsCache.items.shop.personalVehicleDiscounts
            discountVehIntCDs = {d.target.targetValue:d.resource.value for d in personalVehicleDiscounts.values()}
            for discountID in xrange(leftRange, rightRange + 1):
                if discountID in vehicleDiscounts and discountID not in personalVehicleDiscounts:
                    discount = vehicleDiscounts[discountID]
                    vehicleIntCD = discount.getTargetValue()
                    if vehicleIntCD in discountVehIntCDs and discountVehIntCDs[vehicleIntCD] >= discount.resource.value:
                        continue
                    vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
                    if vehicle.isCollectible or vehicle.level != self.__variadicDiscount.level:
                        continue
                    result[vehicleIntCD] = discountID

            return result

    def __getVehicleDiscounts(self):
        if self.__useCache:
            if self.__vehiclesCache is None:
                self.__vehiclesCache = self._itemsCache.items.shop.getVehicleDiscountDescriptions()
            return self.__vehiclesCache
        else:
            return self._itemsCache.items.shop.getVehicleDiscountDescriptions()
