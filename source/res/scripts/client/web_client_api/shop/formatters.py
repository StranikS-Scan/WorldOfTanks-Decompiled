# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/formatters.py
from collections import namedtuple
import re
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_helpers import isVehicleTopConfiguration
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.shared.gui_items import KPI, CREW_SKILL_TO_KPI_NAME_MAP
from helpers import dependency, i18n
from items.components.skills_constants import PERKS
from skeletons.gui.shared import IItemsCache
import nations
_WHITESPACE_RE = re.compile('\\s+')

def _strsanitize(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    s = s.replace(u'\r\n', ' ').replace(u'\n', ' ').replace(u'\t', ' ').replace(u'"', '\\"').replace(u'`', '\\`')
    return _WHITESPACE_RE.sub(s, u' ')


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
        if kpi.type is KPI.Type.OR:
            return _formatKPI(kpi.value)
        return _formatFloat(kpi.value) if kpi.type in {KPI.Type.FACTOR, KPI.Type.VALUE} else kpi.value

    return [ {'name': kpi.name,
     'type': kpi.type,
     'value': formatKPIValue(kpi)} for kpi in kpiList if kpi.value != 1.0 ]


Field = namedtuple('Field', ('name', 'getter'))
idField = Field('id', lambda i: i.intCD)
nameField = Field('name', lambda i: _strsanitize(i.userName))
nationField = Field('nation', lambda i: i.nationName)
nationNameField = Field('nationName', lambda i: i.nationUserName)
typeField = Field('type', lambda i: i.type)
typeNameField = Field('typeName', lambda i: i.typeUserName)
descriptionField = Field('description', lambda i: _strsanitize(i.fullDescription))
inventoryCountField = Field('inventoryCount', lambda i: i.inventoryCount)
buyPriceField = Field('buyPrice', lambda i: _formatPrice(i.buyPrices.itemPrice))
sellPriceField = Field('sellPrice', lambda i: _formatPrice(i.sellPrices.itemPrice))
tagsField = Field('tags', lambda i: list(i.tags))
kpiField = Field('kpi', lambda i: _formatKPI(i.kpi))
_vehicleComponentsFieldSet = (idField,
 nameField,
 buyPriceField,
 sellPriceField,
 descriptionField,
 inventoryCountField)
_vehicleArtifactsFieldSet = _vehicleComponentsFieldSet + (tagsField, kpiField)

class Formatter(object):

    def __init__(self, fields):
        self.__fields = fields

    def format(self, item):
        data = {}
        for field in self.__fields:
            data[field.name] = field.getter(item)

        return data


def makeVehicleFormatter(includeInventoryFields=False):
    isPremiumField = Field('isPremium', lambda i: i.isPremium)
    levelField = Field('level', lambda i: i.level)
    techNameField = Field('techName', lambda i: i.name.split(':')[1])
    isUnlockedField = Field('isUnlocked', lambda i: i.isUnlocked)
    fields = [idField,
     nameField,
     techNameField,
     nationField,
     nationNameField,
     typeField,
     typeNameField,
     levelField,
     descriptionField,
     isPremiumField,
     buyPriceField,
     sellPriceField,
     isUnlockedField]
    if includeInventoryFields:
        isTopConfigurationField = Field('isTopConfiguration', isVehicleTopConfiguration)
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
        fields.extend([isTopConfigurationField,
         shellsField,
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
    fields.extend([Field('cooldown', lambda i: i.descriptor.cooldownSeconds), Field('nations', lambda i: [ nations.NAMES[i] for i in sorted(i.descriptor.compatibleNations()) ])])
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
        return i18n.makeString(key)

    fields.extend([Field('affectedSkill', formatAffectedSkill),
     Field('affectedSkillName', lambda i: i.getAffectedSkillUserName()),
     Field('boosterType', formatBoosterType),
     Field('boosterTypeName', formatBoosterTypeName),
     Field('description', lambda i: i.getCrewBoosterDescription(False) if i.isCrewBooster() else _strsanitize(i.fullDescription))])
    if fittedVehGetter:
        fields.append(Field('fittedVehicles', lambda i: fittedVehGetter(i.intCD)))
    return Formatter(fields)


def makeBoosterFormatter():
    fields = [Field('id', lambda booster: booster.boosterID),
     Field('inventoryCount', lambda booster: booster.count),
     Field('kpi', lambda booster: _formatKPI(booster.kpi)),
     Field('description', lambda booster: booster.description),
     Field('duration', lambda booster: booster.effectTime),
     Field('type', lambda booster: booster.boosterGuiType),
     nameField,
     buyPriceField]
    return Formatter(fields)


def makeModuleFormatter():
    fields = [idField,
     Field('name', lambda i: _strsanitize(i.longUserName)),
     Field('type', lambda i: i.descriptor.itemTypeName),
     buyPriceField,
     sellPriceField,
     inventoryCountField]
    return Formatter(fields)


def makeShellFormatter(includeCount=False):
    fields = [idField,
     nameField,
     inventoryCountField,
     sellPriceField,
     buyPriceField,
     typeField]
    if includeCount:
        fields.append(Field('count', lambda i: i.count))
    return Formatter(fields)


def makeCrewFormatter():
    fields = [Field('fullName', lambda i: i.fullUserName), Field('role', lambda i: i.role), Field('roleLevel', lambda i: i.realRoleLevel[0])]
    return Formatter(fields)


def makePremiumPackFormatter():
    fields = [nameField,
     Field('buyPrice', lambda pack: _formatPrice(pack.buyPrice)),
     Field('duration', lambda pack: pack.duration),
     Field('id', lambda pack: pack.duration)]
    return Formatter(fields)
