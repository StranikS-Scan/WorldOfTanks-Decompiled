# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/HistoricalBattlesRequester.py
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IHistoricalBattlesRequester

class HistoricalBattlesRequester(AbstractSyncDataRequester, IHistoricalBattlesRequester):

    @property
    def data(self):
        return self._data

    @property
    def subdivisionsProgressEXP(self):
        return self._data.get('divisionsEXP', {})

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().historicalBattles.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        from historical_battles_common.hb_constants import PDATA_KEY_HISTORICAL_BATTLES
        return dict(data[PDATA_KEY_HISTORICAL_BATTLES]) if PDATA_KEY_HISTORICAL_BATTLES in data else dict()
