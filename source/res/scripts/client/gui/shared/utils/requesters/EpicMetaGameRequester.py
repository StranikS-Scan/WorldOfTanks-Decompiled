# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/EpicMetaGameRequester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IEpicMetaGameRequester
from items.vehicles import ABILITY_SLOTS_BY_VEHICLE_CLASS, getVehicleClass

class EpicMetaGameRequester(AbstractSyncDataRequester, IEpicMetaGameRequester):

    @property
    def playerLevelInfo(self):
        return self.getCacheValue('metaLevel', (0, 0, 0))

    @property
    def seasonData(self):
        return self.getCacheValue('seasonData', (0, False, None))

    @property
    def skillPoints(self):
        return self.getCacheValue('abilityPts', 0)

    def selectedSkills(self, vehicleCD):
        skillsDict = self.getCacheValue('selectedAbilities', None)
        return skillsDict.get(vehicleCD, [-1] * ABILITY_SLOTS_BY_VEHICLE_CLASS[getVehicleClass(vehicleCD)]) if skillsDict is not None else [-1] * ABILITY_SLOTS_BY_VEHICLE_CLASS[getVehicleClass(vehicleCD)]

    @property
    def skillLevels(self):
        return self.getCacheValue('abilities', {})

    @property
    def battleCount(self):
        return self.getCacheValue('battleCount', 0)

    @property
    def averageXP(self):
        return self.getCacheValue('famePts', 0) / self.battleCount if self.battleCount > 0 else 0

    @async
    def _requestCache(self, callback):
        BigWorld.player().epicMetaGame.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['epicMetaGame']) if 'epicMetaGame' in data else dict()
