# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBMainHeroTank.py
from HeroTank import HeroTank

class HBMainHeroTank(HeroTank):

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()

    def _onVehicleDestroy(self):
        super(HBMainHeroTank, self)._onVehicleDestroy()
        self.removeVehicle()
