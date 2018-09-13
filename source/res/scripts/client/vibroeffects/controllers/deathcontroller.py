# Embedded file name: scripts/client/Vibroeffects/Controllers/DeathController.py
from OnceController import OnceController

class DeathController:
    __wasVehicleAlive = None

    def update(self, isVehicleAlive):
        if self.__wasVehicleAlive and not isVehicleAlive:
            OnceController('crit_death_veff')
        self.__wasVehicleAlive = isVehicleAlive
