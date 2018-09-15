# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/requester/ny_contexts.py
from gui.shared.utils.requesters.abstract import RequestCtx
from new_year.requester.new_year_requester import RequestType
DEFAULT_COOLDOWN = 1

class _CommonNYContext(RequestCtx):

    def getRequestType(self):
        raise NotImplementedError

    def multipleRequestAllowed(self):
        return True

    def getCooldown(self):
        pass


class _NYOpenContainerContext(_CommonNYContext):

    def __init__(self, itemId, waitingID=''):
        super(_NYOpenContainerContext, self).__init__(waitingID)
        self.__id = itemId

    def getID(self):
        return self.__id


class NYBoxOpenContext(_NYOpenContainerContext):

    def getRequestType(self):
        return RequestType.OPEN_BOX


class NYChestOpenContext(_NYOpenContainerContext):

    def getRequestType(self):
        return RequestType.OPEN_CHEST


class NYSelectDiscount(_CommonNYContext):

    def __init__(self, discountID, variadicDiscountID, vehName, vehIntCD, discountVal, waitingID=''):
        super(NYSelectDiscount, self).__init__(waitingID)
        self.__discountID = discountID
        self.__variadicDiscountID = variadicDiscountID
        self.__vehName = vehName
        self.__discountVal = discountVal
        self.__vehIntCD = vehIntCD

    def getRequestType(self):
        return RequestType.APPLY_VEH_DISCOUNT

    def getDiscountID(self):
        return self.__discountID

    def getVariadicDiscountID(self):
        return self.__variadicDiscountID

    def getVehName(self):
        return self.__vehName

    def getVehIntCD(self):
        return self.__vehIntCD

    def getDiscountVal(self):
        return self.__discountVal


class NYSelectTankman(_CommonNYContext):

    def __init__(self, nationID, vehicleInnationID, roleID, variadicTankmanID, waitingID=''):
        super(NYSelectTankman, self).__init__(waitingID)
        self.__nationID = nationID
        self.__vehicleInnationID = vehicleInnationID
        self.__roleID = roleID
        self.__variadicTankmanID = variadicTankmanID

    def getRequestType(self):
        return RequestType.RECRUIT_TANK_WOMAN

    def getNationID(self):
        return self.__nationID

    def getVehicleInnationID(self):
        return self.__vehicleInnationID

    def getRoleID(self):
        return self.__roleID

    def getVariadicTankmanID(self):
        return self.__variadicTankmanID


class CraftToyContext(_CommonNYContext):

    def __init__(self, toyType, toyNation, toyLevel, waitingID=''):
        super(CraftToyContext, self).__init__(waitingID)
        self.__toyType = toyType
        self.__toyNation = toyNation
        self.__toyLevel = toyLevel

    def getRequestType(self):
        return RequestType.CRAFT_TOY

    def getToyType(self):
        return self.__toyType

    def getToyNation(self):
        return self.__toyNation

    def getToyLevel(self):
        return self.__toyLevel


class BreakToyContext(_CommonNYContext):

    def __init__(self, toys, waitingID=''):
        super(BreakToyContext, self).__init__(waitingID)
        self.__toys = toys

    def getRequestType(self):
        return RequestType.BREAK_TOYS

    def multipleRequestAllowed(self):
        return False

    def getToys(self):
        return self.__toys


class PlaceToyContext(_CommonNYContext):

    def __init__(self, toyId, slotId, waitingID=''):
        super(PlaceToyContext, self).__init__(waitingID)
        self.__toyId = toyId
        self.__slotId = slotId

    def getRequestType(self):
        return RequestType.PLACE_TOY

    def getToyID(self):
        return self.__toyId

    def getSlotID(self):
        return self.__slotId

    def getWaiterID(self):
        return (self.getRequestType(), self.__slotId, self.__toyId)

    def getCooldown(self):
        pass
