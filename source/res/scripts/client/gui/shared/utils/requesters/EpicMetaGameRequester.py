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
    def skillPoints(self):
        return self.getCacheValue('abilityPts', 0)

    def selectedSkills(self, vehicleCD):
        skillsDict = self.getCacheValue('selectedAbilities', None)
        return skillsDict.get(vehicleCD, [-1] * ABILITY_SLOTS_BY_VEHICLE_CLASS[getVehicleClass(vehicleCD)]) if skillsDict is not None else [-1] * ABILITY_SLOTS_BY_VEHICLE_CLASS[getVehicleClass(vehicleCD)]

    @property
    def skillLevels(self):
        return self.getCacheValue('abilities', {})

    @async
    def _requestCache(self, callback):
        BigWorld.player().epicMetaGame.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        return dict(data['epicMetaGame']) if 'epicMetaGame' in data else dict()
