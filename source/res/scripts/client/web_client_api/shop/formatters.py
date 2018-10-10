# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/formatters.py
import re
from collections import namedtuple
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.shared.gui_items import KPI, CREW_SKILL_TO_KPI_NAME_MAP
from helpers import dependency, i18n, time_utils
from items.components.skills_constants import PERKS
from skeletons.gui.shared import IItemsCache
import nations
_WHITESPACE_RE = re.compile('\\s+')
_COLOR_TAG_OPEN = '{colorTagOpen}'
_COLOR_TAG_CLOSE = '{colorTagClose}'

def _strsanitize(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    s = s.replace(u'\r\n', ' ').replace(u'\n', ' ').replace(u'\t', ' ').replace(u'\\', '\\u005c').replace(u'"', '\\u0022').replace(u'`', '\\u0060').encode('utf-8')
    return _WHITESPACE_RE.sub(s, ' ')


def _pathsanitize(s):
    s = s or ''
    if s.startswith('..'):
        s = 'gui' + s[2:]
    return s


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

    def formatKPIValue(kpi):
        if kpi.type is KPI.Type.ONE_OF:
            return _formatKPI(kpi.value)
        return _formatFloat(kpi.value) if kpi.type in {KPI.Type.MUL, KPI.Type.ADD} else kpi.value

    return [ {'name': kpi.name,
     'type': kpi.type,
     'value': formatKPIValue(kpi)} for kpi in kpiList ]


def _formatActionParams(actionInfo):
    return actionInfo.discount.getParams()


def _formatValueToColorTag(value):
    return _COLOR_TAG_OPEN + value + _COLOR_TAG_CLOSE


def _formatTechName(value):
    parts = value.split(':')
    return parts[1] if len(parts) > 1 else value


def _formatImagePaths(item):
    return {'small': _pathsanitize(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL)),
     'medium': _pathsanitize(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_MEDIUM)),
     'large': _pathsanitize(item.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_LARGE))}


def _formatVehicleRestore(item):
    if item.hasLimitedRestore():
        restoreInfo = item.restoreInfo
        restorePrice = item.restorePrice
        currency = restorePrice.getCurrency()
        restoreEndDate = time_utils.timestampToISO(restoreInfo.changedAt + restoreInfo.getRestoreTimeLeft())
        return {'price': {currency: restorePrice.getSignValue(currency)},
         'endDate': restoreEndDate}
    else:
        return None


Field = namedtuple('Field', ('name', 'getter'))
idField = Field('id', lambda i: i.intCD)
nameField = Field('name', lambda i: _strsanitize(i.userName))
nationField = Field('nation', lambda i: i.nationName)
nationNameField = Field('nationName', lambda i: _strsanitize(i.nationUserName))
typeField = Field('type', lambda i: i.type)
typeNameField = Field('typeName', lambda i: _strsanitize(i.typeUserName))
descriptionField = Field('description', lambda i: _strsanitize(i.fullDescription))
shortDescriptionSpecialField = Field('shortDescriptionSpecial', lambda i: _strsanitize(i.shortDescriptionSpecial))
longDescriptionSpecialField = Field('longDescriptionSpecial', lambda i: _strsanitize(i.longDescriptionSpecial))
inventoryCountField = Field('inventoryCount', lambda i: i.inventoryCount)
buyPriceField = Field('buyPrice', lambda i: _formatPrice(i.buyPrices.itemPrice))
sellPriceField = Field('sellPrice', lambda i: _formatPrice(i.sellPrices.itemPrice))
tagsField = Field('tags', lambda i: list(i.tags))
kpiField = Field('kpi', lambda i: _formatKPI(i.kpi))
techNameField = Field('techName', lambda i: _formatTechName(i.name))
imagesField = Field('images', _formatImagePaths)
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
     Field('name', lambda actionInfo: _strsanitize(actionInfo.getTitle())),
     Field('description', lambda actionInfo: _strsanitize(actionInfo.event.getDescription())),
     Field('triggerChainID', lambda actionInfo: actionInfo.getTriggerChainID()),
     Field('type', lambda actionInfo: actionInfo.discount.getName()),
     Field('params', _formatActionParams)]
    return Formatter(fields)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def makeVehicleFormatter(includeInventoryFields=False, itemsCache=None):
    isPremiumField = Field('isPremium', lambda i: i.isPremium)
    levelField = Field('level', lambda i: i.level)
    isUnlockedField = Field('isUnlocked', lambda i: i.isUnlocked)
    shortName = Field('shortName', lambda i: _strsanitize(i.shortUserName))
    restore = Field('restore', _formatVehicleRestore)

    def isTradeInAvailable(vehicle):
        tradeIn = itemsCache.items.shop.tradeIn
        return tradeIn.isEnabled and vehicle.level in tradeIn.allowedVehicleLevels and vehicle.intCD not in tradeIn.forbiddenVehicles

    isTradeInAvailableField = Field('isTradeInAvailable', isTradeInAvailable)
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
     restore]
    if includeInventoryFields:
        shellFormatter = makeShellFormatter(includeCount=True)
        shellsField = Field('shells', lambda i: [ shellFormatter.format(s) for s in i.shells ])
        moduleFormatter = makeModuleFormatter()
        modulesField = Field('modules', lambda i: [ moduleFormatter.format(m) for m in i.modules if m is not None ])
        deviceFormatter = makeDeviceFormatter()
        devicesField = Field('devices', lambda i: [ (deviceFormatter.format(d) if d is not None else None) for d in i.optDevices ])
        equipmentFormatter = makeEquipmentFormatter()
        equipmentField = Field('equipment', lambda i: [ (equipmentFormatter.format(e) if e is not None else None) for e in i.equipment.regularConsumables.getInstalledItems() ])
        crewFormatter = makeCrewFormatter()
        crewField = Field('crew', lambda i: [ (crewFormatter.format(c) if c else None) for _, c in i.crew ])

        def formatReadiness(vehicle):
            isReady = vehicle.isReadyToFight
            data = {'isReady': isReady}
            if not isReady:
                data['reason'] = vehicle.getState()[0]
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def makeDeviceFormatter(compatVehGetter=None, fittedVehGetter=None, itemsCache=None):
    fields = list(_vehicleArtifactsFieldSet)
    fields.append(Field('removePrice', lambda i: _formatPrice(i.getRemovalPrice(itemsCache.items))))
    if compatVehGetter:
        fields.append(Field('compatVehicles', lambda i: compatVehGetter(i.intCD)))
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeEquipmentFormatter(fittedVehGetter=None):
    fields = list(_vehicleArtifactsFieldSet)
    fields.remove(descriptionField)
    fields.extend([Field('cooldown', lambda i: i.descriptor.cooldownSeconds), Field('nations', lambda i: [ nations.NAMES[i] for i in sorted(i.descriptor.compatibleNations()) ]), Field('description', lambda i: _strsanitize(i.descriptor.description))])
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeBattleBoosterFormatter(fittedVehGetter=None):
    fields = list(_vehicleArtifactsFieldSet)
    fields.remove(descriptionField)

    def formatAffectedSkill(i):
        return CREW_SKILL_TO_KPI_NAME_MAP.get(i.getAffectedSkillName(), '') if i.isCrewBooster() else ''

    def formatBoosterType(i):
        if i.isCrewBooster():
            if i.getAffectedSkillName() in PERKS:
                return 'perk'
            return 'skill'

    def formatBoosterTypeName(i):
        if i.isCrewBooster():
            if i.getAffectedSkillName() in PERKS:
                key = ITEM_TYPES.TANKMAN_SKILLS_TYPE_PERK_SHORT
            else:
                key = ITEM_TYPES.TANKMAN_SKILLS_TYPE_SKILL_SHORT
        else:
            key = ITEM_TYPES.OPTIONALDEVICE_NAME
        return _strsanitize(i18n.makeString(key))

    def formatBoosterDescription(i):
        return _strsanitize(i.getCrewBoosterDescription(False)) if i.isCrewBooster() else _strsanitize(i.getOptDeviceBoosterDescription(vehicle=None, valueFormatter=_formatValueToColorTag))

    fields.extend([Field('affectedSkill', formatAffectedSkill),
     Field('affectedSkillName', lambda i: _strsanitize(i.getAffectedSkillUserName())),
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
     Field('description', lambda booster: _strsanitize(booster.getBonusDescription(valueFormatter=_formatValueToColorTag))),
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
     Field('name', lambda i: _strsanitize(i.longUserName)),
     Field('type', lambda i: _strsanitize(i.descriptor.itemTypeName)),
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
    fields = [Field('fullName', lambda i: i.fullUserName), Field('role', lambda i: i.role), Field('roleLevel', lambda i: i.realRoleLevel[0])]
    return Formatter(fields)


def makePremiumPackFormatter():
    fields = [nameField,
     shortDescriptionSpecialField,
     longDescriptionSpecialField,
     Field('buyPrice', lambda pack: _formatPrice(pack.buyPrice)),
     Field('duration', lambda pack: pack.duration),
     Field('id', lambda pack: pack.id)]
    return Formatter(fields)
