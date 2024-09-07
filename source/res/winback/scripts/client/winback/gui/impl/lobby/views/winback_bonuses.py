# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_bonuses.py
from collections import OrderedDict
from goodies.goodie_helpers import getPriceWithDiscount
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import BlueprintBonusTypes
from gui.server_events.bonuses import SimpleBonus, GoodiesBonus
from gui.shared.money import Money
from gui.shared.tooltips import getUnlockPrice
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_DAY
from shared_utils import first
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.offers import IOffersDataProvider
from gui.shared.gui_items.Vehicle import Vehicle
from gui.server_events.bonuses import SelectableBonus
from winback.gui.impl.gen.view_models.views.lobby.views.rent_vehicle_bonus_model import RentType
from winback.gui.impl.gen.view_models.views.lobby.views.winback_reward_view_model import RewardName
from winback.gui.impl.lobby.winback_helpers import getDiscountFromGoody, getDiscountFromBlueprint

class WinbackSelectableBonus(SelectableBonus):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(WinbackSelectableBonus, self).__init__(value, isCompensation, ctx, name)
        self._isDiscount = self._name == RewardName.SELECTABLE_VEHICLE_DISCOUNT.value
        self._firstGift = self._getFirstGift() if self._isDiscount else None
        return

    @property
    def isDiscount(self):
        return self._isDiscount

    @property
    def data(self):
        return first(self._value.itervalues())

    def getLevel(self):
        return self.data.get('level', -1)

    def getTokenId(self):
        return first(self.getTokens().keys())

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

    def _getFirstGift(self):
        tokenName = self.getTokenId().replace('_gift', '')
        offer = self.__offersProvider.getOfferByToken(tokenName)
        return None if not offer else offer.getFirstGift()

    def getTooltip(self):
        specialArgs = {'level': self.getLevel(),
         'isDiscount': self._isDiscount,
         'purchaseDiscount': self.getPurchaseDiscount(),
         'researchDiscount': self.getResearchDiscount()}
        return [backport.createTooltipData(isSpecial=True, specialArgs=specialArgs)]


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
        return self._getVehData(vehCD).get('crewLvl')

    def getTankmenRoleLevelsAndSkills(self, vehCD):
        tankmen = self._getVehData(vehCD).get('tankmen', [])
        tankmenSkills = [ tankman.get('skills', []) for tankman in tankmen ]
        tankmenRoleLevels = [ tankman.get('roleLevel', -1) for tankman in tankmen ]
        tankmenRoleLevels = tankmenRoleLevels if tankmenRoleLevels else [self.getCrewLevel(vehCD)]
        return (tankmenRoleLevels, tankmenSkills)

    def getVehicle(self, vehCD):
        return self.itemsCache.items.getItemByCD(vehCD)

    def getTooltip(self):
        return [ self._createVehicleTooltip(vehCD) for vehCD in self.getVehicleCDs() ]

    def _getVehData(self, vehCD):
        return self._value.get(vehCD, {})

    def _getRentTooltip(self, vehicleCD):
        tankmenRoleLevelsAndSkills = self.getTankmenRoleLevelsAndSkills(vehicleCD)
        crewLevel = tankmenRoleLevelsAndSkills[0][0]
        rentValue = self.getRentValue(vehicleCD)
        rentName = self.getRentName(vehicleCD)
        if rentName == RentType.TIME.value:
            rentValue = getServerUTCTime() + rentValue * ONE_DAY
        rentSeason = None
        specialArgs = (vehicleCD,
         tankmenRoleLevelsAndSkills,
         rentValue if rentName == RentType.TIME.value else 0,
         rentValue if rentName == RentType.BATTLES.value else 0,
         rentValue if rentName == RentType.WINS.value else 0,
         rentSeason,
         crewLevel is not None,
         self._getVehData(vehicleCD).get('slot', 0) > 0,
         bool(self._getVehData(vehicleCD).get('unlockModules', [])))
        return backport.createTooltipData(isSpecial=True, specialArgs=specialArgs, specialAlias=TOOLTIPS_CONSTANTS.WINBACK_EXTENDED_AWARD_VEHICLE)

    def _createVehicleTooltip(self, vehicleCD):
        return self._getRentTooltip(vehicleCD)


class WinbackVehicleDiscountBonus(WinbackVehicleBonus):
    __slots__ = ('currencyDiscount', 'xpDiscount')
    __goodiesCache = dependency.descriptor(IGoodiesCache)

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
        goodie = self.__goodiesCache.getGoodieByID(goodieID)
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
         False,
         False,
         False,
         self._getBlueprintCount(vehicleCD),
         self.getPrices(vehicleCD)[1],
         True,
         True], specialAlias=TOOLTIPS_CONSTANTS.WINBACK_DISCOUNT_AWARD_VEHICLE)
