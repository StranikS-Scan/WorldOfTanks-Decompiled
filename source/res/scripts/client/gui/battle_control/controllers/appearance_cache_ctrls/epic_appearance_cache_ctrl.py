# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/appearance_cache_ctrls/epic_appearance_cache_ctrl.py
from gui.battle_control.controllers.appearance_cache_ctrls import getWholeVehModels
from gui.battle_control.controllers.appearance_cache_ctrls.default_appearance_cache_ctrl import DefaultAppearanceCacheController
from items.vehicles import VehicleDescriptor

class EpicAppearanceCacheController(DefaultAppearanceCacheController):
    SUPPLY_VEHICLES = ('germany:G00_Artilleriebunker', 'germany:G00_Feuerbunker', 'germany:G00_Startgestell', 'ussr:R00_Baloon')

    def arenaLoadCompleted(self):
        super(EpicAppearanceCacheController, self).arenaLoadCompleted()
        self._precacheExtraResources()

    def _precacheExtraResources(self):
        for vehicleTypeName in self.SUPPLY_VEHICLES:
            descr = VehicleDescriptor(typeName=vehicleTypeName)
            self._appearanceCache.loadResources(descr.makeCompactDescr(), getWholeVehModels(descr))
