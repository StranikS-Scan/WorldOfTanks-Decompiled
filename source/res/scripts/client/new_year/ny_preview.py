# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_preview.py
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from items.components.ny_constants import ToySettings
from new_year.ny_constants import Collections
from skeletons.gui.shared import IItemsCache
_DEFAULT_VEH_ID = 6929
_MAP_VEH_ID = {(Collections.NewYear18, ToySettings.SOVIET): 7169,
 (Collections.NewYear18, ToySettings.ASIAN): 6193,
 (Collections.NewYear18, ToySettings.MODERN_WESTERN): 3937,
 (Collections.NewYear18, ToySettings.TRADITIONAL_WESTERN): 6209}

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehiclePreviewID(style, yearName=None, collectionName=None, itemsCache=None):
    styledVehicleCD = None
    if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item):
        styledVehicleCD = g_currentVehicle.item.intCD
    else:
        accDossier = itemsCache.items.getAccountDossier()
        vehiclesStats = accDossier.getRandomStats().getVehicles()
        vehicleGetter = itemsCache.items.getItemByCD
        sortedVehicles = sorted((vehicleGetter(veh) for veh in vehiclesStats.iterkeys()), key=lambda veh: (veh.level, vehiclesStats[veh.intCD].battlesCount), reverse=True)
        for vehicle in sortedVehicles:
            if style.mayInstall(vehicle):
                styledVehicleCD = vehicle.intCD
                break

    if styledVehicleCD is None:
        styledVehicleCD = _MAP_VEH_ID.get((yearName, collectionName), _DEFAULT_VEH_ID)
    return styledVehicleCD
