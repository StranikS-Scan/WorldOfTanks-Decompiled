# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/formatters/vehicle_filters.py
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui import GUI_NATIONS
from gui.Scaleform import getVehicleTypeAssetPath, getNationsFilterAssetPath, getLevelsAssetPath
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER

def packIntVehicleTypesFilter(defaultVehType=-1):
    result = [{'label': MENU.CAROUSEL_TANK_FILTER_ALL,
      'data': defaultVehType,
      'icon': getVehicleTypeAssetPath('all')}]
    for idx, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
        result.append({'label': '#menu:carousel_tank_filter/' + vehicleType,
         'data': idx,
         'icon': getVehicleTypeAssetPath(vehicleType)})

    return result


def packVehicleTypesFilter(defaultVehType):
    result = [{'label': MENU.CAROUSEL_TANK_FILTER_ALL,
      'data': defaultVehType,
      'icon': getVehicleTypeAssetPath('all')}]
    for _, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
        result.append({'label': '#menu:carousel_tank_filter/' + vehicleType,
         'data': vehicleType,
         'icon': getVehicleTypeAssetPath(vehicleType)})

    return result


def packNationsFilter():
    result = [{'label': MENU.NATIONS_ALL,
      'data': -1,
      'icon': getNationsFilterAssetPath('all')}]
    for idx, nation in enumerate(GUI_NATIONS):
        result.append({'label': MENU.nations(nation),
         'data': idx,
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
