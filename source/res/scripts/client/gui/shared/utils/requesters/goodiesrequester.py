# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/GoodiesRequester.py
from __future__ import absolute_import
from collections import namedtuple
from future.utils import iteritems
import BigWorld
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IGoodiesRequester
GoodieVariable = namedtuple('GoodieVariable', 'state finishTime count expirations')

class _ClanReserveInfo(namedtuple('_ClanReserveInfo', 'finishTime value duration')):
    __slots__ = ()

    def __new__(cls, finishTime, value, duration=3600):
        return super(_ClanReserveInfo, cls).__new__(cls, finishTime, value, duration)


class GoodiesRequester(AbstractSyncDataRequester, IGoodiesRequester):

    def _requestCache(self, callback=None):
        BigWorld.player().goodies.getCache(lambda resID, value: self._response(resID, value, callback))

    @property
    def goodies(self):
        return self.getCacheValue('goodies', {})

    def getActiveClanReserves(self):
        return self.getCacheValue('clanReserves', {})

    def _preprocessValidData(self, data):
        processed = dict(data)
        goodies = data.get('goodies', {})
        processed['goodies'] = {gID:GoodieVariable(status, finishTime, count, expirations) for gID, (status, finishTime, count, expirations) in iteritems(goodies)}
        clanReserves = {}
        for crID, crData in iteritems(data.get('clanReserves', {})):
            clanReserves[crID] = _ClanReserveInfo(crData['timeExpiration'], crData['factors'], crData['duration'])

        processed['clanReserves'] = clanReserves
        return processed
