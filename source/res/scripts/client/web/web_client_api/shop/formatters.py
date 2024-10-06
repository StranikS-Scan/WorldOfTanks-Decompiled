# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/formatters.py
import re
from collections import namedtuple
import typing
import nations
from constants import RentType
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.game_control.veh_comparison_basket import isValidVehicleForComparing
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import CREW_SKILL_TO_KPI_NAME_MAP, GUI_ITEM_TYPE, KPI
from gui.shared.gui_items.Vehicle import Vehicle, getShortUserName, getUserName
from gui.shop import SHOP_RENT_SEASON_TYPE_MAP, SHOP_RENT_TYPE_MAP
from helpers import dependency, i18n, time_utils
from helpers.func_utils import replaceImgPrefix
from items.components.supply_slot_categories import SlotCategories
from items import vehicles
from nation_change.nation_change_helpers import getGroupByVehTypeCompactDescr, iterVehTypeCDsInNationGroup
from rent_common import SeasonRentDuration
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Union, Any, Optional
    from gui.shared.gui_items.Tankman import Tankman
    from web.web_client_api.shop.crew import _ShopTankman, _ShopRecruit
    AnyTankman = Union[Tankman, _ShopTankman, _ShopRecruit]
COLOR_TAG_OPEN = '{colorTagOpen}'
COLOR_TAG_CLOSE = '{colorTagClose}'
_WHITESPACE_RE = re.compile('\\s+')
_RENT_DURATION_MAP = {SeasonRentDuration.ENTIRE_SEASON: SHOP_RENT_TYPE_MAP[RentType.SEASON_RENT],
 SeasonRentDuration.SEASON_CYCLE: SHOP_RENT_TYPE_MAP[RentType.SEASON_CYCLE_RENT]}

def formatValueToColorTag(value):
    return COLOR_TAG_OPEN + value + COLOR_TAG_CLOSE


def _formatPrice(itemPrice):
    if itemPrice.isActionPrice():
        price = itemPrice.defPrice.toDict()
        price['discount'] = itemPrice.price.toDict()
        return price
    else:
        return itemPrice.price.toDict() or None


def _formatFloat(val):
    return round(val, 4)


def _formatKPI(kpiList):

    def _formatKPIValue(kpi, value):
        if kpi.type == KPI.Type.AGGREGATE_MUL:
            minValue, maxValue = value
            return (_formatFloat(minValue), _formatFloat(maxValue))
        return _formatFloat(value) if kpi.type in (KPI.Type.MUL, KPI.Type.ADD) else value

    return [ {'name': kpi.name,
     'type': kpi.type,
     'specValue': _formatKPIValue(kpi, kpi.specValue) if kpi.specValue else None,
     'vehicleTypes': kpi.vehicleTypes,
     'value': _formatKPIValue(kpi, kpi.value) if kpi.type != KPI.Type.ONE_OF else _formatKPI(kpi.value),
     'descr': backport.text(kpi.getDescriptionR()) if kpi.getDescriptionR() > 0 else ''} for kpi in kpiList ]


def _formatActionParams(actionInfo):
    return actionInfo.discount.getParams()


def _formatTechName(value):
    parts = value.split(':')
    return parts[1] if len(parts) > 1 else value


def _formatImagePaths(item):
    return {'small': replaceImgPrefix(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL)),
     'medium': replaceImgPrefix(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_MEDIUM)),
     'large': replaceImgPrefix(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_LARGE))}


def _formatVehicleRestore(item):
    if item.isRestorePossible():
        restoreInfo = item.restoreInfo
        restorePrice = item.restorePrice
        currency = restorePrice.getCurrency()
        if item.hasLimitedRestore():
            restoreEndDate = time_utils.timestampToISO(restoreInfo.changedAt + restoreInfo.getRestoreTimeLeft())
        else:
            restoreEndDate = None
        return {'price': {currency: restorePrice.getSignValue(currency)},
         'endDate': restoreEndDate}
    else:
        return


def _formatVehicleOwnership(item):
    if item.isInInventory and item.activeInNationGroup:
        result = {}
        if not item.isRented:
            result['type'] = 'permanent'
        elif item.rentalIsOver:
            result['type'] = 'rentalsOver'
        else:
            result['type'] = 'rented'
            info = item.rentInfo
            event = info.getActiveSeasonRent()

            def _formatInfinite(val):
                return val if val < float('inf') else -1

            if event:
                rentType = 'event'
            elif item.isTelecomRent:
                rentType = 'telecom'
            else:
                rentType = None
            result['info'] = {'event': {'type': SHOP_RENT_SEASON_TYPE_MAP.get(event.seasonType, 'unknown'),
                       'id': event.seasonID,
                       'duration': _RENT_DURATION_MAP.get(event.duration, 'undefined'),
                       'expire': event.expiryTime} if event else None,
             'rentType': rentType,
             'time': _formatInfinite(info.getTimeLeft()),
             'battles': _formatInfinite(info.battlesLeft),
             'wins': _formatInfinite(info.winsLeft)}
        return result
    else:
        return


def _formatVehicleNationChange(vehicle):
    if vehicle.hasNationGroup:
        result = {}
        result['isAvailable'] = vehicle.isNationChangeAvailable
        result['otherNationsVehCDs'] = list(iterVehTypeCDsInNationGroup(vehicle.intCD))
        nationGroupVehicles = getGroupByVehTypeCompactDescr(vehicle.intCD)
        nationID, _ = vehicles.g_list.getIDsByName(nationGroupVehicles[0])
        result['mainNation'] = nations.NAMES[nationID]
        return result
    else:
        return None


def _formatVehicleComparingAvailability(item):
    return not isValidVehicleForComparing(item)


def _formatUserName(item):
    return getUserName(item.descriptor.type, textPrefix=True) if isinstance(item, Vehicle) else item.userName


def _formatShortUserName(item):
    return getShortUserName(item.descriptor.type, textPrefix=True) if isinstance(item, Vehicle) else item.shortUserName


def _formatOptDeviceCategories(item):
    return list(item.descriptor.categories) if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else []


def _formatOptDeviceEffects(item):
    if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        itemR = R.strings.artefacts.dyn(item.descriptor.groupName)
        effectR = itemR.dyn('effect') if itemR else None
        effectsList = [ backport.text(effect()) for effect in effectR.values() ] if effectR else []
        return effectsList
    else:
        return []


def _formatTags(item):
    if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        tags = set(item.tags)
        tags.difference_update(SlotCategories.ALL)
        tags.add(item.descriptor.tierlessName)
        tags.update(item.descriptor.categories)
        return list(tags)
    return list(item.tags)


Field = namedtuple('Field', ('name', 'getter'))
idField = Field('id', lambda i: i.intCD)
nameField = Field('name', _formatUserName)
nationField = Field('nation', lambda i: i.nationName)
nationNameField = Field('nationName', lambda i: i.nationUserName)
typeField = Field('type', lambda i: i.type)
typeNameField = Field('typeName', lambda i: i.typeUserName)
descriptionField = Field('description', lambda i: i.fullDescription)
shortDescriptionSpecialField = Field('shortDescriptionSpecial', lambda i: i.shortDescriptionSpecial)
longDescriptionSpecialField = Field('longDescriptionSpecial', lambda i: i.longDescriptionSpecial)
inventoryCountField = Field('inventoryCount', lambda i: i.inventoryCount)
buyPriceField = Field('buyPrice', lambda i: _formatPrice(i.buyPrices.itemPrice))
sellPriceField = Field('sellPrice', lambda i: _formatPrice(i.sellPrices.itemPrice))
tagsField = Field('tags', _formatTags)
kpiField = Field('kpi', lambda i: _formatKPI(i.getKpi()))
techNameField = Field('techName', lambda i: _formatTechName(i.name))
imagesField = Field('images', _formatImagePaths)
optDeviceCategoriesField = Field('categories', _formatOptDeviceCategories)
optDeviceEffectField = Field('effects', _formatOptDeviceEffects)
optDeviceGroupName = Field('groupName', lambda i: backport.text(R.strings.artefacts.dyn(i.descriptor.tierlessName).name()))
_vehicleComponentsFieldSet = (idField,
 nameField,
 techNameField,
 buyPriceField,
 sellPriceField,
 descriptionField,
 inventoryCountField,
 shortDescriptionSpecialField,
 longDescriptionSpecialField,
 imagesField)
_vehicleArtifactsFieldSet = _vehicleComponentsFieldSet + (tagsField, kpiField)
_vehicleOptDeviceFieldSet = _vehicleArtifactsFieldSet + (optDeviceCategoriesField, optDeviceEffectField, optDeviceGroupName)

class Formatter(object):
    __slots__ = ('__fields',)

    def __init__(self, fields):
        self.__fields = fields

    def format(self, item, allowedFields=None):
        return {field.name:field.getter(item) for field in self.__fields} if allowedFields is None else {field.name:field.getter(item) for field in self.__fields if field.name in allowedFields}


def makeActionFormatter():
    fields = [Field('id', lambda actionInfo: actionInfo.getID()),
     Field('startDate', lambda actionInfo: time_utils.timestampToISO(actionInfo.getExactStartTime())),
     Field('endDate', lambda actionInfo: time_utils.timestampToISO(actionInfo.getExactFinishTime())),
     Field('name', lambda actionInfo: actionInfo.getTitle()),
     Field('description', lambda actionInfo: actionInfo.event.getDescription()),
     Field('triggerChainID', lambda actionInfo: actionInfo.getTriggerChainID()),
     Field('type', lambda actionInfo: actionInfo.discount.getName()),
     Field('params', _formatActionParams)]
    return Formatter(fields)


def makeVehicleFormatter(includeInventoryFields=False):
    isPremiumField = Field('isPremium', lambda i: i.isPremium)
    levelField = Field('level', lambda i: i.level)
    isUnlockedField = Field('isUnlocked', lambda i: i.isUnlocked)
    shortName = Field('shortName', _formatShortUserName)
    restore = Field('restore', _formatVehicleRestore)
    isTradeInAvailableField = Field('isTradeInAvailable', lambda i: i.isTradeInAvailable)
    isTradeOffAvailableField = Field('isTradeOffAvailable', lambda i: i.isTradeOffAvailable)
    tradeOffPriceField = Field('tradeOffPrice', lambda i: i.tradeOffPrice.toDict() or None)
    inHangarField = Field('inHangar', lambda i: i.isInInventory)
    ownershipField = Field('ownership', _formatVehicleOwnership)
    nationChangeField = Field('nationChange', _formatVehicleNationChange)
    clanLockField = Field('clanLock', lambda i: i.clanLock)
    isCollectibleField = Field('isCollectible', lambda i: i.isCollectible)
    isNotComparingAvailableField = Field('isNotComparingAvailable', _formatVehicleComparingAvailability)
    isOnlyForBattleRoyaleBattles = Field('isOnlyForBattleRoyaleBattles', lambda i: i.isOnlyForBattleRoyaleBattles)
    fields = [idField,
     nameField,
     shortName,
     techNameField,
     nationField,
     nationNameField,
     typeField,
     typeNameField,
     levelField,
     descriptionField,
     shortDescriptionSpecialField,
     longDescriptionSpecialField,
     isPremiumField,
     buyPriceField,
     sellPriceField,
     isUnlockedField,
     imagesField,
     isTradeInAvailableField,
     isTradeOffAvailableField,
     tradeOffPriceField,
     restore,
     inHangarField,
     ownershipField,
     nationChangeField,
     clanLockField,
     isCollectibleField,
     isNotComparingAvailableField,
     isOnlyForBattleRoyaleBattles]
    if includeInventoryFields:
        shellFormatter = makeShellFormatter(includeCount=True)
        shellsField = Field('shells', lambda i: [ shellFormatter.format(s) for s in i.shells.installed.getItems() ])
        moduleFormatter = makeModuleFormatter()
        modulesField = Field('modules', lambda i: [ moduleFormatter.format(m) for m in i.modules if m is not None ])
        deviceFormatter = makeDeviceFormatter()
        devicesField = Field('devices', lambda i: [ (deviceFormatter.format(d) if d is not None else None) for d in i.optDevices.installed ])
        equipmentFormatter = makeEquipmentFormatter()
        equipmentField = Field('equipment', lambda i: [ (equipmentFormatter.format(e) if e is not None else None) for e in i.consumables.installed.getItems() ])
        crewFormatter = makeCrewFormatter()
        crewField = Field('crew', lambda i: [ (crewFormatter.format(c) if c else None) for _, c in i.crew ])

        def formatReadiness(vehicle):
            isReady = vehicle.isReadyToFight
            data = {'isReady': isReady}
            if not isReady:
                reason, stateLevel = vehicle.getState()
                data['reason'] = reason
                data['stateLevel'] = stateLevel
            return data

        readinessField = Field('readiness', formatReadiness)
        isFavoriteField = Field('isFavorite', lambda i: i.isFavorite)
        fields.extend([shellsField,
         modulesField,
         devicesField,
         equipmentField,
         crewField,
         readinessField,
         isFavoriteField])
    return Formatter(fields)


def makeShopTankmanFormatter():
    return Formatter((Field('groupName', lambda i: i.groupName),
     Field('location', lambda i: i.location.value),
     Field('role', _formatTankmanRole),
     Field('rank', _formatTankmanRank),
     Field('vehicle', _formatVehicleInfo),
     Field('name', _formatTankmanNames),
     Field('isPremium', lambda i: i.isPremium),
     Field('gender', lambda i: i.gender.value),
     Field('nation', _formatTankmanNationInfo),
     Field('icons', _formatTankmanIcons)))


def _formatTankmanRole(crewItem):
    return {'id': crewItem.roleID,
     'name': crewItem.roleName,
     'userName': crewItem.roleUserName}


def _formatTankmanRank(crewItem):
    return {'id': crewItem.rankID,
     'userName': crewItem.rankUserName}


def _formatVehicleInfo(crewItem):
    return {vType:{'id': descr.type.compactDescr,
     'type': first((t for t in vehicles.VEHICLE_CLASS_TAGS if t in descr.type.tags)),
     'name': descr.type.userString,
     'nation': nations.MAP[descr.type.id[0]]} for vType, descr in (('current', crewItem.vehicleDescr), ('native', crewItem.vehicleNativeDescr)) if descr is not None}


def _formatTankmanNames(crewItem):
    return {'first': crewItem.firstUserName,
     'last': crewItem.lastUserName,
     'full': crewItem.fullUserName}


def _formatTankmanNationInfo(crewItem):
    return {'id': crewItem.nationID,
     'name': crewItem.nationName,
     'userName': crewItem.nationUserName}


def _formatTankmanIcons(crewItem):
    return {'person': crewItem.icon,
     'role': crewItem.iconRole,
     'rank': crewItem.iconRank}


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def makeDeviceFormatter(compatVehGetter=None, fittedVehGetter=None, itemsCache=None):
    fields = list(_vehicleOptDeviceFieldSet)
    fields.append(Field('removePrice', lambda i: _formatPrice(i.getRemovalPrice(itemsCache.items))))
    if compatVehGetter:
        fields.append(Field('compatVehicles', lambda i: compatVehGetter(i.intCD)))
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeEquipmentFormatter(fittedVehGetter=None):
    fields = list(_vehicleArtifactsFieldSet)
    fields.remove(descriptionField)
    fields.extend([Field('cooldown', lambda i: i.descriptor.cooldownSeconds), Field('nations', lambda i: [ nations.NAMES[i] for i in sorted(i.descriptor.compatibleNations()) ]), Field('description', lambda i: i.descriptor.description)])
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeBattleBoosterFormatter(fittedVehGetter=None):
    fields = list(_vehicleArtifactsFieldSet)
    fields.remove(descriptionField)

    def formatAffectedSkill(i):
        return CREW_SKILL_TO_KPI_NAME_MAP.get(i.getAffectedSkillName(), '') if i.isCrewBooster() else ''

    def formatBoosterType(i):
        return 'skill' if i.isCrewBooster() else 'device'

    def formatBoosterTypeName(i):
        if i.isCrewBooster():
            key = ITEM_TYPES.TANKMAN_SKILLS_TYPE_SKILL_SHORT
        else:
            key = ITEM_TYPES.OPTIONALDEVICE_NAME
        return i18n.makeString(key)

    def formatBoosterDescription(i):
        return i.getCrewBoosterDescription(False) if i.isCrewBooster() else i.getOptDeviceBoosterDescription(vehicle=None, valueFormatter=formatValueToColorTag)

    fields.extend([Field('affectedSkill', formatAffectedSkill),
     Field('affectedSkillName', lambda i: i.getAffectedSkillUserName()),
     Field('boosterType', formatBoosterType),
     Field('boosterTypeName', formatBoosterTypeName),
     Field('description', formatBoosterDescription)])
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeBoosterFormatter():
    fields = [Field('id', lambda booster: booster.boosterID),
     Field('inventoryCount', lambda booster: booster.count),
     Field('kpi', lambda booster: _formatKPI(booster.kpi)),
     Field('description', lambda booster: booster.getBonusDescription(valueFormatter=formatValueToColorTag)),
     shortDescriptionSpecialField,
     longDescriptionSpecialField,
     Field('duration', lambda booster: booster.effectTime),
     Field('type', lambda booster: booster.boosterGuiType),
     nameField,
     buyPriceField,
     imagesField]
    return Formatter(fields)


def makeModuleFormatter():
    fields = [idField,
     Field('name', lambda i: i.longUserName),
     Field('type', lambda i: i.descriptor.itemTypeName),
     techNameField,
     nationField,
     buyPriceField,
     sellPriceField,
     inventoryCountField,
     imagesField]
    return Formatter(fields)


def makeShellFormatter(includeCount=False):
    fields = [idField,
     nameField,
     inventoryCountField,
     sellPriceField,
     buyPriceField,
     typeField,
     nationField,
     techNameField,
     imagesField]
    if includeCount:
        fields.append(Field('count', lambda i: i.count))
    return Formatter(fields)


def makeCrewFormatter():
    fields = [Field('fullName', lambda i: i.fullUserName), Field('role', lambda i: i.role), Field('roleLevel', lambda i: i.realRoleLevel.lvl)]
    return Formatter(fields)


def makePremiumPackFormatter():
    fields = [nameField,
     shortDescriptionSpecialField,
     longDescriptionSpecialField,
     Field('buyPrice', lambda pack: _formatPrice(pack.buyPrice)),
     Field('duration', lambda pack: pack.duration),
     Field('id', lambda pack: pack.id)]
    return Formatter(fields)


def makeCustomizationFormatter():
    fields = [Field('id', lambda i: i.id),
     Field('type', lambda i: i.itemTypeName),
     Field('priceGroup', lambda i: i.priceGroup),
     Field('installedCount', lambda i: i.installedCount()),
     buyPriceField,
     sellPriceField]
    return Formatter(fields)


def makeInventoryEnhancementsFormatter():
    fields = [Field('id', lambda i: i.id), Field('count', lambda i: i.count)]
    return Formatter(fields)


def makeInstalledEnhancementsFormatter():
    fields = [Field('vehicle_int_cd', lambda i: i.vehIntCD), Field('enhancements', lambda i: i.enhancements)]
    return Formatter(fields)


def makeCrewBooksFormatter():
    fields = [idField,
     Field('images', lambda item: {'small': replaceImgPrefix(item.getShopIcon(size='small')),
      'medium': replaceImgPrefix(item.getShopIcon(size='big')),
      'large': replaceImgPrefix(item.getShopIcon(size='large'))}),
     Field('type', lambda book: book.getBookType()),
     Field('nation', lambda book: book.getNation())]
    return Formatter(fields)
