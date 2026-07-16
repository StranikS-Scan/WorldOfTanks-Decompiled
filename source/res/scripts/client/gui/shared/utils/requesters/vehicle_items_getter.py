# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/vehicle_items_getter.py
from __future__ import absolute_import
from future.utils import itervalues, viewkeys, viewvalues
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params
from items import vehicles, tankmen, EQUIPMENT_TYPES, ItemsPrices
from items.components.c11n_constants import DecalType
from soft_exception import SoftException
import nations

def _getVehicles(nationID):
    return itervalues(vehicles.g_list.getList(nationID))


def _getChassis(nationID):
    return itervalues(vehicles.g_cache.chassis(nationID))


def _getEngines(nationID):
    return itervalues(vehicles.g_cache.engines(nationID))


def _getRadios(nationID):
    return itervalues(vehicles.g_cache.radios(nationID))


def _getTurrets(nationID):
    return itervalues(vehicles.g_cache.turrets(nationID))


def _getGuns(nationID):
    return itervalues(vehicles.g_cache.guns(nationID))


def _getShells(nationID):
    return itervalues(vehicles.g_cache.shells(nationID))


def _filterByNationAndEqType(items, getParameters, nationID, eqType=None):
    ignoreNation = nationID == nations.NONE_INDEX or nationID is None
    ignoreEquipmentType = eqType is None
    if ignoreNation and ignoreEquipmentType:
        return
    else:
        for value in itervalues(items):
            itemParams = getParameters(value)
            if ignoreNation:
                conditionNation = True
            else:
                conditionNation = nationID in itemParams.nations
            if ignoreEquipmentType:
                conditionType = True
            else:
                conditionType = eqType == itemParams.equipmentType
            if conditionNation and conditionType:
                yield value

        return


def _getEquipments(nationID):
    return _filterByNationAndEqType(vehicles.g_cache.equipments(), params.EquipmentParams, nationID, EQUIPMENT_TYPES.regular)


def _getBattleBoosters(nationID):
    return _filterByNationAndEqType(vehicles.g_cache.equipments(), params.EquipmentParams, nationID, EQUIPMENT_TYPES.battleBoosters)


def _getBattleAbilities(nationID):
    return _filterByNationAndEqType(vehicles.g_cache.equipments(), params.EquipmentParams, nationID, EQUIPMENT_TYPES.battleAbilities)


def _getOptionalDevices(nationID):
    return _filterByNationAndEqType(vehicles.g_cache.optionalDevices(), params.OptionalDeviceParams, nationID)


def _getPaints(_):
    return itervalues(vehicles.g_cache.customization20().paints)


def _getCamouflages(_):
    return itervalues(vehicles.g_cache.customization20().camouflages)


def _getCrewSkins(_):
    return itervalues(tankmen.g_cache.crewSkins().skins)


def _getCrewBooks(_):
    return itervalues(tankmen.g_cache.crewBooks().books)


def _getModifications(_):
    return itervalues(vehicles.g_cache.customization20().modifications)


def _getDecals(_):
    return itervalues(vehicles.g_cache.customization20().decals)


def _getEmblems(_):
    decals = vehicles.g_cache.customization20().decals
    return [ decal for decal in itervalues(decals) if decal.type == DecalType.EMBLEM ]


def _getInscriptions(_):
    decals = vehicles.g_cache.customization20().decals
    return [ decal for decal in itervalues(decals) if decal.type == DecalType.INSCRIPTION ]


def _getStyles(_):
    return itervalues(vehicles.g_cache.customization20().styles)


def _getProjectionDecal(_):
    return itervalues(vehicles.g_cache.customization20().projection_decals)


def _getPersonalNumber(_):
    return itervalues(vehicles.g_cache.customization20().personal_numbers)


def _getAttachment(_):
    return itervalues(vehicles.g_cache.customization20().attachments)


def _getStatTrackers(_):
    return itervalues(vehicles.g_cache.customization20().stat_trackers)


def _getSequence(_):
    return itervalues(vehicles.g_cache.customization20().sequences)


_MODULES_GETTERS = {GUI_ITEM_TYPE.VEHICLE: _getVehicles,
 GUI_ITEM_TYPE.CHASSIS: _getChassis,
 GUI_ITEM_TYPE.ENGINE: _getEngines,
 GUI_ITEM_TYPE.RADIO: _getRadios,
 GUI_ITEM_TYPE.TURRET: _getTurrets,
 GUI_ITEM_TYPE.GUN: _getGuns,
 GUI_ITEM_TYPE.SHELL: _getShells,
 GUI_ITEM_TYPE.EQUIPMENT: _getEquipments,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: _getBattleBoosters,
 GUI_ITEM_TYPE.BATTLE_ABILITY: _getBattleAbilities,
 GUI_ITEM_TYPE.OPTIONALDEVICE: _getOptionalDevices,
 GUI_ITEM_TYPE.PAINT: _getPaints,
 GUI_ITEM_TYPE.CAMOUFLAGE: _getCamouflages,
 GUI_ITEM_TYPE.MODIFICATION: _getModifications,
 GUI_ITEM_TYPE.DECAL: _getDecals,
 GUI_ITEM_TYPE.EMBLEM: _getEmblems,
 GUI_ITEM_TYPE.INSCRIPTION: _getInscriptions,
 GUI_ITEM_TYPE.STYLE: _getStyles,
 GUI_ITEM_TYPE.PROJECTION_DECAL: _getProjectionDecal,
 GUI_ITEM_TYPE.PERSONAL_NUMBER: _getPersonalNumber,
 GUI_ITEM_TYPE.CREW_SKINS: _getCrewSkins,
 GUI_ITEM_TYPE.CREW_BOOKS: _getCrewBooks,
 GUI_ITEM_TYPE.SEQUENCE: _getSequence,
 GUI_ITEM_TYPE.ATTACHMENT: _getAttachment,
 GUI_ITEM_TYPE.STAT_TRACKER: _getStatTrackers}

def getItemsIterator(data, nationID=None, itemTypeID=None, onlyWithPrices=False):
    if 'itemPrices' in data and onlyWithPrices:
        prices = data['itemPrices']
    else:
        prices = ItemsPrices()
    getters = _MODULES_GETTERS
    if itemTypeID is None:
        itemTypeIDs = viewkeys(getters)
    elif itemTypeID in getters:
        itemTypeIDs = (itemTypeID,)
    else:
        raise SoftException('itemTypeID is invalid: {}'.format(itemTypeID))
    if nationID is None:
        nationIDs = viewvalues(nations.INDICES)
    else:
        nationIDs = (nationID,)
    for nextID in nationIDs:
        for typeID in itemTypeIDs:
            getter = getters[typeID]
            for item in getter(nextID):
                intCD = item.compactDescr
                if not onlyWithPrices or intCD in prices:
                    yield intCD

    return
