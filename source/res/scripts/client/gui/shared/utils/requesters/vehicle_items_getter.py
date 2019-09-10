# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/vehicle_items_getter.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params
from items import vehicles, tankmen, EQUIPMENT_TYPES, ItemsPrices
from items.components.c11n_constants import DecalType
from soft_exception import SoftException
import nations

def _getVehicles(nationID):
    return vehicles.g_list.getList(nationID).itervalues()


def _getChassis(nationID):
    return vehicles.g_cache.chassis(nationID).itervalues()


def _getEngines(nationID):
    return vehicles.g_cache.engines(nationID).itervalues()


def _getRadios(nationID):
    return vehicles.g_cache.radios(nationID).itervalues()


def _getTurrets(nationID):
    return vehicles.g_cache.turrets(nationID).itervalues()


def _getGuns(nationID):
    return vehicles.g_cache.guns(nationID).itervalues()


def _getShells(nationID):
    return vehicles.g_cache.shells(nationID).itervalues()


def _filterByNationAndEqType(items, getParameters, nationID, eqType=None):
    ignoreNation = nationID == nations.NONE_INDEX or nationID is None
    ignoreEquipmentType = eqType is None
    if ignoreNation and ignoreEquipmentType:
        return
    else:
        for value in items.itervalues():
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
    return vehicles.g_cache.customization20().paints.itervalues()


def _getCamouflages(_):
    return vehicles.g_cache.customization20().camouflages.itervalues()


def _getCrewSkins(_):
    return tankmen.g_cache.crewSkins().skins.itervalues()


def _getCrewBooks(_):
    return tankmen.g_cache.crewBooks().books.itervalues()


def _getModifications(_):
    return vehicles.g_cache.customization20().modifications.itervalues()


def _getDecals(_):
    return vehicles.g_cache.customization20().decals.itervalues()


def _getEmblems(_):
    decals = vehicles.g_cache.customization20().decals
    return [ decal for decal in decals.itervalues() if decal.type == DecalType.EMBLEM ]


def _getInscriptions(_):
    decals = vehicles.g_cache.customization20().decals
    return [ decal for decal in decals.itervalues() if decal.type == DecalType.INSCRIPTION ]


def _getStyles(_):
    return vehicles.g_cache.customization20().styles.itervalues()


def _getProjectionDecal(_):
    return vehicles.g_cache.customization20().projection_decals.itervalues()


def _getPersonalNumber(_):
    return vehicles.g_cache.customization20().personal_numbers.itervalues()


def _getAttachment(_):
    return vehicles.g_cache.customization20().attachments.itervalues()


def _getSequence(_):
    return vehicles.g_cache.customization20().sequences.itervalues()


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
 GUI_ITEM_TYPE.ATTACHMENT: _getAttachment}

def getItemsIterator(data, nationID=None, itemTypeID=None, onlyWithPrices=False):
    if 'itemPrices' in data and onlyWithPrices:
        prices = data['itemPrices']
    else:
        prices = ItemsPrices()
    getters = _MODULES_GETTERS
    if itemTypeID is None:
        itemTypeIDs = getters.keys()
    elif itemTypeID in getters:
        itemTypeIDs = (itemTypeID,)
    else:
        raise SoftException('itemTypeID is invalid: {}'.format(itemTypeID))
    if nationID is None:
        nationIDs = nations.INDICES.itervalues()
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
