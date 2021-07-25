# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/EpicMetaGameRequester.py
import typing
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IEpicMetaGameRequester

class EpicMetaGameRequester(AbstractSyncDataRequester, IEpicMetaGameRequester):

    @property
    def playerLevelInfo(self):
        return self.getCacheValue('metaLevel', (1, 0))

    @property
    def seasonData(self):
        return self.getCacheValue('seasonData', (0, None, dict()))

    @property
    def skillPoints(self):
        return self.getCacheValue('abilityPts', 0)

    def selectedSkills(self, vehicleCD):
        skillsDict = self.getCacheValue('selectedAbilities', None)
        return skillsDict.get(vehicleCD, []) if skillsDict is not None else []

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
