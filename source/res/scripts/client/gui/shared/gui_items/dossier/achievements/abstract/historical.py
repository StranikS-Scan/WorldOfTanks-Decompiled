# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/historical.py
from regular import RegularAchievement
from mixins import HasVehiclesList, Deprecated

class HistoricalAchievement(Deprecated, HasVehiclesList, RegularAchievement):

    def getVehiclesListTitle(self):
        pass

    def _getVehiclesDescrsList(self):
        return []
