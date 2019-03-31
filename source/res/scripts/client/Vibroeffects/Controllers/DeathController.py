# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/DeathController.py
# Compiled at: 2011-03-25 20:17:34
from OnceController import OnceController

class DeathController:
    __wasVehicleAlive = None

    def update(self, isVehicleAlive):
        if self.__wasVehicleAlive and not isVehicleAlive:
            OnceController('crit_death_veff')
        self.__wasVehicleAlive = isVehicleAlive
