# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/Vehicle.py
import logging
import math
import random
from collections import namedtuple
from copy import deepcopy
from itertools import izip
from operator import itemgetter
import typing
import BigWorld
from backports.functools_lru_cache import lru_cache
import constants
from AccountCommands import LOCK_REASON, VEHICLE_SETTINGS_FLAG, VEHICLE_EXTRA_SETTING_FLAG
from PerksParametersController import PerksParametersController
from collector_vehicle import CollectorVehicleConsts
from constants import WIN_XP_FACTOR_MODE, RentType
from gui import GUI_SETTINGS
from RTSShared import RTSSupply
from gui import makeHtmlString
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prb_getters, prbDispatcherProperty
from gui.prb_control.settings import PREBATTLE_SETTING_NAME
from gui.shared.economics import calcRentPackages, getActionPrc, calcVehicleRestorePrice
from gui.shared.formatters import text_styles
from gui.shared.gui_items import CLAN_LOCK, GUI_ITEM_TYPE, getItemIconName, GUI_ITEM_ECONOMY_CODE, checkForTags
from gui.shared.gui_items.Tankman import Tankman, BROTHERHOOD_SKILL_NAME
from gui.shared.gui_items.customization.slots import ProjectionDecalSlot, BaseCustomizationSlot, EmblemSlot
from gui.shared.gui_items.fitting_item import FittingItem, RentalInfoProvider
from gui.shared.gui_items.gui_item import HasStrCD
from gui.shared.gui_items.gui_item_economics import ItemPrice, ItemPrices, ITEM_PRICE_EMPTY
from gui.shared.gui_items.vehicle_equipment import VehicleEquipment, SUPPORT_EXT_DATA_FEATURES
from gui.shared.money import MONEY_UNDEFINED, Currency, Money
from gui.shared.utils import makeSearchableString
from helpers import i18n, time_utils, dependency, func_utils
from items import vehicles, tankmen, customizations, getTypeInfoByName, getTypeOfCompactDescr, filterIntCDsByItemType
from items.components.c11n_constants import SeasonType, CustomizationType, HIDDEN_CAMOUFLAGE_ID, ApplyArea, CUSTOM_STYLE_POOL_ID, ItemTags, EMPTY_ITEM_ID
from items.customizations import createNationalEmblemComponents
from items.vehicles import getItemByCompactDescr, getVehicleType
from nation_change.nation_change_helpers import hasNationGroup, iterVehTypeCDsInNationGroup
from post_progression_common import TankSetupGroupsId
from rent_common import parseRentID
from shared_utils import findFirst, CONST_CONTAINER
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IIGRController, IRentalsController, IVehiclePostProgressionController
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from vehicle_outfit.outfit import Area, REGIONS_BY_SLOT_TYPE, ANCHOR_TYPE_TO_SLOT_TYPE_MAP
if typing.TYPE_CHECKING:
    from skeletons.gui.shared import IItemsRequester
    from items.components.c11n_components import StyleItem
    from items.customizations import CustomizationOutfit
    from vehicle_outfit.outfit import Outfit
    from gui.veh_post_progression.models.progression import PostProgressionItem, AvailabilityCheckResult
    from post_progression_common import VehicleState
    from typing import Dict, Any, List, Tuple
_logger = logging.getLogger(__name__)

class VEHICLE_CLASS_NAME(CONST_CONTAINER):
    LIGHT_TANK = 'lightTank'
    MEDIUM_TANK = 'mediumTank'
    HEAVY_TANK = 'heavyTank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'


VEHICLE_TYPES_ORDER = (VEHICLE_CLASS_NAME.LIGHT_TANK,
 VEHICLE_CLASS_NAME.MEDIUM_TANK,
 VEHICLE_CLASS_NAME.HEAVY_TANK,
 VEHICLE_CLASS_NAME.AT_SPG,
 VEHICLE_CLASS_NAME.SPG)
EmblemSlotHelper = namedtuple('EmblemSlotHelper', ['tankAreaSlot', 'tankAreaId'])
SlotHelper = namedtuple('SlotHelper', ['tankAreaSlot', 'tankAreaId'])
VEHICLE_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(VEHICLE_TYPES_ORDER)))
UNKNOWN_VEHICLE_CLASS_ORDER = 100

def compareByVehTypeName(vehTypeA, vehTypeB):
    return VEHICLE_TYPES_ORDER_INDICES[vehTypeA] - VEHICLE_TYPES_ORDER_INDICES[vehTypeB]


def compareByVehTableTypeName(vehTypeA, vehTypeB):
    return VEHICLE_TABLE_TYPES_ORDER_INDICES[vehTypeA] - VEHICLE_TABLE_TYPES_ORDER_INDICES[vehTypeB]


VEHICLE_TABLE_TYPES_ORDER = (VEHICLE_CLASS_NAME.HEAVY_TANK,
 VEHICLE_CLASS_NAME.MEDIUM_TANK,
 VEHICLE_CLASS_NAME.LIGHT_TANK,
 VEHICLE_CLASS_NAME.AT_SPG,
 VEHICLE_CLASS_NAME.SPG)
VEHICLE_TABLE_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(VEHICLE_TABLE_TYPES_ORDER)))
VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED = dict(((n, i) for i, n in enumerate(reversed(VEHICLE_TABLE_TYPES_ORDER))))
VEHICLE_BATTLE_TYPES_ORDER = (VEHICLE_CLASS_NAME.HEAVY_TANK,
 VEHICLE_CLASS_NAME.MEDIUM_TANK,
 VEHICLE_CLASS_NAME.AT_SPG,
 VEHICLE_CLASS_NAME.LIGHT_TANK,
 VEHICLE_CLASS_NAME.SPG)
VEHICLE_BATTLE_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(VEHICLE_BATTLE_TYPES_ORDER)))
_ALL_ROLES_ORDER = [constants.ROLE_TYPE.LT_UNIVERSAL,
 constants.ROLE_TYPE.LT_WHEELED,
 constants.ROLE_TYPE.HT_UNIVERSAL,
 constants.ROLE_TYPE.MT_UNIVERSAL,
 constants.ROLE_TYPE.ATSPG_UNIVERSAL,
 constants.ROLE_TYPE.HT_ASSAULT,
 constants.ROLE_TYPE.MT_ASSAULT,
 constants.ROLE_TYPE.ATSPG_ASSAULT,
 constants.ROLE_TYPE.MT_SNIPER,
 constants.ROLE_TYPE.ATSPG_SNIPER,
 constants.ROLE_TYPE.MT_SUPPORT,
 constants.ROLE_TYPE.HT_BREAK,
 constants.ROLE_TYPE.HT_SUPPORT,
 constants.ROLE_TYPE.ATSPG_SUPPORT,
 constants.ROLE_TYPE.SPG]
_LIGHT_GROUPS = [constants.ROLE_TYPE.LT_UNIVERSAL, constants.ROLE_TYPE.LT_WHEELED]
_MEDIUM_GROUPS = [constants.ROLE_TYPE.MT_ASSAULT,
 constants.ROLE_TYPE.MT_UNIVERSAL,
 constants.ROLE_TYPE.MT_SNIPER,
 constants.ROLE_TYPE.MT_SUPPORT]
_HEAVY_GROUPS = [constants.ROLE_TYPE.HT_ASSAULT,
 constants.ROLE_TYPE.HT_UNIVERSAL,
 constants.ROLE_TYPE.HT_BREAK,
 constants.ROLE_TYPE.HT_SUPPORT]
_AT_SPG_GROUPS = [constants.ROLE_TYPE.ATSPG_ASSAULT,
 constants.ROLE_TYPE.ATSPG_UNIVERSAL,
 constants.ROLE_TYPE.ATSPG_SNIPER,
 constants.ROLE_TYPE.ATSPG_SUPPORT]
_SPG_GROUPS = {constants.ROLE_TYPE.SPG}
VEHICLE_ROLES_LABELS = [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _ALL_ROLES_ORDER ]
VEHICLE_ROLES_LABELS_BY_CLASS = {VEHICLE_CLASS_NAME.LIGHT_TANK: [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _LIGHT_GROUPS ],
 VEHICLE_CLASS_NAME.MEDIUM_TANK: [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _MEDIUM_GROUPS ],
 VEHICLE_CLASS_NAME.HEAVY_TANK: [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _HEAVY_GROUPS ],
 VEHICLE_CLASS_NAME.AT_SPG: [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _AT_SPG_GROUPS ],
 VEHICLE_CLASS_NAME.SPG: [ constants.ROLE_TYPE_TO_LABEL.get(group) for group in _SPG_GROUPS ]}

class VEHICLE_TAGS(CONST_CONTAINER):
    PREMIUM = 'premium'
    PREMIUM_IGR = 'premiumIGR'
    CANNOT_BE_SOLD = 'cannot_be_sold'
    COMMANDER = 'commander'
    SECRET = 'secret'
    SUPPLY = 'supply'
    SPECIAL = 'special'
    OBSERVER = 'observer'
    DISABLED_IN_ROAMING = 'disabledInRoaming'
    EVENT = 'event_battles'
    EXCLUDED_FROM_SANDBOX = 'excluded_from_sandbox'
    TELECOM = 'telecom'
    UNRECOVERABLE = 'unrecoverable'
    CREW_LOCKED = 'lockCrew'
    OUTFIT_LOCKED = 'lockOutfit'
    PROGRESSION_DECALS_ONLY = 'lockExceptProgression'
    OPTIONAL_DEVICES_LOCKED = 'lockOptionalDevices'
    EQUIPMENT_LOCKED = 'lockEquipment'
    EPIC_BATTLES = 'epic_battles'
    BATTLE_ROYALE = 'battle_royale'
    RENT_PROMOTION = 'rent_promotion'
    EARN_CRYSTALS = 'earn_crystals'
    MAPS_TRAINING = 'maps_training'
    T34_DISCLAIMER = 't34_disclaimer'
    CLAN_WARS_BATTLES = 'clanWarsBattles'


DISCLAIMER_TAGS = frozenset((VEHICLE_TAGS.T34_DISCLAIMER,))
EPIC_ACTION_VEHICLE_CDS = (44033, 63265)
NOT_FULL_AMMO_MULTIPLIER = 0.2
_MAX_RENT_MULTIPLIER = 2
RentPackagesInfo = namedtuple('RentPackagesInfo', ('hasAvailableRentPackages', 'mainRentType', 'seasonType'))
CrystalsEarnedInfo = namedtuple('CrystalsEarnedInfo', ('current', 'max'))
EliteStatusProgress = typing.NamedTuple('EliteStatusProgress', (('unlocked', typing.Set[int]), ('toUnlock', typing.Set[int]), ('total', typing.Set[int])))

class Vehicle(FittingItem):
    __slots__ = ('__customState', '_inventoryID', '_xp', '_dailyXPFactor', '_isElite', '_isFullyElite', '_clanLock', '_isUnique', '_rentPackages', '_rentPackagesInfo', '_isDisabledForBuy', '_isSelected', '_restorePrice', '_tradeInAvailable', '_tradeOffAvailable', '_tradeOffPriceFactor', '_tradeOffPrice', '_searchableUserName', '_personalDiscountPrice', '_rotationGroupNum', '_rotationBattlesLeft', '_isRotationGroupLocked', '_isInfiniteRotationGroup', '_settings', '_lock', '_repairCost', '_health', '_gun', '_turret', '_engine', '_chassis', '_radio', '_fuelTank', '_equipment', '_bonuses', '_crewIndices', '_slotsIds', '_crew', '_lastCrew', '_hasModulesToSelect', '_outfitComponents', '_isStyleInstalled', '_slotsAnchors', '_unlockedBy', '_maxRentDuration', '_minRentDuration', '_slotsAnchorsById', '_hasNationGroup', '_extraSettings', '_perksController', '_groupIDs', '_postProgression')

    class VEHICLE_STATE(object):
        DAMAGED = 'damaged'
        EXPLODED = 'exploded'
        DESTROYED = 'destroyed'
        UNDAMAGED = 'undamaged'
        BATTLE = 'battle'
        IN_PREBATTLE = 'inPrebattle'
        LOCKED = 'locked'
        CREW_NOT_FULL = 'crewNotFull'
        AMMO_NOT_FULL = 'ammoNotFull'
        SERVER_RESTRICTION = 'serverRestriction'
        RENTAL_IS_OVER = 'rentalIsOver'
        IGR_RENTAL_IS_OVER = 'igrRentalIsOver'
        IN_PREMIUM_IGR_ONLY = 'inPremiumIgrOnly'
        GROUP_IS_NOT_READY = 'group_is_not_ready'
        NOT_PRESENT = 'notpresent'
        UNAVAILABLE = 'unavailable'
        UNSUITABLE_TO_QUEUE = 'unsuitableToQueue'
        UNSUITABLE_TO_UNIT = 'unsuitableToUnit'
        WILL_BE_UNLOCKED_IN_BATTLE = 'willBeUnlockedInBattle'
        CUSTOM = (UNSUITABLE_TO_QUEUE, UNSUITABLE_TO_UNIT, WILL_BE_UNLOCKED_IN_BATTLE)
        UNSUITABLE = (UNSUITABLE_TO_QUEUE, UNSUITABLE_TO_UNIT)
        DEAL_IS_OVER = 'dealIsOver'
        ROTATION_GROUP_UNLOCKED = 'rotationGroupUnlocked'
        ROTATION_GROUP_LOCKED = 'rotationGroupLocked'
        RENTABLE = 'rentable'
        RENTABLE_AGAIN = 'rentableAgain'
        DISABLED = 'disabled'
        TOO_HEAVY = 'tooHeavy'

    CAN_SELL_STATES = (VEHICLE_STATE.UNDAMAGED,
     VEHICLE_STATE.CREW_NOT_FULL,
     VEHICLE_STATE.AMMO_NOT_FULL,
     VEHICLE_STATE.GROUP_IS_NOT_READY,
     VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
     VEHICLE_STATE.UNSUITABLE_TO_UNIT,
     VEHICLE_STATE.ROTATION_GROUP_UNLOCKED,
     VEHICLE_STATE.ROTATION_GROUP_LOCKED,
     VEHICLE_STATE.TOO_HEAVY,
     VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE)
    TRADE_OFF_NOT_READY_STATES = (VEHICLE_STATE.DAMAGED,
     VEHICLE_STATE.EXPLODED,
     VEHICLE_STATE.DESTROYED,
     VEHICLE_STATE.BATTLE,
     VEHICLE_STATE.IN_PREBATTLE,
     VEHICLE_STATE.LOCKED)
    GROUP_STATES = (VEHICLE_STATE.GROUP_IS_NOT_READY,)

    class VEHICLE_STATE_LEVEL(object):
        CRITICAL = 'critical'
        INFO = 'info'
        WARNING = 'warning'
        ATTENTION = 'attention'
        RENTABLE = 'rentableBlub'
        ROLE = 'role'

    rentalsController = dependency.descriptor(IRentalsController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)
    igrCtrl = dependency.descriptor(IIGRController)
    itemsCache = dependency.descriptor(IItemsCache)
    __customizationService = dependency.descriptor(ICustomizationService)
    __postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)
    tradeInCtrl = dependency.descriptor(ITradeInController)

    def __init__(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None, extData=None, invData=None):
        self.__postProgressionCtrl.processVehExtData(getVehicleType(typeCompDescr or strCompactDescr), extData)
        if strCompactDescr is not None:
            vehDescr = vehicles.VehicleDescr(compactDescr=strCompactDescr, extData=extData)
        else:
            _, nID, innID = vehicles.parseIntCompactDescr(typeCompDescr)
            vehDescr = vehicles.VehicleDescr(typeID=(nID, innID), extData=extData)
        super(Vehicle, self).__init__(vehDescr.type.compactDescr, proxy, strCD=HasStrCD(strCompactDescr))
        self._descriptor = vehDescr
        self._inventoryID = inventoryID
        self._xp = 0
        self._dailyXPFactor = -1
        self._isElite = False
        self._isFullyElite = False
        self._clanLock = 0
        self._isUnique = self.isHidden
        self._rentPackages = []
        self._rentPackagesInfo = RentPackagesInfo(False, None, None)
        self._isDisabledForBuy = False
        self._isSelected = False
        self._restorePrice = None
        self._groupIDs = set()
        self._rotationGroupNum = 0
        self._rotationBattlesLeft = 0
        self._isRotationGroupLocked = False
        self._isInfiniteRotationGroup = False
        self._unlockedBy = []
        self._perksController = None
        self._postProgression = None
        self._hasNationGroup = hasNationGroup(vehDescr.type.compactDescr)
        self._outfitComponents = {}
        self._isStyleInstalled = False
        if self.isPremiumIGR:
            self._searchableUserName = makeSearchableString(self.shortUserName)
        else:
            self._searchableUserName = makeSearchableString(self.userName)
        invData = invData or dict()
        postProgressionFeatures = None
        if proxy is not None and proxy.inventory.isSynced() and proxy.stats.isSynced() and proxy.shop.isSynced() and proxy.vehicleRotation.isSynced() and proxy.recycleBin.isSynced():
            invDataTmp = proxy.inventory.getItems(GUI_ITEM_TYPE.VEHICLE, inventoryID)
            if invDataTmp is not None:
                invData = invDataTmp
            self._xp = proxy.stats.vehiclesXPs.get(self.intCD, self._xp)
            if proxy.shop.winXPFactorMode == WIN_XP_FACTOR_MODE.ALWAYS or self.intCD not in proxy.stats.multipliedVehicles and not self.isOnlyForEventBattles:
                self._dailyXPFactor = proxy.shop.dailyXPFactor
            self._isElite = not vehDescr.type.unlocksDescrs or self.intCD in proxy.stats.eliteVehicles
            self._isFullyElite = self.isElite and not any((data[1] not in proxy.stats.unlocks for data in vehDescr.type.unlocksDescrs))
            clanDamageLock = proxy.stats.vehicleTypeLocks.get(self.intCD, {}).get(CLAN_LOCK, 0)
            clanNewbieLock = proxy.stats.globalVehicleLocks.get(CLAN_LOCK, 0)
            self._clanLock = clanDamageLock or clanNewbieLock
            self._isDisabledForBuy = self.intCD in proxy.shop.getNotToBuyVehicles()
            invRentData = invData.get('rent')
            if invRentData is not None:
                self._rentInfo = RentalInfoProvider(isRented=True, *invRentData)
            hasAvailableRentPackages, mainRentType, seasonType = self.rentalsController.getRentPackagesInfo(proxy.shop.getVehicleRentPrices().get(self.intCD, {}), self._rentInfo)
            self._rentPackagesInfo = RentPackagesInfo(hasAvailableRentPackages, mainRentType, seasonType)
            self._isSelected = bool(self.invID in proxy.stats.oldVehInvIDs)
            self.createAppliedOutfits(proxy)
            restoreConfig = proxy.shop.vehiclesRestoreConfig
            self._restorePrice = calcVehicleRestorePrice(self.buyPrices.itemPrice.defPrice, proxy.shop)
            self._restoreInfo = proxy.recycleBin.getVehicleRestoreInfo(self.intCD, restoreConfig.restoreDuration, restoreConfig.restoreCooldown)
            self._personalDiscountPrice = proxy.shop.getPersonalVehicleDiscountPrice(self.intCD)
            self._rotationGroupNum = proxy.vehicleRotation.getGroupNum(self.intCD)
            self._rotationBattlesLeft = proxy.vehicleRotation.getBattlesCount(self.rotationGroupNum)
            self._isRotationGroupLocked = proxy.vehicleRotation.isGroupLocked(self.rotationGroupNum)
            self._isInfiniteRotationGroup = proxy.vehicleRotation.isInfinite(self.rotationGroupNum)
            self._unlockedBy = proxy.vehicleRotation.unlockedBy(self.rotationGroupNum)
            postProgressionFeatures = proxy.inventory.getVehPostProgressionFeaturesListByCD(self.intCD)
        if postProgressionFeatures is None and extData and SUPPORT_EXT_DATA_FEATURES in extData:
            postProgressionFeatures = extData[SUPPORT_EXT_DATA_FEATURES]
        self._inventoryCount = 1 if invData.keys() else 0
        self._settings = invData.get('settings', 0)
        self._extraSettings = invData.get('extraSettings', 0)
        self._lock = invData.get('lock', (0, 0))
        self._repairCost, self._health = invData.get('repair', (0, 0))
        self._gun = self.itemsFactory.createVehicleGun(vehDescr.gun.compactDescr, proxy, vehDescr.gun)
        self._turret = self.itemsFactory.createVehicleTurret(vehDescr.turret.compactDescr, proxy, vehDescr.turret)
        self._engine = self.itemsFactory.createVehicleEngine(vehDescr.engine.compactDescr, proxy, vehDescr.engine)
        self._chassis = self.itemsFactory.createVehicleChassis(vehDescr.chassis.compactDescr, proxy, vehDescr.chassis)
        self._radio = self.itemsFactory.createVehicleRadio(vehDescr.radio.compactDescr, proxy, vehDescr.radio)
        self._fuelTank = self.itemsFactory.createVehicleFuelTank(vehDescr.fuelTank.compactDescr, proxy, vehDescr.fuelTank)
        sellPrice = self._calcSellPrice(proxy)
        defaultSellPrice = self._calcDefaultSellPrice(proxy)
        self._sellPrices = ItemPrices(itemPrice=ItemPrice(price=sellPrice, defPrice=defaultSellPrice), itemAltPrice=ITEM_PRICE_EMPTY)
        self._equipment = VehicleEquipment(proxy, vehDescr, invData, postProgressionFeatures)
        defaultCrew = [None] * len(vehDescr.type.crewRoles)
        crewList = invData.get('crew', defaultCrew)
        battleCrewList = invData.get('battleCrewCDs')
        self._bonuses = self._calcCrewBonuses(battleCrewList or crewList, proxy, fromBattle=battleCrewList is not None)
        self._crewIndices = dict([ (invID, idx) for idx, invID in enumerate(crewList) ])
        self._crew = self._buildCrew(battleCrewList or crewList, proxy, fromBattle=battleCrewList is not None)
        self._lastCrew = invData.get('lastCrew')
        if self.canTradeIn:
            self._rentPackagesInfo = RentPackagesInfo(False, 0, 0)
            self._rentPackages = []
            self._maxRentDuration, self._minRentDuration = (0, 0)
        else:
            self._rentPackages = calcRentPackages(self, proxy, self.rentalsController)
            self._maxRentDuration, self._minRentDuration = self.__calcMinMaxRentDuration()
        self._hasModulesToSelect = self.__hasModulesToSelect()
        self.__customState = ''
        self._slotsAnchorsById, self._slotsAnchors = self.__initAnchors()
        if self.__postProgressionCtrl.isDisabledFor(self):
            self._descriptor.installModifications([], rebuildAttrs=False)
            self._equipment.optDevices.dynSlotType = None
        return

    def __initAnchors(self):
        vehDescr = self._descriptor
        slotsAnchors = {cType:{area:{} for area in Area.ALL} for cType in GUI_ITEM_TYPE.CUSTOMIZATIONS}
        slotsAnchorsById = {}
        hullEmblemSlots = EmblemSlotHelper(vehDescr.hull.emblemSlots, Area.HULL)
        if vehDescr.turret.showEmblemsOnGun:
            turretEmblemSlots = EmblemSlotHelper(vehDescr.turret.emblemSlots, Area.GUN)
        else:
            turretEmblemSlots = EmblemSlotHelper(vehDescr.turret.emblemSlots, Area.TURRET)
        for emblemSlotHelper in (hullEmblemSlots, turretEmblemSlots):
            for emblemSlot in emblemSlotHelper.tankAreaSlot:
                areaId = emblemSlotHelper.tankAreaId
                slotType = ANCHOR_TYPE_TO_SLOT_TYPE_MAP.get(emblemSlot.type)
                if slotType is not None:
                    regionIdx = len(slotsAnchors[slotType][areaId])
                    slot = EmblemSlot(emblemSlot, emblemSlotHelper.tankAreaId, regionIdx)
                    slotsAnchors[slotType][areaId][regionIdx] = slot
                    slotsAnchorsById[emblemSlot.slotId] = slot

        chassisCustomizationSlots = SlotHelper(vehDescr.chassis.slotsAnchors, Area.CHASSIS)
        hullCustomizationSlots = SlotHelper(vehDescr.hull.slotsAnchors, Area.HULL)
        turretCustomizationSlots = SlotHelper(vehDescr.turret.slotsAnchors, Area.TURRET)
        gunCustomizationSlots = SlotHelper(vehDescr.gun.slotsAnchors, Area.GUN)
        for slotHelper in (chassisCustomizationSlots,
         hullCustomizationSlots,
         turretCustomizationSlots,
         gunCustomizationSlots):
            for anchor in slotHelper.tankAreaSlot:
                if anchor.type not in ANCHOR_TYPE_TO_SLOT_TYPE_MAP:
                    continue
                slotType = ANCHOR_TYPE_TO_SLOT_TYPE_MAP[anchor.type]
                if slotType in (GUI_ITEM_TYPE.PROJECTION_DECAL,
                 GUI_ITEM_TYPE.MODIFICATION,
                 GUI_ITEM_TYPE.STYLE,
                 GUI_ITEM_TYPE.SEQUENCE,
                 GUI_ITEM_TYPE.ATTACHMENT):
                    areaId = Area.MISC
                else:
                    areaId = slotHelper.tankAreaId
                if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    regionIdx = len(slotsAnchors[slotType][areaId])
                    customizationSlot = ProjectionDecalSlot(anchor, slotHelper.tankAreaId, regionIdx)
                else:
                    if anchor.applyTo is not None:
                        regions = REGIONS_BY_SLOT_TYPE[areaId][slotType]
                        if anchor.applyTo in regions:
                            regionIdx = regions.index(anchor.applyTo)
                        else:
                            continue
                    else:
                        regionIdx = len(slotsAnchors[slotType][areaId])
                    customizationSlot = BaseCustomizationSlot(anchor, slotHelper.tankAreaId, regionIdx)
                slotsAnchors[slotType][areaId][regionIdx] = customizationSlot
                slotsAnchorsById[customizationSlot.slotId] = customizationSlot

        if not slotsAnchors[GUI_ITEM_TYPE.MODIFICATION][Area.MISC]:
            slotsAnchors[GUI_ITEM_TYPE.MODIFICATION][Area.MISC] = slotsAnchors[GUI_ITEM_TYPE.STYLE][Area.MISC]
        return (slotsAnchorsById, slotsAnchors)

    def getAnchors(self, slotType, areaId):
        return self._slotsAnchors.get(slotType, {}).get(areaId, {}).iteritems()

    def getAnchorBySlotId(self, slotType, areaId, regionIdx):
        return self._slotsAnchors.get(slotType, {}).get(areaId, {}).get(regionIdx)

    @property
    def buyPrices(self):
        currency = self._buyPrices.itemPrice.price.getCurrency()
        if self._personalDiscountPrice is not None and self._personalDiscountPrice.get(currency) <= self._buyPrices.itemPrice.price.get(currency):
            currentPrice = self._personalDiscountPrice
        else:
            currentPrice = self._buyPrices.itemPrice.price
        if self.isRented and not self.rentalIsOver:
            buyPrice = currentPrice - self.rentCompensation
        else:
            buyPrice = currentPrice
        return ItemPrices(itemPrice=ItemPrice(price=buyPrice, defPrice=self._buyPrices.itemPrice.defPrice), itemAltPrice=self._buyPrices.itemAltPrice)

    @property
    def searchableUserName(self):
        return self._searchableUserName

    @property
    def searchableShortUserName(self):
        return makeSearchableString(self.shortUserName)

    @property
    def outfits(self):
        vehicleCD = self.descriptor.makeCompactDescr()
        outfits = {season:self.__getOutfit(component, vehicleCD) for season, component in self._outfitComponents.iteritems()}
        return outfits

    def getPersonalDiscountPrice(self):
        return self._personalDiscountPrice

    def getUnlockDescrByIntCD(self, intCD):
        for unlockIdx, data in enumerate(self.descriptor.type.unlocksDescrs):
            if intCD == data[1]:
                return (unlockIdx, data[0], set(data[2:]))

        return (-1, 0, set())

    def initPerksController(self, scopedPerks):
        if not self._perksController:
            self._perksController = PerksParametersController(self.descriptor.type.compactDescr, scopedPerks)

    def stopPerksController(self):
        if self._perksController:
            self._perksController.destroy()
            self._perksController = None
        return

    def getPerksController(self):
        return self._perksController

    def setPerksController(self, perksController):
        self._perksController = perksController

    def _calcSellPrice(self, proxy):
        return self.__calcSellPrice(proxy, self.sellPrices.itemPrice.price)

    def _calcDefaultSellPrice(self, proxy):
        return self.__calcSellPrice(proxy, self.sellPrices.itemPrice.defPrice)

    def _getDescriptor(self):
        return None

    def _calcCrewBonuses(self, crew, proxy, fromBattle):
        bonuses = dict()
        bonuses['equipment'] = 0.0
        for eq in self.consumables.installed.getItems():
            bonuses['equipment'] += eq.crewLevelIncrease

        for battleBooster in self.battleBoosters.installed.getItems():
            bonuses['equipment'] += battleBooster.getCrewBonus(self)

        bonuses['optDevices'] = self.descriptor.miscAttrs['crewLevelIncrease']
        bonuses['commander'] = 0
        commanderEffRoleLevel = 0
        bonuses['brotherhood'] = tankmen.getSkillsConfig().getSkill('brotherhood').crewLevelIncrease
        for tID in crew:
            if tID is None:
                bonuses['brotherhood'] = 0.0
                continue
            tmanInvData = {'compDescr': tID} if fromBattle else proxy.inventory.getItems(GUI_ITEM_TYPE.TANKMAN, tID)
            if not tmanInvData:
                continue
            tdescr = tankmen.TankmanDescr(compactDescr=tmanInvData['compDescr'])
            if 'brotherhood' not in tdescr.skills or tdescr.skills.index('brotherhood') == len(tdescr.skills) - 1 and tdescr.lastSkillLevel != tankmen.MAX_SKILL_LEVEL:
                bonuses['brotherhood'] = 0.0
            if tdescr.role == Tankman.ROLES.COMMANDER:
                factor, addition = tdescr.efficiencyOnVehicle(self.descriptor)
                commanderEffRoleLevel = round(tdescr.roleLevel * factor + addition)

        bonuses['commander'] += round((commanderEffRoleLevel + bonuses['brotherhood'] + bonuses['equipment']) / tankmen.COMMANDER_ADDITION_RATIO)
        return bonuses

    def _buildCrew(self, crew, proxy, fromBattle):
        crewItems = list()
        crewRoles = self.descriptor.type.crewRoles
        for idx, tankmanID in enumerate(crew):
            tankman = None
            if tankmanID is not None:
                if fromBattle:
                    tmanInvData = {'compDescr': tankmanID,
                     'invID': -1}
                else:
                    tmanInvData = proxy.inventory.getItems(GUI_ITEM_TYPE.TANKMAN, tankmanID)
                tankman = self.itemsFactory.createTankman(strCompactDescr=tmanInvData['compDescr'], inventoryID=tmanInvData.get('invID', tankmanID), vehicle=self, proxy=proxy)
            crewItems.append((idx, tankman))

        return sortCrew(crewItems, crewRoles)

    @staticmethod
    def __crewSort(t1, t2):
        return 0 if t1 is None or t2 is None else t1.__cmp__(t2)

    def _parseCompDescr(self, compactDescr):
        nId, innID = vehicles.parseVehicleCompactDescr(compactDescr)
        return (GUI_ITEM_TYPE.VEHICLE, nId, innID)

    def createAppliedOutfits(self, proxy):
        styleOutfitData = proxy.inventory.getOutfitData(self.intCD, SeasonType.ALL)
        styleProgressionLevel = 0
        if styleOutfitData is not None:
            self._isStyleInstalled = True
            styledOutfitComponent = customizations.parseCompDescr(styleOutfitData)
            styleProgressionLevel = styledOutfitComponent.styleProgressionLevel
            styleIntCD = vehicles.makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, styledOutfitComponent.styleId)
            style = vehicles.getItemByCompactDescr(styleIntCD)
        else:
            style = None
            outfitsPool = proxy.inventory.getC11nOutfitsFromPool(self.intCD)
            isCustomOutfitStored = outfitsPool and outfitsPool[0][0] == CUSTOM_STYLE_POOL_ID
            if not isCustomOutfitStored:
                self._isStyleInstalled = False
            else:
                isCustomOutfitInstalled = any((proxy.inventory.getOutfitData(self.intCD, s) for s in SeasonType.SEASONS))
                self._isStyleInstalled = not isCustomOutfitInstalled
        self._outfitComponents = {season:self._getOutfitComponent(proxy, style, styleProgressionLevel, season) for season in SeasonType.SEASONS}
        return

    def _getOutfitComponent(self, proxy, style, styleProgressionLevel, season):
        if style is not None:
            return self.__getStyledOutfitComponent(proxy, style, styleProgressionLevel, season)
        else:
            return self.__getEmptyOutfitComponent() if self._isStyleInstalled else self.__getCustomOutfitComponent(proxy, season)

    @classmethod
    def _parserOptDevs(cls, layoutList, proxy):
        result = list()
        for i in xrange(len(layoutList)):
            optDevDescr = layoutList[i]
            result.append(cls.itemsFactory.createOptionalDevice(optDevDescr.compactDescr, proxy) if optDevDescr is not None else None)

        return result

    @property
    def iconContour(self):
        return getContourIconPath(self.name)

    @property
    def iconUnique(self):
        return getUniqueIconPath(self.name, withLightning=False)

    @property
    def iconUniqueLight(self):
        return getUniqueIconPath(self.name, withLightning=True)

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        name = getNationLessName(self.name)
        return RES_SHOP_EXT.getVehicleIcon(size, name)

    @property
    def invID(self):
        return self._inventoryID

    @property
    def xp(self):
        return self._xp

    @property
    def dailyXPFactor(self):
        return self._dailyXPFactor

    @dailyXPFactor.setter
    def dailyXPFactor(self, value):
        self._dailyXPFactor = value

    @property
    def isElite(self):
        return self._isElite

    @property
    def isFullyElite(self):
        return self._isFullyElite

    def getEliteStatusProgress(self):
        vehType = self.descriptor.type
        installable = {intCD for intCD in vehType.installableComponents if getTypeOfCompactDescr(intCD) in GUI_ITEM_TYPE.VEHICLE_MODULES}
        unlocksDescrs = {data[1] for data in vehType.unlocksDescrs}
        total = unlocksDescrs | installable
        if not self.hasTurrets:
            for turretCD in filterIntCDsByItemType(total, GUI_ITEM_TYPE.TURRET):
                total.remove(turretCD)

        unlocked = total & self.itemsCache.items.stats.unlocks
        toUnlock = total - unlocked
        return EliteStatusProgress(unlocked, toUnlock, total)

    @property
    def clanLock(self):
        return self._clanLock

    @property
    def isUnique(self):
        return self._isUnique

    @property
    def rentPackages(self):
        return self._rentPackages

    @property
    def hasRentPackages(self):
        return self._rentPackagesInfo.hasAvailableRentPackages

    @property
    def getRentPackagesInfo(self):
        return self._rentPackagesInfo

    @property
    def isDisabledForBuy(self):
        return self._isDisabledForBuy

    @property
    def isSelected(self):
        return self._isSelected

    @property
    def restorePrice(self):
        return self._restorePrice

    @property
    def isTradeInAvailable(self):
        availableToBuy = False
        if self.tradeInCtrl.isEnabled():
            availableToBuy = self.intCD in self.tradeInCtrl.getAllPossibleVehiclesToBuy() and self.isUnlocked and not self.isRestorePossible() and not self.isRented
        return availableToBuy

    @property
    def canTradeIn(self):
        return self.isTradeInAvailable and not self.isInInventory and not self.isDisabledForBuy

    @property
    def isTradeOffAvailable(self):
        availableToSell = False
        if self.tradeInCtrl.isEnabled():
            availableToSell = self.intCD in self.tradeInCtrl.getAllPossibleVehiclesToSell() and self.isPurchased
        return availableToSell

    @property
    def canTradeOff(self):
        return self.isTradeOffAvailable and not self.canNotBeSold

    @property
    def discountPercentage(self):
        buyPrice = self.tradeInBuyPrice.gold or 0
        price = self.buyPrices.itemPrice.defPrice.gold or buyPrice or 1
        return math.floor(100 * (1 - buyPrice / float(price)))

    @property
    def isFreeExchange(self):
        if not self.tradeInCtrl.isEnabled():
            return False
        else:
            tradeInInfo = self.tradeInCtrl.getConfig().getTradeInInfoByVehicleToSell(self.intCD)
            return False if tradeInInfo is None else tradeInInfo.conversionRule.freeExchange

    @property
    def groupIDs(self):
        return self._groupIDs

    @property
    def tradeOffPriceFactor(self):
        return 0 if not self.tradeInCtrl.isEnabled() else self.tradeInCtrl.getConfig().getSellPriceFactorFor(self.intCD)

    @property
    def tradeOffPrice(self):
        return MONEY_UNDEFINED if self.buyPrices.itemPrice.defPrice.gold is None else Money(gold=int(math.ceil(self.tradeOffPriceFactor * self.buyPrices.itemPrice.defPrice.gold)))

    @property
    def tradeInBuyPrice(self):
        return self.tradeInCtrl.getTradeInPrice(self).price

    @property
    def rotationGroupNum(self):
        return self._rotationGroupNum

    @property
    def rotationBattlesLeft(self):
        return self._rotationBattlesLeft

    @property
    def isRotationGroupLocked(self):
        return self._isRotationGroupLocked

    @property
    def unlockedBy(self):
        return self._unlockedBy

    @property
    def isInfiniteRotationGroup(self):
        return self._isInfiniteRotationGroup

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value

    @property
    def lock(self):
        return self._lock

    @property
    def repairCost(self):
        return self._repairCost

    @repairCost.setter
    def repairCost(self, value):
        self._repairCost = value

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value

    @property
    def gun(self):
        return self._gun

    @gun.setter
    def gun(self, value):
        self._gun = value

    @property
    def turret(self):
        return self._turret

    @turret.setter
    def turret(self, value):
        self._turret = value

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, value):
        self._engine = value

    @property
    def chassis(self):
        return self._chassis

    @chassis.setter
    def chassis(self, value):
        self._chassis = value

    @property
    def radio(self):
        return self._radio

    @radio.setter
    def radio(self, value):
        self._radio = value

    @property
    def fuelTank(self):
        return self._fuelTank

    @fuelTank.setter
    def fuelTank(self, value):
        self._fuelTank = value

    @property
    def setupLayouts(self):
        return self._equipment.setupLayouts

    @property
    def optDevices(self):
        return self._equipment.optDevices

    @property
    def shells(self):
        return self._equipment.shells

    @property
    def consumables(self):
        return self._equipment.consumables

    @property
    def battleBoosters(self):
        return self._equipment.battleBoosters

    @property
    def battleAbilities(self):
        return self._equipment.battleAbilities

    @property
    def modules(self):
        return (self.chassis,
         self.turret if self.hasTurrets else None,
         self.gun,
         self.engine,
         self.radio)

    @property
    def bonuses(self):
        return self._bonuses

    @property
    def crewIndices(self):
        return self._crewIndices

    @property
    def crew(self):
        return self._crew

    @crew.setter
    def crew(self, value):
        self._crew = value

    @property
    def lastCrew(self):
        return self._lastCrew

    @property
    def hasModulesToSelect(self):
        return self._hasModulesToSelect

    @property
    def isRentable(self):
        return self.hasRentPackages and not self.isPurchased

    @property
    def isPurchased(self):
        return self.isInInventory and not self.rentInfo.isRented

    def isPreviewAllowed(self):
        return not self.isInInventory and not self.isSecret

    @property
    def rentExpiryTime(self):
        return self.rentInfo.rentExpiryTime

    @property
    def rentCompensation(self):
        return self.rentInfo.compensations

    @property
    def isRentAvailable(self):
        return self.maxRentDuration - self.rentLeftTime >= self.minRentDuration if self._rentPackagesInfo.mainRentType == RentType.TIME_RENT else self._rentPackagesInfo.hasAvailableRentPackages and self._rentPackagesInfo.mainRentType in (RentType.SEASON_RENT, RentType.SEASON_CYCLE_RENT)

    @property
    def isRentPromotion(self):
        return checkForTags(self.tags, VEHICLE_TAGS.RENT_PROMOTION) and self.rentExpiryState and self.isRentable and self.isRentAvailable and self.isUnlocked

    @property
    def minRentPrice(self):
        minRentPackage = self.getRentPackage()
        return minRentPackage.get('rentPrice', MONEY_UNDEFINED) if minRentPackage is not None else MONEY_UNDEFINED

    @property
    def isRented(self):
        return self.rentInfo.isRented

    @property
    def currentSeasonRent(self):
        return self.rentInfo.getActiveSeasonRent()

    @property
    def rentLeftTime(self):
        return self.rentInfo.getTimeLeft()

    @property
    def maxRentDuration(self):
        return self._maxRentDuration

    @property
    def minRentDuration(self):
        return self._minRentDuration

    @property
    def rentalIsOver(self):
        return self.isRented and self.rentExpiryState and not self.isSelected

    @property
    def rentalIsActive(self):
        return self.isRented and not self.rentExpiryState

    @property
    def rentLeftBattles(self):
        return self.rentInfo.battlesLeft

    @property
    def isSeasonRent(self):
        return bool(self.rentInfo.seasonRent)

    @property
    def rentExpiryState(self):
        return self.rentInfo.getExpiryState()

    @property
    def isWotPlusRent(self):
        return self._rentInfo.isWotPlus

    @property
    def isTelecomRent(self):
        return self._rentInfo.isTelecomRent

    @property
    def type(self):
        return set(vehicles.VEHICLE_CLASS_TAGS & self.tags).pop()

    @property
    def typeUserName(self):
        return getTypeUserName(self.type, self.isElite)

    @property
    def typeBigIconResource(self):
        return getTypeBigIconResource(self.type, self.isElite)

    @property
    def hasTurrets(self):
        vDescr = self.descriptor
        return len(vDescr.hull.fakeTurrets['lobby']) != len(vDescr.turrets)

    @property
    def hasBattleTurrets(self):
        vDescr = self.descriptor
        return len(vDescr.hull.fakeTurrets['battle']) != len(vDescr.turrets)

    @property
    def ammoMaxSize(self):
        return self.descriptor.gun.maxAmmo

    @property
    def ammoMinSize(self):
        return self.descriptor.gun.maxAmmo * NOT_FULL_AMMO_MULTIPLIER

    @property
    def isAmmoFull(self):
        return sum((s.count for s in self.shells.installed.getItems())) >= self.ammoMinSize

    @property
    def isAmmoNotFullInSetups(self):
        return self.shells.setupLayouts.isAmmoNotFull(self.ammoMinSize)

    @property
    def isAmmoCanSwitch(self):
        return self.isSetupSwitchActive(TankSetupGroupsId.EQUIPMENT_AND_SHELLS)

    @property
    def isTooHeavy(self):
        return not self.descriptor.isWeightConsistent()

    @property
    def hasCrew(self):
        return findFirst(lambda x: x[1] is not None, self.crew) is not None

    @property
    def hasShells(self):
        return self.shells.setupLayouts.isAmmoFull(minAmmo=1)

    @property
    def hasConsumables(self):
        return bool(self.consumables.setupLayouts.getUniqueItems())

    @property
    def hasOptionalDevices(self):
        return bool(self.optDevices.setupLayouts.getUniqueItems())

    @property
    def modelState(self):
        if self.health < 0:
            return Vehicle.VEHICLE_STATE.EXPLODED
        return Vehicle.VEHICLE_STATE.DESTROYED if self.repairCost > 0 and self.health == 0 else Vehicle.VEHICLE_STATE.UNDAMAGED

    @property
    def isWheeledTech(self):
        return self._descriptor.type.isWheeledVehicle

    @property
    def isTrackWithinTrack(self):
        return self._descriptor.isTrackWithinTrack

    @property
    def miscAttrs(self):
        return self._descriptor.miscAttrs

    @property
    def hasNationGroup(self):
        isEnabled = self.lobbyContext.getServerSettings().isNationChangeEnabled()
        return isEnabled and self._hasNationGroup

    @property
    def isNationChangeAvailable(self):
        return self.hasNationGroup and not self.isLocked and not self.isBroken and (self.isPurchased or self.isRented)

    def isAmmoFullInSetups(self, setupIdx=None):
        return self.shells.setupLayouts.isAmmoFull(setupIdx, self.ammoMinSize)

    def getAllNationGroupVehs(self, proxy):
        nationGroupVehs = [ proxy.getItemByCD(cd) for cd in iterVehTypeCDsInNationGroup(self.intCD) ]
        nationGroupVehs.insert(0, self)
        return nationGroupVehs

    def getC11nItemNoveltyCounter(self, proxy, item):
        newItems = proxy.inventory.getC11nItemsNoveltyCounters(self._descriptor.type)
        return newItems.get(item.intCD, 0)

    def getC11nItemsNoveltyCounter(self, proxy, itemTypes=None, season=None, itemFilter=None):
        count = 0
        newItems = proxy.inventory.getC11nItemsNoveltyCounters(self._descriptor.type)
        for itemCD, qtyItems in newItems.iteritems():
            item = proxy.getItemByCD(itemCD)
            if not item.mayInstall(self):
                continue
            if itemFilter is not None and not itemFilter(item):
                continue
            if (itemTypes is None or item.itemTypeID in itemTypes) and (season is None or item.season & season):
                count += qtyItems

        return count

    def getNewC11nItems(self, proxy):
        newItems = []
        for itemCD in proxy.inventory.getC11nItemsNoveltyCounters(self._descriptor.type).iterkeys():
            item = proxy.getItemByCD(itemCD)
            if item.id == EMPTY_ITEM_ID:
                continue
            newItems.append(item)

        return newItems

    def getState(self, isCurrentPlayer=True):
        ms = self.modelState
        if not self.isInInventory and isCurrentPlayer:
            ms = Vehicle.VEHICLE_STATE.NOT_PRESENT
        if self.isInBattle:
            ms = Vehicle.VEHICLE_STATE.BATTLE
        elif self.rentalIsOver:
            ms = Vehicle.VEHICLE_STATE.RENTAL_IS_OVER
            if self.isPremiumIGR:
                ms = Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_OVER
            elif self.isTelecom:
                ms = Vehicle.VEHICLE_STATE.DEAL_IS_OVER
        elif self.isDisabledInPremIGR:
            ms = Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY
        elif self.isInPrebattle:
            ms = Vehicle.VEHICLE_STATE.IN_PREBATTLE
        elif self.isDisabled:
            ms = Vehicle.VEHICLE_STATE.DISABLED
        elif self.isLocked:
            ms = Vehicle.VEHICLE_STATE.LOCKED
        elif self.isDisabledInRoaming:
            ms = Vehicle.VEHICLE_STATE.SERVER_RESTRICTION
        elif self.isRotationGroupLocked:
            ms = Vehicle.VEHICLE_STATE.ROTATION_GROUP_LOCKED
        ms = self.checkUndamagedState(ms, isCurrentPlayer)
        ms = self.__getRentableState(ms, isCurrentPlayer)
        if ms in Vehicle.CAN_SELL_STATES and self.__customState in Vehicle.VEHICLE_STATE.UNSUITABLE:
            ms = self.__customState
        return (ms, self.__getStateLevel(ms))

    def setCustomState(self, state):
        self.__customState = state

    def getCustomState(self):
        return self.__customState

    def clearCustomState(self):
        self.__customState = ''

    def isCustomStateSet(self):
        return self.__customState != ''

    def checkUndamagedState(self, state, isCurrnentPlayer=True):
        if state == Vehicle.VEHICLE_STATE.UNDAMAGED and isCurrnentPlayer:
            if self.isBroken:
                return Vehicle.VEHICLE_STATE.DAMAGED
            if self.isTooHeavy:
                return Vehicle.VEHICLE_STATE.TOO_HEAVY
            if not self.isCrewFull:
                return Vehicle.VEHICLE_STATE.CREW_NOT_FULL
            if not self.isAmmoFull:
                return Vehicle.VEHICLE_STATE.AMMO_NOT_FULL
            if not self.isRotationGroupLocked and self.rotationGroupNum != 0:
                return Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
            if self.__customState == Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE:
                return self.__customState
        return state

    def __getRentableState(self, state, isCurrentPlayer):
        if isCurrentPlayer and self.isRentPromotion and self._rentPackagesInfo.hasAvailableRentPackages:
            if not self.isRented:
                return Vehicle.VEHICLE_STATE.RENTABLE
            return Vehicle.VEHICLE_STATE.RENTABLE_AGAIN
        return state

    def isRotationApplied(self):
        return self.rotationGroupNum != 0

    def isGroupReady(self):
        return (True, '')

    def __getStateLevel(self, state):
        if state in (Vehicle.VEHICLE_STATE.CREW_NOT_FULL,
         Vehicle.VEHICLE_STATE.DAMAGED,
         Vehicle.VEHICLE_STATE.EXPLODED,
         Vehicle.VEHICLE_STATE.DESTROYED,
         Vehicle.VEHICLE_STATE.SERVER_RESTRICTION,
         Vehicle.VEHICLE_STATE.RENTAL_IS_OVER,
         Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_OVER,
         Vehicle.VEHICLE_STATE.TOO_HEAVY,
         Vehicle.VEHICLE_STATE.AMMO_NOT_FULL,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         Vehicle.VEHICLE_STATE.DEAL_IS_OVER,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT,
         Vehicle.VEHICLE_STATE.ROTATION_GROUP_LOCKED):
            return Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        if state in (Vehicle.VEHICLE_STATE.UNDAMAGED, Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED):
            return Vehicle.VEHICLE_STATE_LEVEL.INFO
        if state in (Vehicle.VEHICLE_STATE.RENTABLE, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN):
            return Vehicle.VEHICLE_STATE_LEVEL.RENTABLE
        return Vehicle.VEHICLE_STATE_LEVEL.ATTENTION if state in (Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE,) else Vehicle.VEHICLE_STATE_LEVEL.WARNING

    @property
    def isPremium(self):
        return checkForTags(self.tags, VEHICLE_TAGS.PREMIUM)

    @property
    def isPremiumIGR(self):
        return checkForTags(self.tags, VEHICLE_TAGS.PREMIUM_IGR)

    @property
    def isSecret(self):
        return checkForTags(self.tags, VEHICLE_TAGS.SECRET)

    @property
    def isSpecial(self):
        return checkForTags(self.tags, VEHICLE_TAGS.SPECIAL)

    @property
    def isCollectible(self):
        return checkForTags(self.tags, CollectorVehicleConsts.COLLECTOR_VEHICLES_TAG)

    @property
    def isSupply(self):
        return checkForTags(self.tags, VEHICLE_TAGS.SUPPLY)

    @property
    def isExcludedFromSandbox(self):
        return checkForTags(self.tags, VEHICLE_TAGS.EXCLUDED_FROM_SANDBOX)

    @property
    def isObserver(self):
        return checkForTags(self.tags, VEHICLE_TAGS.OBSERVER)

    @property
    def isCommander(self):
        return checkForTags(self.tags, VEHICLE_TAGS.COMMANDER)

    @property
    def isEvent(self):
        return self.isOnlyForEventBattles

    @property
    def isDisabledInRoaming(self):
        return checkForTags(self.tags, VEHICLE_TAGS.DISABLED_IN_ROAMING) and self.lobbyContext.getServerSettings().roaming.isInRoaming()

    @property
    def canNotBeSold(self):
        return checkForTags(self.tags, VEHICLE_TAGS.CANNOT_BE_SOLD)

    @property
    def isUnrecoverable(self):
        return checkForTags(self.tags, VEHICLE_TAGS.UNRECOVERABLE)

    @property
    def isCrewLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.CREW_LOCKED)

    @property
    def isOutfitLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.OUTFIT_LOCKED)

    @property
    def isProgressionDecalsOnly(self):
        return checkForTags(self.tags, VEHICLE_TAGS.PROGRESSION_DECALS_ONLY)

    @property
    def isCrewSkillLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.CREW_SKILLS_LOCKED)

    @property
    def isShellsLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.SHELLS_LOCKED)

    @property
    def isDeviceLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.DEVICE_LOCKED)

    @property
    def isDisabledInPremIGR(self):
        return self.isPremiumIGR and self.igrCtrl.getRoomType() != constants.IGR_TYPE.PREMIUM

    @property
    def name(self):
        return self.descriptor.type.name

    @property
    def userName(self):
        return getUserName(self.descriptor.type)

    @property
    def longUserName(self):
        typeInfo = getTypeInfoByName('vehicle')
        tagsDump = [ typeInfo['tags'][tag]['userString'] for tag in self.tags if typeInfo['tags'][tag]['userString'] != '' ]
        return '%s %s' % (''.join(tagsDump), getUserName(self.descriptor.type))

    @property
    def shortUserName(self):
        return getShortUserName(self.descriptor.type)

    @property
    def level(self):
        return self.descriptor.type.level

    @property
    def fullDescription(self):
        description = self.descriptor.type.description
        return description if description.find('_descr') == -1 else ''

    @property
    def shortDescriptionSpecial(self):
        description = self.descriptor.type.shortDescriptionSpecial
        return description if description.find('_short_special') == -1 else ''

    @property
    def longDescriptionSpecial(self):
        description = self.descriptor.type.longDescriptionSpecial
        return description if description.find('_long_special') == -1 else ''

    @property
    def tags(self):
        return self.descriptor.type.tags

    @property
    def rotationGroupIdx(self):
        return self.rotationGroupNum - 1

    @property
    def canSell(self):
        if not self.isInInventory:
            return False
        st, _ = self.getState()
        if self.isRented:
            if not self.rentalIsOver:
                return False
            if st in (self.VEHICLE_STATE.RENTAL_IS_OVER, self.VEHICLE_STATE.IGR_RENTAL_IS_OVER, self.VEHICLE_STATE.RENTABLE_AGAIN):
                st = self.checkUndamagedState(self.modelState)
        return st in self.CAN_SELL_STATES and not checkForTags(self.tags, VEHICLE_TAGS.CANNOT_BE_SOLD)

    @property
    def isReadyToTradeOff(self):
        return self.canTradeOff and self.getState()[0] not in self.TRADE_OFF_NOT_READY_STATES

    @property
    def isLocked(self):
        return self.lock[0] != LOCK_REASON.NONE

    @property
    def isInBattle(self):
        return self.lock[0] == LOCK_REASON.ON_ARENA

    @property
    def isInPrebattle(self):
        return self.lock[0] in (LOCK_REASON.PREBATTLE, LOCK_REASON.UNIT)

    @property
    def isAwaitingBattle(self):
        return self.lock[0] == LOCK_REASON.IN_QUEUE

    @property
    def isInUnit(self):
        return self.lock[0] == LOCK_REASON.UNIT

    @property
    def isDisabled(self):
        return self.lock[0] == LOCK_REASON.BREAKER

    @property
    def typeOfLockingArena(self):
        return None if not self.isLocked else self.lock[1]

    @property
    def isBroken(self):
        return self.repairCost > 0

    @property
    def isAlive(self):
        return not self.isBroken and not self.isLocked

    @property
    def isCrewFull(self):
        crew = [ tman for _, tman in self.crew ]
        return None not in crew and len(crew)

    @property
    def isOnlyForEventBattles(self):
        return checkForTags(self.tags, VEHICLE_TAGS.EVENT)

    @property
    def isOnlyForEpicBattles(self):
        return checkForTags(self.tags, VEHICLE_TAGS.EPIC_BATTLES)

    @property
    def isEpicActionVehicle(self):
        return self.isOnlyForEpicBattles and self.isRented

    @property
    def isOnlyForBattleRoyaleBattles(self):
        return checkForTags(self.tags, VEHICLE_TAGS.BATTLE_ROYALE)

    @property
    def isOnlyForMapsTrainingBattles(self):
        return checkForTags(self.tags, VEHICLE_TAGS.MAPS_TRAINING)

    @property
    def isOnlyForClanWarsBattles(self):
        return checkForTags(self.tags, VEHICLE_TAGS.CLAN_WARS_BATTLES)

    @property
    def isTelecom(self):
        return checkForTags(self.tags, VEHICLE_TAGS.TELECOM)

    @property
    def isTelecomDealOver(self):
        return self.isTelecom and self.rentExpiryState

    @property
    def isStyleInstalled(self):
        return self._isStyleInstalled

    @property
    def isEquipmentLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.EQUIPMENT_LOCKED)

    @property
    def isOptionalDevicesLocked(self):
        return checkForTags(self.tags, VEHICLE_TAGS.OPTIONAL_DEVICES_LOCKED)

    @property
    def isEarnCrystals(self):
        return checkForTags(self.tags, VEHICLE_TAGS.EARN_CRYSTALS)

    def getCrystalsEarnedInfo(self):
        limit = 0
        stats = self.itemsCache.items.stats
        if self.isEarnCrystals:
            limits = self.lobbyContext.getServerSettings().getCrystalRewardConfig().limits
            if limits is not None:
                if self.level in limits.level:
                    limit = limits.level[self.level]
                if self.intCD in limits.vehicle:
                    limit = limits.vehicle[self.intCD]
        return CrystalsEarnedInfo(stats.getWeeklyVehicleCrystals(self.intCD), limit)

    def hasLockMode(self):
        isBS = prb_getters.isBattleSession()
        if isBS:
            isBSVehicleLockMode = bool(prb_getters.getPrebattleSettings()[PREBATTLE_SETTING_NAME.VEHICLE_LOCK_MODE])
            if isBSVehicleLockMode and self.clanLock > 0:
                return True
        return False

    def isReadyToPrebattle(self, checkForRent=True):
        if checkForRent and self.rentalIsOver:
            return False
        if not self.isGroupReady()[0]:
            return False
        result = not self.hasLockMode()
        if result:
            result = not self.isBroken and self.isCrewFull and not self.isTooHeavy and not self.isDisabledInPremIGR and not self.isInBattle and not self.isRotationGroupLocked and not self.isDisabled
        return result

    @property
    def isReadyToFight(self):
        if self.rentalIsOver:
            return False
        if not self.isGroupReady()[0]:
            return False
        result = not self.hasLockMode()
        if result:
            result = self.isAlive and self.isCrewFull and not self.isTooHeavy and not self.isDisabledInRoaming and not self.isDisabledInPremIGR and not self.isRotationGroupLocked
        return result

    @property
    def activeInNationGroup(self):
        return not bool(self._extraSettings & VEHICLE_EXTRA_SETTING_FLAG.NOT_ACTIVE_IN_NATION_GROUP)

    @property
    def isXPToTman(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.XP_TO_TMAN)

    @property
    def isAutoRepair(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.AUTO_REPAIR)

    @property
    def isAutoLoad(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.AUTO_LOAD)

    @property
    def isAutoEquip(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.AUTO_EQUIP)

    def isAutoBattleBoosterEquip(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER)

    @property
    def isFavorite(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.GROUP_0)

    @property
    def isAutoRentStyle(self):
        return bool(self.settings & VEHICLE_SETTINGS_FLAG.AUTO_RENT_CUSTOMIZATION)

    @property
    def role(self):
        return self._descriptor.type.role

    @property
    def roleLabel(self):
        return constants.ROLE_TYPE_TO_LABEL.get(self.role)

    @property
    def roleActions(self):
        return self._descriptor.type.actions

    @property
    def roleActionsLabels(self):
        actions = self.roleActions
        if actions:
            return [ constants.ACTION_TYPE_TO_LABEL.get(action) for action in actions ]

    @property
    def typeDescr(self):
        return self._descriptor.type

    @property
    def compactDescr(self):
        return self._descriptor.type.compactDescr

    @property
    def isPostProgressionActive(self):
        return self.postProgression.isActive(self)

    @property
    def isPostProgressionExists(self):
        return self.postProgression.isExists()

    @property
    def isRoleSlotActive(self):
        return self.postProgression.isRoleSlotActive(self)

    @property
    def postProgression(self):
        if self._postProgression is None:
            self._postProgression = self.itemsCache.items.getVehPostProgression(self.intCD, self._descriptor.type)
        return self._postProgression

    def isRoleSlotExists(self, externalState=None):
        return self.postProgression.isRoleSlotExists(externalState)

    def postProgressionAvailability(self, unlockOnly=False):
        return self.postProgression.isAvailable(self, unlockOnly)

    def clearPostProgression(self):
        self._postProgression = None
        self._descriptor.installModifications(self.postProgression.getActiveModifications(self))
        return

    def installPostProgression(self, customState, ignoreDisabled=False, rebuildAttrs=True):
        self._postProgression = self.postProgression.clone()
        self._postProgression.setState(customState)
        self._descriptor.installModifications(self.postProgression.getActiveModifications(self, ignoreDisabled), rebuildAttrs=rebuildAttrs)

    def installPostProgressionItem(self, postProgressionItem):
        self._postProgression = postProgressionItem
        self._descriptor.installModifications(self.postProgression.getActiveModifications(self))

    def isSetupSwitchActive(self, groupID):
        return self.postProgression.isSetupSwitchActive(self, groupID)

    def isCustomizationEnabled(self):
        locked = False
        if self.__prbDispatcher is not None:
            permission = self.__prbDispatcher.getGUIPermissions()
            if permission is not None:
                locked = not permission.canChangeVehicle()
        return not self.isOnlyForEventBattles and not self.isInBattle and self.isInInventory and not self.isLocked and not locked and not self.isBroken and not self.isOutfitLocked and not self.isDisabled

    def isAutoLoadFull(self):
        return self.shells.installed == self.shells.layout if self.isAutoLoad else True

    def isAutoEquipFull(self):
        return self.consumables.installed == self.consumables.layout if self.isAutoEquip else True

    def mayPurchase(self, money):
        if self.isOnlyForEventBattles:
            return (False, 'isDisabledForBuy')
        if self.isDisabledForBuy:
            return (False, 'isDisabledForBuy')
        return (False, 'premiumIGR') if self.isPremiumIGR else super(Vehicle, self).mayPurchase(money)

    def mayRent(self, money):
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE)
        if self.isDisabledForBuy and not self.isRentable:
            return (False, GUI_ITEM_ECONOMY_CODE.RENTAL_DISABLED)
        if self.isRentable and not self.isRentAvailable:
            return (False, GUI_ITEM_ECONOMY_CODE.RENTAL_TIME_EXCEEDED)
        minRentPrice = self.minRentPrice
        return self._isEnoughMoney(minRentPrice, money) if minRentPrice else (False, GUI_ITEM_ECONOMY_CODE.NO_RENT_PRICE)

    def mayRestore(self, money):
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE)
        return (False, GUI_ITEM_ECONOMY_CODE.RESTORE_DISABLED) if not self.isRestoreAvailable() or constants.IS_CHINA and self.rentalIsActive else self._isEnoughMoney(self.restorePrice, money)

    def mayRestoreWithExchange(self, money, exchangeRate):
        mayRestore, reason = self.mayRestore(money)
        if mayRestore:
            return mayRestore
        if reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CREDITS and money.isSet(Currency.GOLD):
            money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
            mayRestore, reason = self._isEnoughMoney(self.restorePrice, money)
            return mayRestore
        return False

    def getDisclaimerTag(self):
        disclaimers = set(DISCLAIMER_TAGS & self.tags)
        if len(disclaimers) > 1:
            _logger.warning("Vehicle has several disclaimer tags. This design isn't provided and only one will be used.")
        return disclaimers.pop() if disclaimers else ''

    def getDisclaimerUrl(self):
        vehicleDisclaimerURLs = GUI_SETTINGS.vehicleDisclaimerURLs
        return vehicleDisclaimerURLs.get(self.getDisclaimerTag(), '')

    def getRentPackage(self, rentID=None):
        if rentID is not None:
            for package in self.rentPackages:
                if package.get('rentID', None) == rentID:
                    return package

        elif self.rentPackages:
            return min(self.rentPackages, key=itemgetter('rentPrice'))
        return

    def getGUIEmblemID(self):
        return self.icon

    def getRentPackageActionPrc(self, rentID=None):
        package = self.getRentPackage(rentID)
        return getActionPrc(package['rentPrice'], package['defaultRentPrice']) if package else 0

    def getAutoUnlockedItems(self):
        return self.descriptor.type.autounlockedItems[:]

    def getAutoUnlockedItemsMap(self):
        return dict(((vehicles.getItemByCompactDescr(nodeCD).itemTypeName, nodeCD) for nodeCD in self.descriptor.type.autounlockedItems))

    def getUnlocksDescrs(self):
        for unlockIdx, data in enumerate(self.descriptor.type.unlocksDescrs):
            yield (unlockIdx,
             data[0],
             data[1],
             set(data[2:]))

    def getUnlocksDescr(self, unlockIdx):
        try:
            data = self.descriptor.type.unlocksDescrs[unlockIdx]
        except IndexError:
            data = (0, 0, set())

        return (data[0], data[1], set(data[2:]))

    def getPerfectCrew(self):
        return self.getCrewBySkillLevels(100)

    def getCrewWithoutSkill(self, skillName):
        crewItems = list()
        crewRoles = self.descriptor.type.crewRoles
        for slotIdx, tman in self.crew:
            if tman and skillName in tman.skillsMap:
                tmanDescr = tman.descriptor
                skills = tmanDescr.skills[:]
                if tmanDescr.skillLevel(skillName) < tankmen.MAX_SKILL_LEVEL:
                    lastSkillLevel = tankmen.MAX_SKILL_LEVEL
                else:
                    lastSkillLevel = tmanDescr.lastSkillLevel
                skills.remove(skillName)
                unskilledTman = self.itemsFactory.createTankman(tankmen.generateCompactDescr(tmanDescr.getPassport(), tmanDescr.vehicleTypeID, tmanDescr.role, tmanDescr.roleLevel, skills, lastSkillLevel), vehicle=self)
                crewItems.append((slotIdx, unskilledTman))
            crewItems.append((slotIdx, tman))

        return sortCrew(crewItems, crewRoles)

    def getCrewBySkillLevels(self, defRoleLevel, skillsByIdxs=None, levelByIdxs=None, nativeVehsByIdxs=None, activateBrotherhood=False):
        skillsByIdxs = skillsByIdxs or {}
        levelByIdxs = levelByIdxs or {}
        nativeVehsByIdxs = nativeVehsByIdxs or {}
        crewItems = list()
        crewRoles = self.descriptor.type.crewRoles
        brotherhoodActive = skillsByIdxs and all((BROTHERHOOD_SKILL_NAME in skills for skills in skillsByIdxs.values()))
        for idx, _ in enumerate(crewRoles):
            defRoleLevel = levelByIdxs.get(idx, defRoleLevel)
            if defRoleLevel is not None:
                role = self.descriptor.type.crewRoles[idx][0]
                nativeVehicle = nativeVehsByIdxs.get(idx)
                if nativeVehicle is not None:
                    nationID, vehicleTypeID = nativeVehicle.descriptor.type.id
                else:
                    nationID, vehicleTypeID = self.descriptor.type.id
                tankman = self.itemsFactory.createTankman(tankmen.generateCompactDescr(tankmen.generatePassport(nationID), vehicleTypeID, role, defRoleLevel, skillsByIdxs.get(idx, [])), vehicle=self, vehicleSlotIdx=idx)
                if brotherhoodActive and activateBrotherhood:
                    tankman.setBrotherhoodActivity(True)
                    tankman.rebuildSkills()
            else:
                tankman = None
            crewItems.append((idx, tankman))

        return sortCrew(crewItems, crewRoles)

    def getOutfit(self, season):
        component = self._outfitComponents.get(season)
        vehicleCD = self.descriptor.makeCompactDescr()
        outfit = self.__getOutfit(component=component, vehicleCD=vehicleCD)
        return outfit

    def getOutfitComponent(self, season):
        return self._outfitComponents.get(season)

    def removeOutfitForSeason(self, season):
        self._outfitComponents[season] = customizations.CustomizationOutfit()

    def setCustomOutfit(self, season, outfit):
        for s in SeasonType.REGULAR:
            if s == season:
                self._outfitComponents[s] = outfit.pack()
            if s in self._outfitComponents and self._outfitComponents[s].styleId:
                self._outfitComponents[s] = self.__getEmptyOutfitComponent()

    def setOutfits(self, fromVehicle):
        for season in SeasonType.RANGE:
            self._outfitComponents[season] = fromVehicle.getOutfitComponent(season)

    def hasOutfit(self, season):
        outfit = self.getOutfit(season)
        return outfit is not None

    def hasOutfitWithItems(self, season):
        outfit = self.getOutfit(season)
        if outfit is not None:
            for intCD in outfit.items():
                item = self.__customizationService.getItemByCD(intCD)
                isNationalEmblem = ItemTags.NATIONAL_EMBLEM in item.tags
                if not isNationalEmblem:
                    return True

        return False

    def getBuiltInEquipmentIDs(self):
        return vehicles.getBuiltinEqsForVehicle(self._descriptor.type)

    def getBonusCamo(self):
        for season in SeasonType.SEASONS:
            outfit = self.getOutfit(season)
            if not outfit:
                continue
            intCD = outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getItemCD()
            if intCD:
                return getItemByCompactDescr(intCD)

        return None

    def getAnyOutfitSeason(self):
        activeSeasons = []
        for season in SeasonType.COMMON_SEASONS:
            if self.hasOutfitWithItems(season):
                activeSeasons.append(season)

        return random.choice(activeSeasons) if activeSeasons else SeasonType.SUMMER

    def isRestorePossible(self):
        return self.restoreInfo.isRestorePossible() if not self.isPurchased and not self.isUnrecoverable and self.lobbyContext.getServerSettings().isVehicleRestoreEnabled() and self.restoreInfo is not None else False

    def isRestoreAvailable(self):
        return self.isRestorePossible() and not self.restoreInfo.isInCooldown()

    def hasDisclaimer(self):
        vehicleDisclaimerURLs = GUI_SETTINGS.vehicleDisclaimerURLs
        return vehicleDisclaimerURLs.get(self.getDisclaimerTag(), None) is not None

    def hasLimitedRestore(self):
        return self.isRestorePossible() and self.restoreInfo.isLimited() and self.restoreInfo.getRestoreTimeLeft() > 0

    def hasRestoreCooldown(self):
        return self.isRestorePossible() and self.restoreInfo.isInCooldown()

    def isRecentlyRestored(self):
        return self.isPurchased and self.restoreInfo.isInCooldown() if self.restoreInfo is not None else False

    def __cmp__(self, other):
        if self.isRestorePossible() and not other.isRestorePossible():
            return -1
        if not self.isRestorePossible() and other.isRestorePossible():
            return 1
        return cmp(other.hasLimitedRestore(), self.hasLimitedRestore()) or cmp(self.restoreInfo.getRestoreTimeLeft(), other.restoreInfo.getRestoreTimeLeft()) if self.isRestorePossible() and other.isRestorePossible() else super(Vehicle, self).__cmp__(other)

    def __eq__(self, other):
        return False if other is None else self.descriptor.type.id == other.descriptor.type.id

    def __repr__(self):
        return 'Vehicle<id:%d, intCD:%d, nation:%d, lock:%s>' % (self.invID,
         self.intCD,
         self.nationID,
         self.lock)

    def _mayPurchase(self, price, money):
        return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE) if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False) else super(Vehicle, self)._mayPurchase(price, money)

    def _getShortInfo(self, vehicle=None, expanded=False):
        description = i18n.makeString('#menu:descriptions/' + self.itemTypeName)
        caliber = self.descriptor.gun.shots[0].shell.caliber
        armor = findVehicleArmorMinMax(self.descriptor)
        return description % {'weight': backport.getNiceNumberFormat(float(self.descriptor.physics['weight']) / 1000),
         'hullArmor': backport.getIntegralFormat(armor[1]),
         'caliber': backport.getIntegralFormat(caliber)}

    def _sortByType(self, other):
        return compareByVehTypeName(self.type, other.type)

    @prbDispatcherProperty
    def __prbDispatcher(self):
        return None

    def __calcSellPrice(self, proxy, price):
        if self.isRented:
            return MONEY_UNDEFINED
        defaultDevices, installedDevices, _ = self.descriptor.getDevices()
        for defCompDescr, instCompDescr in izip(defaultDevices, installedDevices):
            if defCompDescr == instCompDescr:
                continue
            modulePrice = FittingItem(defCompDescr, proxy).sellPrices.itemPrice.defPrice
            price = price - modulePrice
            modulePrice = FittingItem(instCompDescr, proxy).sellPrices.itemPrice.defPrice
            price = price + modulePrice

        return price

    def __hasModulesToSelect(self):
        components = []
        for moduleCD in self.descriptor.type.installableComponents:
            moduleType = getTypeOfCompactDescr(moduleCD)
            if moduleType == GUI_ITEM_TYPE.FUEL_TANK:
                continue
            if moduleType in components:
                return True
            components.append(moduleType)

        return False

    def __calcMinMaxRentDuration(self):
        if self.rentPackages:
            maxDays = None
            minDays = None
            for package in self.rentPackages:
                rentID = package.get('rentID', 0)
                rentType, days = parseRentID(rentID)
                if rentType == RentType.TIME_RENT:
                    if maxDays is None or days > maxDays:
                        maxDays = days
                    if minDays is None or days < minDays:
                        minDays = days

            maxDuration = maxDays * _MAX_RENT_MULTIPLIER * time_utils.ONE_DAY if maxDays else 0
            minDuration = minDays * time_utils.ONE_DAY if minDays else 0
            return (maxDuration, minDuration)
        else:
            return (0, 0)

    def __getCustomOutfitComponent(self, proxy, season):
        customOutfitData = proxy.inventory.getOutfitData(self.intCD, season)
        return customizations.parseCompDescr(customOutfitData) if customOutfitData is not None else self.__getEmptyOutfitComponent()

    def __getStyledOutfitComponent(self, proxy, style, styleProgressionLevel, season):
        component = deepcopy(style.outfits.get(season))
        if style.progression:
            if not style.isProgressionRewindEnabled:
                componentProgression = 0
                progressionData = self.itemsCache.items.inventory.getC11nProgressionDataForItem(style.compactDescr)
                if progressionData is not None:
                    vehCD = self.intCD if style.progression.autobound else 0
                    vehProgressionData = progressionData.get(vehCD, None)
                    if vehProgressionData is not None:
                        componentProgression = vehProgressionData.currentLevel
                    component.styleProgressionLevel = componentProgression
            else:
                component.styleProgressionLevel = styleProgressionLevel
        if ItemTags.ADD_NATIONAL_EMBLEM in style.tags:
            emblems = createNationalEmblemComponents(self._descriptor)
            component.decals.extend(emblems)
        diff = proxy.inventory.getOutfitData(self.intCD, season)
        if diff is None:
            return component.copy()
        else:
            diffComponent = customizations.parseCompDescr(diff)
            if component.styleId != diffComponent.styleId:
                _logger.error('Merging outfits of different styles is not allowed. ID1: %s ID2: %s', component.styleId, diffComponent.styleId)
                return component.copy()
            return component.applyDiff(diffComponent)

    def __getEmptyOutfitComponent(self):
        if self.descriptor.type.hasCustomDefaultCamouflage:
            appliedTo = reduce(int.__or__, ApplyArea.HULL_CAMOUFLAGE_REGIONS)
            camoComp = customizations.CamouflageComponent(id=HIDDEN_CAMOUFLAGE_ID, appliedTo=appliedTo)
            return customizations.CustomizationOutfit(camouflages=[camoComp])
        return customizations.CustomizationOutfit()

    @lru_cache(4)
    def __getOutfit(self, component, vehicleCD):
        outfit = self.itemsFactory.createOutfit(component=component, vehicleCD=vehicleCD)
        return outfit


def getTypeUserName(vehType, isElite):
    return i18n.makeString('#menu:header/vehicleType/elite/%s' % vehType) if isElite else i18n.makeString('#menu:header/vehicleType/%s' % vehType)


def getTypeShortUserName(vehType):
    return i18n.makeString('#menu:classes/short/%s' % vehType)


def _getLevelIconName(vehLevel, postfix=''):
    return 'tank_level_%s%d.png' % (postfix, int(vehLevel))


def getLevelBigIconPath(vehLevel):
    return '../maps/icons/levels/%s' % _getLevelIconName(vehLevel, 'big_')


def getLevelSmallIconPath(vehLevel):
    return '../maps/icons/levels/%s' % _getLevelIconName(vehLevel, 'small_')


def getLevelIconPath(vehLevel):
    return '../maps/icons/levels/%s' % _getLevelIconName(vehLevel)


def getIconPath(vehicleName):
    return '../maps/icons/vehicle/%s' % getItemIconName(vehicleName)


def getSizedIconPath(vehicleName, size):
    return '../maps/icons/vehicle/%s/%s' % (size, getItemIconName(vehicleName))


def getNationName(vehicleName):
    return vehicleName.split(':')[0]


def getNationLessName(vehicleName):
    return vehicleName.split(':')[1]


def getNationLessIconName(vehicleName):
    return getNationLessName(vehicleName).replace('-', '_')


def getIconShopPath(vehicleName, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
    name = getNationLessName(vehicleName)
    path = RES_SHOP_EXT.getVehicleIcon(size, name)
    return func_utils.makeFlashPath(path) if path is not None else '../maps/shop/vehicles/%s/empty_tank.png' % size


def getIconShopResource(vehicleName, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
    name = getNationLessName(vehicleName)
    name = name.replace('-', '_')
    size = 'c_%s' % size
    image = R.images.gui.maps.shop.vehicles.dyn(size).dyn(name)
    return image() if image.isValid() else R.images.gui.maps.shop.vehicles.dyn(size).dyn('empty_tank')()


def getIconResource(vehicleName):
    rName = getIconResourceName(vehicleName=vehicleName)
    image = R.images.gui.maps.icons.vehicle.dyn(rName)
    return image() if image.isValid() else None


def getIconResourceName(vehicleName):
    return vehicleName.replace(':', '_').replace('-', '_')


def getContourIconPath(vehicleName):
    return '../maps/icons/vehicle/contour/%s' % getItemIconName(vehicleName)


def getSmallIconPath(vehicleName):
    return '../maps/icons/vehicle/small/%s' % getItemIconName(vehicleName)


def getUniqueIconPath(vehicleName, withLightning=False):
    return '../maps/icons/vehicle/unique/%s' % getItemIconName(vehicleName) if withLightning else '../maps/icons/vehicle/unique/normal_%s' % getItemIconName(vehicleName)


def getTypeSmallIconPath(vehicleType, isElite=False):
    return RES_ICONS.maps_icons_vehicletypes_elite_all_png(vehicleType) if isElite else RES_ICONS.maps_icons_vehicletypes_all_png(vehicleType)


def getTypeBigIconPath(vehicleType, isElite=False):
    return RES_ICONS.getVehicleTypeBigIcon(vehicleType, '_elite' if isElite else '')


def getTypeVPanelIconPath(vehicleType):
    return RES_ICONS.getVehicleTypeVPanelIconPath(vehicleType)


def getTypeBigIconResource(vehicleType, isElite=False):
    return R.images.gui.maps.icons.vehicleTypes.big.dyn((vehicleType + '_elite' if isElite else vehicleType).replace('-', '_'))


def getUserName(vehicleType, textPrefix=False):
    return _getActualName(vehicleType.userString, vehicleType.tags, textPrefix)


def getShortUserName(vehicleType, textPrefix=False):
    return _getActualName(vehicleType.shortUserString, vehicleType.tags, textPrefix)


def _getActualName(name, tags, textPrefix=False):
    if checkForTags(tags, VEHICLE_TAGS.PREMIUM_IGR):
        if textPrefix:
            return i18n.makeString(ITEM_TYPES.MARKER_IGR, vehName=name)
        return makeHtmlString('html_templates:igr/premium-vehicle', 'name', {'vehicle': name})
    return name


def findVehicleArmorMinMax(vd):

    def findComponentArmorMinMax(armor, minMax):
        for value in armor:
            if value != 0:
                if minMax is None:
                    minMax = [value, value]
                else:
                    minMax[0] = min(minMax[0], value)
                    minMax[1] = max(minMax[1], value)

        return minMax

    minMax = None
    minMax = findComponentArmorMinMax(vd.hull.primaryArmor, minMax)
    for turrets in vd.type.turrets:
        for turret in turrets:
            minMax = findComponentArmorMinMax(turret.primaryArmor, minMax)

    return minMax


def sortCrew(crewItems, crewRoles):
    RO = Tankman.TANKMEN_ROLES_ORDER
    return sorted(crewItems, cmp=lambda a, b: RO[crewRoles[a[0]][0]] - RO[crewRoles[b[0]][0]])


def getLobbyDescription(vehicle):
    return text_styles.stats(i18n.makeString('#menu:header/level/%s' % vehicle.level)) + ' ' + text_styles.main(i18n.makeString('#menu:header/level', vTypeName=getTypeUserName(vehicle.type, vehicle.isElite)))


def getOrderByVehicleClass(className=None):
    if className and className in VEHICLE_BATTLE_TYPES_ORDER_INDICES:
        result = VEHICLE_BATTLE_TYPES_ORDER_INDICES[className]
    else:
        result = UNKNOWN_VEHICLE_CLASS_ORDER
    return result


def getVehicleClassTag(tags):
    supplyTags = RTSSupply.SUPPLY_TAG_LIST & tags
    if supplyTags:
        return list(supplyTags).pop()
    else:
        subSet = vehicles.VEHICLE_CLASS_TAGS & tags
        result = None
        if subSet:
            result = list(subSet).pop()
        return result


def getCrewCount(vehs):
    return reduce(lambda acc, value: acc + value, [ len([ tankman for _, tankman in veh.crew if tankman is not None ]) for veh in vehs ])


_VEHICLE_STATE_TO_ICON = {Vehicle.VEHICLE_STATE.BATTLE: RES_ICONS.MAPS_ICONS_VEHICLESTATES_BATTLE,
 Vehicle.VEHICLE_STATE.IN_PREBATTLE: RES_ICONS.MAPS_ICONS_VEHICLESTATES_INPREBATTLE,
 Vehicle.VEHICLE_STATE.DAMAGED: RES_ICONS.MAPS_ICONS_VEHICLESTATES_DAMAGED,
 Vehicle.VEHICLE_STATE.DESTROYED: RES_ICONS.MAPS_ICONS_VEHICLESTATES_DAMAGED,
 Vehicle.VEHICLE_STATE.EXPLODED: RES_ICONS.MAPS_ICONS_VEHICLESTATES_DAMAGED,
 Vehicle.VEHICLE_STATE.CREW_NOT_FULL: RES_ICONS.MAPS_ICONS_VEHICLESTATES_CREWNOTFULL,
 Vehicle.VEHICLE_STATE.RENTAL_IS_OVER: RES_ICONS.MAPS_ICONS_VEHICLESTATES_RENTALISOVER,
 Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT: RES_ICONS.MAPS_ICONS_VEHICLESTATES_UNSUITABLETOUNIT,
 Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE: RES_ICONS.MAPS_ICONS_VEHICLESTATES_UNSUITABLETOUNIT,
 Vehicle.VEHICLE_STATE.GROUP_IS_NOT_READY: RES_ICONS.MAPS_ICONS_VEHICLESTATES_GROUP_IS_NOT_READY,
 Vehicle.VEHICLE_STATE.TOO_HEAVY: backport.image(R.images.gui.maps.icons.vehicleStates.weight())}
_VEHICLE_STATE_TO_ADD_ICON = {Vehicle.VEHICLE_STATE.RENTABLE: RES_ICONS.MAPS_ICONS_VEHICLESTATES_RENT_ICO_BIG,
 Vehicle.VEHICLE_STATE.RENTABLE_AGAIN: RES_ICONS.MAPS_ICONS_VEHICLESTATES_RENTAGAIN_ICO_BIG}

def getVehicleStateIcon(vState):
    if vState in _VEHICLE_STATE_TO_ICON:
        icon = _VEHICLE_STATE_TO_ICON[vState]
    else:
        icon = ''
    return icon


def getVehicleStateAddIcon(vState):
    if vState in _VEHICLE_STATE_TO_ADD_ICON:
        icon = _VEHICLE_STATE_TO_ADD_ICON[vState]
    else:
        icon = ''
    return icon


def getBattlesLeft(vehicle):
    return i18n.makeString('#menu:infinitySymbol') if vehicle.isInfiniteRotationGroup else str(vehicle.rotationBattlesLeft)
