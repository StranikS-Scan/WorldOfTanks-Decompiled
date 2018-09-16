# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/vehicle_filters.py
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from nations import INDICES
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.Scaleform import getVehicleTypeAssetPath, getNationsFilterAssetPath, getLevelsAssetPath
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TYPES_ORDER_INDICES

def packIntVehicleTypesFilter(defaultVehType=-1):
    result = [{'label': MENU.CAROUSEL_TANK_FILTER_ALL,
      'data': defaultVehType,
      'icon': getVehicleTypeAssetPath('all')}]
    for idx, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
        result.append({'label': '#menu:carousel_tank_filter/' + vehicleType,
         'data': idx,
         'icon': getVehicleTypeAssetPath(vehicleType)})

    return result


def packVehicleTypesFilter(defaultVehType, types=VEHICLE_TYPES_ORDER):
    if types is not VEHICLE_TYPES_ORDER:
        types = sorted(types, key=lambda _type: VEHICLE_TYPES_ORDER_INDICES[_type])
    result = [{'label': MENU.CAROUSEL_TANK_FILTER_ALL,
      'data': defaultVehType,
      'icon': getVehicleTypeAssetPath('all')}]
    for vehicleType in types:
        result.append({'label': '#menu:carousel_tank_filter/' + vehicleType,
         'data': vehicleType,
         'icon': getVehicleTypeAssetPath(vehicleType)})

    return result


def packNationsFilter(nations=GUI_NATIONS):
    if nations is not GUI_NATIONS:
        nations = sorted(nations, key=lambda nation: GUI_NATIONS_ORDER_INDEX[nation])
    result = [{'label': MENU.NATIONS_ALL,
      'data': -1,
      'icon': getNationsFilterAssetPath('all')}]
    for nation in nations:
        result.append({'label': MENU.nations(nation),
         'data': INDICES[nation],
         'icon': getNationsFilterAssetPath(nation)})

    return result


def packVehicleLevelsFilter(levelRange=range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)):
    result = [{'label': MENU.LEVELS_ALL,
      'data': -1,
      'icon': getLevelsAssetPath('level_all')}]
    for level in levelRange:
        result.append({'label': '#menu:levels/%d' % level,
         'data': level,
         'icon': getLevelsAssetPath('level_%d' % level)})

    return result
