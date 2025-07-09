# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/vehicle_stats_helper.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache
DEFAULT_VEHICLE_STATS = 0

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getStatTrackersVehicleStats(vehCD, databaseID=None, itemsCache=None):
    accDossier = itemsCache.items.getAccountDossier(databaseID=databaseID)
    vehStats = accDossier.getStatTrackersVehicleStatsBlock().getVehicles().get(vehCD)
    return vehStats.frags if vehStats else DEFAULT_VEHICLE_STATS
