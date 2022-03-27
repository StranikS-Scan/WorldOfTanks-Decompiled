# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/model_helpers.py
import logging
from RTSShared import RTSSupply
from constants import ARENA_BONUS_TYPE
from gui.impl.gen import R
from gui.impl.gen.view_models.common.vehicle_base_model import VehicleBaseModel, VehicleClass, VehicleNation
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_view_model import GameMode
from gui.impl.gen.view_models.views.lobby.rts.carousel_supply_slot_model import CarouselSupplySlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_vehicle_slot_model import CarouselVehicleSlotModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_view_model import RosterVehicleViewModel, MannerEnum
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_supply_view_model import SupplyType, RosterSupplyViewModel
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import CurrencyTypeEnum
from gui.shared.gui_items.Vehicle import getIconResource, Vehicle, getVehicleClassTag
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
SUPPLY_ID_TO_ENUM = {RTSSupply.AT_GUN: SupplyType.AT_GUN,
 RTSSupply.PILLBOX: SupplyType.PILLBOX,
 RTSSupply.BUNKER: SupplyType.BUNKER,
 RTSSupply.MORTAR: SupplyType.MORTAR,
 RTSSupply.BARRICADES: SupplyType.BARRICADES,
 RTSSupply.WATCH_TOWER: SupplyType.WATCHTOWER,
 RTSSupply.FLAMER: SupplyType.FLAMETHROWER}
SUPPLY_ENUM_TO_ID = {SupplyType.AT_GUN: RTSSupply.AT_GUN,
 SupplyType.PILLBOX: RTSSupply.PILLBOX,
 SupplyType.BUNKER: RTSSupply.BUNKER,
 SupplyType.MORTAR: RTSSupply.MORTAR,
 SupplyType.BARRICADES: RTSSupply.BARRICADES,
 SupplyType.WATCHTOWER: RTSSupply.WATCH_TOWER,
 SupplyType.FLAMETHROWER: RTSSupply.FLAMER}
VEHICLE_TO_ENUM = {'lightTank': VehicleClass.LIGHTTANK,
 'mediumTank': VehicleClass.MEDIUMTANK,
 'heavyTank': VehicleClass.HEAVYTANK,
 'AT-SPG': VehicleClass.AT_SPG,
 'SPG': VehicleClass.SPG}
ARENA_BONUS_TYPE_TO_ENUM = {ARENA_BONUS_TYPE.RTS: GameMode.ONEXSEVEN,
 ARENA_BONUS_TYPE.RTS_1x1: GameMode.ONEXONE}
ARENA_BONUS_TYPE_TO_CURRENCY_TYPE_ENUM = {ARENA_BONUS_TYPE.RTS: CurrencyTypeEnum.CURRENCY1X7,
 ARENA_BONUS_TYPE.RTS_1x1: CurrencyTypeEnum.CURRENCY1X1}
CURRENCY_TYPE_TO_ARENA_TYPE = {v:k for k, v in ARENA_BONUS_TYPE_TO_CURRENCY_TYPE_ENUM.iteritems()}

def getGameMode(bonusType):
    return ARENA_BONUS_TYPE_TO_ENUM.get(bonusType, None)


def getCurrencyType(bonusType):
    return ARENA_BONUS_TYPE_TO_CURRENCY_TYPE_ENUM.get(bonusType, None)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def buildVehicleSlotModel(intCD, slotModel, mannerGetter=None, itemsCache=None):
    if intCD <= 0:
        return
    vehicle = itemsCache.items.getItemByCD(intCD)
    vehicleModel = slotModel.vehicle
    packRosterVehicleModel(vehicle, vehicleModel, packVehicleBaseModel, mannerGetter)
    slotModel.setIsEmpty(False)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def buildSupplySlotModel(intCD, slotModel, supplyAmountSettings, itemsCache=None):
    if intCD <= 0:
        return
    supply = itemsCache.items.getItemByCD(intCD)
    if not RTSSupply.isSupply(supply.descriptor.type):
        _logger.error('Could not identify item as a valid rts supply, using vehicles tags: %(tags)s, vehicleName: %(name)s', {'tags': supply.tags,
         'name': supply.name})
        return
    supplyModel = slotModel.supply
    fillRosterSupplyModel(supply, supplyModel, supplyAmountSettings)
    slotModel.setIsEmpty(False)


def fillRosterSupplyModel(supply, model, supplyAmountSettings):
    tag = getVehicleClassTag(supply.tags)
    rtsSupplyType = RTSSupply.TAG_TO_SUPPLY[tag]
    model.setIntCD(supply.intCD)
    model.setType(SUPPLY_ID_TO_ENUM[rtsSupplyType])
    if tag in supplyAmountSettings:
        model.setDefenseCount(supplyAmountSettings[tag])


def packVehicleBaseModel(vehicle, model, imageResGetter=getIconResource):
    model.setIntCD(vehicle.intCD)
    model.setNation(VehicleNation(vehicle.nationName))
    model.setClass(VEHICLE_TO_ENUM[vehicle.type])
    model.setTier(vehicle.level)
    model.setShortName(vehicle.shortUserName)
    model.setIsElite(vehicle.isElite)
    model.setIsPremium(vehicle.isPremium)
    model.setImage(imageResGetter(vehicle.name))


def packRosterVehicleModel(vehicle, model, baseVehiclePacker=packVehicleBaseModel, mannerGetter=None):
    baseVehiclePacker(vehicle, model)
    if mannerGetter is not None:
        manner = mannerGetter(vehicle.intCD)
        model.setManner(MannerEnum(manner))
    return


def swapSupplyModel(first, second):
    intCD = first.getIntCD()
    sType = first.getType()
    count = first.getDefenseCount()
    first.setIntCD(second.getIntCD())
    first.setType(second.getType())
    first.setDefenseCount(second.getDefenseCount())
    second.setIntCD(intCD)
    second.setType(sType)
    second.setDefenseCount(count)


def swapRosterVehicleViewModel(first, second):
    intCD = first.getIntCD()
    nation = first.getNation()
    vehClass = first.getClass()
    tier = first.getTier()
    shortName = first.getShortName()
    isElite = first.getIsElite()
    isPremium = first.getIsPremium()
    image = first.getImage()
    manner = first.getManner()
    first.setIntCD(second.getIntCD())
    first.setNation(second.getNation())
    first.setClass(second.getClass())
    first.setTier(second.getTier())
    first.setShortName(second.getShortName())
    first.setIsElite(second.getIsElite())
    first.setIsPremium(second.getIsPremium())
    first.setImage(second.getImage())
    first.setManner(second.getManner())
    second.setIntCD(intCD)
    second.setNation(nation)
    second.setClass(vehClass)
    second.setTier(tier)
    second.setShortName(shortName)
    second.setIsElite(isElite)
    second.setIsPremium(isPremium)
    second.setImage(image)
    second.setManner(manner)
