# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_bonuses.py
from collections import OrderedDict
from goodies.goodie_helpers import getPriceWithDiscount
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.impl.gen.view_models.views.lobby.winback.rent_vehicle_bonus_model import RentType
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import RewardName
from gui.impl.lobby.winback.winback_helpers import getDiscountFromGoody, getDiscountFromBlueprint, getNonCompensationToken
from gui.selectable_reward.common import WinbackSelectableRewardManager
from gui.server_events.bonuses import SimpleBonus, GoodiesBonus
from gui.shared.money import Money
from gui.shared.tooltips import getUnlockPrice
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_DAY
from shared_utils import first
from skeletons.gui.goodies import IGoodiesCache
from gui.shared.gui_items.Vehicle import Vehicle

class WinbackSelectableBonus(SimpleBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        super(WinbackSelectableBonus, self).__init__(name, value, isCompensation, ctx, compensationReason)
        self._isDiscount = self._name == RewardName.SELECTABLE_VEHICLE_DISCOUNT.value
        self._firstGift = None if not self._isDiscount else self.getFirstGift()
        return

    def getLevel(self):
        return int(self._value.get('level', '1'))

    def getToken(self):
        return self._value.get('token')

    def getPurchaseDiscount(self):
        if self._firstGift is None:
            return 0
        else:
            goodyID = first(self._firstGift.rawBonuses.get(GoodiesBonus.GOODIES, {}))
            purchaseDiscount, _ = getDiscountFromGoody(goodyID)
            return purchaseDiscount

    def getResearchDiscount(self):
        if self._firstGift is None:
            return 0
        else:
            fragmentID, fragmentCount = first(self._firstGift.rawBonuses.get(BlueprintBonusTypes.BLUEPRINTS, {}).items())
            return getDiscountFromBlueprint(fragmentID, fragmentCount)

    def getFirstGift(self):
        tokenName = getNonCompensationToken(self.getToken())
        selectableBonus = first(WinbackSelectableRewardManager.getSelectableBonuses(lambda tID: tID == tokenName))
        return WinbackSelectableRewardManager.getFirstOfferGift(selectableBonus) if selectableBonus is not None else None

    def getTooltip(self):
        return [{'level': self.getLevel(),
          'isDiscount': self._isDiscount,
          'purchaseDiscount': self.getPurchaseDiscount(),
          'researchDiscount': self.getResearchDiscount()}]


class WinbackVehicleBonus(SimpleBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        super(WinbackVehicleBonus, self).__init__(name, value, isCompensation, ctx, compensationReason)
        self._value = OrderedDict(sorted(self._value.items(), key=lambda item: -self.getVehicle(item[0]).level))

    def getVehicleCDs(self):
        return self._value.keys()

    def getRentData(self, vehCD):
        return self._getVehData(vehCD).get('rent', {})

    def isRent(self, vehCD):
        return self.getRentValue(vehCD) > 0

    def getRentValue(self, vehCD):
        rentData = self.getRentData(vehCD)
        return rentData.get('wins', 0) or rentData.get('battles', 0) or rentData.get('time', 0)

    def getRentName(self, vehCD):
        rentData = self.getRentData(vehCD)
        for rentName, rentValue in rentData.items():
            if rentValue > 0:
                return rentName

    def getRentType(self, vehCD):
        rentName = self.getRentName(vehCD)
        for rentType in RentType.__members__.values():
            if rentType.value == rentName:
                return rentType

        return None

    def getCrewLevel(self, vehCD):
        return self._getVehData(vehCD).get('crewLvl', -1)

    def getVehicle(self, vehCD):
        return self.itemsCache.items.getItemByCD(vehCD)

    def getTooltip(self):
        return [ self._createVehicleTooltip(vehCD) for vehCD in self.getVehicleCDs() ]

    def _getVehData(self, vehCD):
        return self._value.get(vehCD, {})

    def _getRentTooltip(self, vehicleCD):
        crewLevel = self.getCrewLevel(vehicleCD)
        rentValue = self.getRentValue(vehicleCD)
        rentName = self.getRentName(vehicleCD)
        if rentName == RentType.TIME.value:
            rentValue = getServerUTCTime() + rentValue * ONE_DAY
        rentSeason = None
        rentCycle = None
        isSeniority = False
        specialArgs = (vehicleCD,
         crewLevel,
         rentValue if rentName == RentType.TIME.value else 0,
         rentValue if rentName == RentType.BATTLES.value else 0,
         rentValue if rentName == RentType.WINS.value else 0,
         rentSeason,
         rentCycle,
         isSeniority,
         crewLevel > 0,
         self._getVehData(vehicleCD).get('slot', 0) > 0,
         bool(self.getUnlockModules(vehicleCD)))
        return backport.createTooltipData(isSpecial=True, specialArgs=specialArgs, specialAlias=TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE)

    def getUnlockModules(self, vehicleCD):
        return self._getVehData(vehicleCD).get('unlockModules', [])

    def _createVehicleTooltip(self, vehicleCD):
        return self._getRentTooltip(vehicleCD)


class WinbackVehicleDiscountBonus(WinbackVehicleBonus):
    __slots__ = ('currencyDiscount', 'xpDiscount')
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        super(WinbackVehicleDiscountBonus, self).__init__(name, value, isCompensation, ctx, compensationReason)
        for vehCD in self._value:
            vehicle = self.getVehicle(vehCD)
            self._value[vehCD]['prices'] = self._getPrices(vehicle)
            _, cost, _, defCost, _ = getUnlockPrice(vehicle.intCD, None, vehicle.level, self._getBlueprintCount(vehCD))
            self._value[vehCD]['xps'] = (defCost, cost)

        return

    def _getBlueprintCount(self, vehCD):
        return self._getVehData(vehCD).get(BlueprintBonusTypes.BLUEPRINTS, {}).get(vehCD, 0)

    def _getPrices(self, vehicle):
        price = vehicle.buyPrices.itemPrice.defPrice
        goodieID = first(self._getVehData(vehicle.intCD).get(GoodiesBonus.GOODIES, {}))
        goodie = self.goodiesCache.getGoodieByID(goodieID)
        discountPrice = getPriceWithDiscount(price.credits, goodie.resource)
        return (price, Money(credits=discountPrice))

    def getPrices(self, vehCD):
        return self._getVehData(vehCD).get('prices', (None, None))

    def getXPs(self, vehCD):
        return self._getVehData(vehCD).get('xps', (None, None))

    def getResources(self, vehCD):
        goodieID = first(self._getVehData(vehCD).get(GoodiesBonus.GOODIES, {}))
        return (goodieID, self._getBlueprintCount(vehCD))

    def _createVehicleTooltip(self, vehicleCD):
        return backport.createTooltipData(isSpecial=True, specialArgs=[vehicleCD,
         None,
         None,
         None,
         None,
         None,
         None,
         False,
         False,
         False,
         False,
         self._getBlueprintCount(vehicleCD),
         self.getPrices(vehicleCD)[1],
         True,
         True], specialAlias=TOOLTIPS_CONSTANTS.WINBACK_DISCOUNT_AWARD_VEHICLE)
