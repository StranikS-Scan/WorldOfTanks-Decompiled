# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/ArmoryYardRequester.py
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IArmoryYardRequester

class ArmoryYardRequester(AbstractSyncDataRequester, IArmoryYardRequester):

    @property
    def data(self):
        return self._data

    @property
    def progressionLevel(self):
        from armory_yard_constants import PROGRESSION_LEVEL_PDATA_KEY
        return self._data.get(PROGRESSION_LEVEL_PDATA_KEY, 0)

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().armoryYard.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        from armory_yard_constants import PDATA_KEY_ARMORY_YARD
        return dict(data[PDATA_KEY_ARMORY_YARD]) if PDATA_KEY_ARMORY_YARD in data else dict()
