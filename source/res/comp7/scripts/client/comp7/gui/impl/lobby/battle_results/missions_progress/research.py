# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/missions_progress/research.py
from __future__ import absolute_import
from __future__ import division
import typing
from helpers import dependency
from comp7.gui.shared.gui_items.dossier.stats import getComp7DossierStats
from gui.battle_results.progress.research import VehicleProgressHelper
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7.gui.shared.gui_items.dossier.stats import AccountComp7StatsBlock

class Comp7VehicleProgressHelper(VehicleProgressHelper):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _getAvgVehicleXp(self, vehTypeCompDescr):
        seasonNumber = self.__comp7Ctrl.getActualSeasonNumber()
        if not seasonNumber:
            return 0
        accDossier = self._itemsCache.items.getAccountDossier()
        seasonStats = getComp7DossierStats(accDossier, season=seasonNumber)
        if not seasonStats:
            return 0
        vehiclesStats = seasonStats.getVehicles() or {}
        vehicleStats = vehiclesStats.get(vehTypeCompDescr, None)
        if vehicleStats is not None:
            battlesCount, _wins, xp, _prestigePoints = vehicleStats
            if battlesCount:
                return xp / battlesCount
            return 0
        else:
            return
