# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/AbilitiesManager.py
import typing
import heapq
from collections import defaultdict, namedtuple
from items import perks
from itertools import imap
from debug_utils import LOG_DEBUG_DEV
_AbilityRecord = namedtuple('_AbilityRecord', ('name', 'perks'))

class AbilitiesManager(object):
    DEFAULT_PRIORITY = 99

    def __init__(self):
        self._scopes = defaultdict(list)

    def destroy(self):
        self.reset()

    def addBuild(self, vehInvID, scopeName, perksList, priority=DEFAULT_PRIORITY):
        validPerks = filter(lambda (perkID, perkLevel): perks.g_cache.perks().validatePerk(perkID)[0] and perkLevel > 0, perksList)
        if len(validPerks) != len(perksList):
            LOG_DEBUG_DEV('AbilitiesManager.addBuild: build is empty or holds not valid perks: {}, {}, {}, {}'.format(vehInvID, scopeName, priority, perksList))
        if validPerks:
            LOG_DEBUG_DEV('AbilitiesManager.addBuild:{}, {}, {}, {}'.format(vehInvID, scopeName, priority, validPerks))
            del_index = None
            for i, (pr, rec) in enumerate(self._scopes[vehInvID]):
                if rec.name == scopeName:
                    del_index = i
                    break

            if del_index is not None:
                del self._scopes[vehInvID][del_index]
                heapq.heapify(self._scopes[vehInvID])
            heapq.heappush(self._scopes[vehInvID], (priority, _AbilityRecord(scopeName, tuple(validPerks))))
            return True
        else:
            return False

    def getPerksByVehicle(self, vehInvID):
        vehiclePerks = self._scopes.get(vehInvID)
        if vehiclePerks is None:
            return tuple()
        else:
            srt = heapq.nsmallest(len(vehiclePerks), vehiclePerks)
            return tuple(imap(lambda x: x[1].perks, srt))

    def getScopesNames(self, vehInvID):
        vehiclePerks = self._scopes.get(vehInvID)
        if vehiclePerks is None:
            return {}
        else:
            srt = heapq.nsmallest(len(vehiclePerks), vehiclePerks)
            return {i:item[1].name for i, item in enumerate(srt)}

    def removePerksByVehicle(self, vehInvID):
        if vehInvID in self._scopes:
            self._scopes.pop(vehInvID)

    def reset(self):
        self._scopes.clear()
