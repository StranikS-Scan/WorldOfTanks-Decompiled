# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/__init__.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES

def vehicleComparisonKey(vehicle):
    return (not vehicle.isFavorite,
     GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
     VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
     vehicle.level,
     vehicle.userName)
