# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_requester.py
from typing import Dict, List
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from items.components.lunar_ny_constants import INVALID_CHARM_ID
from lunar_ny_common import settings_constants as const
from lunar_ny.lunar_ny_charm import LunarNYCharm
from skeletons.gui.shared.utils.requesters import IRequester

class ILunarNYRequester(IRequester):

    def getCharms(self):
        raise NotImplementedError

    def getSlots(self):
        raise NotImplementedError

    def getCharmsInSlots(self):
        raise NotImplementedError

    def getCountCharms(self):
        raise NotImplementedError


class LunarNYRequester(AbstractSyncDataRequester, ILunarNYRequester):

    def getCharms(self):
        return self.getCacheValue(const.INVENTORY_CHARMS, {}).copy()

    def getSlots(self):
        return self.getCacheValue(const.ALBUM_SLOTS, [])[:]

    def getCharmsInSlots(self):
        charms = self.getCacheValue(const.INVENTORY_CHARMS, {})
        slots = self.getCacheValue(const.ALBUM_SLOTS, [])
        return [ (charms[charmID] if charmID > INVALID_CHARM_ID else None) for charmID in slots ]

    def getCountCharms(self):
        charms = self.getCacheValue(const.INVENTORY_CHARMS, {})
        count = 0
        for charm in charms.values():
            count += charm.getCountInStorage() + charm.getCountInSlots()

        return count

    def _preprocessValidData(self, data):
        result = {}
        if const.INVENTORY_CHARMS in data:
            inventoryCharms = {}
            for charmId, (totalCount, unseenCount, countInSlots) in data[const.INVENTORY_CHARMS].iteritems():
                inventoryCharms[charmId] = LunarNYCharm(charmId, totalCount, unseenCount, countInSlots)

            result[const.INVENTORY_CHARMS] = inventoryCharms
        if const.ALBUM_SLOTS in data:
            result[const.ALBUM_SLOTS] = data[const.ALBUM_SLOTS]
        return result

    @async
    def _requestCache(self, callback):
        BigWorld.player().lunarNY.getCache(lambda resID, value: self._response(resID, value, callback))
