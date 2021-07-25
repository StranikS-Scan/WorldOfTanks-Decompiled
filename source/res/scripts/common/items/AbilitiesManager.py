# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/AbilitiesManager.py
import typing
from operator import add
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

    def addBuild(self, vehInvID, scopeName, perksDict, priority=DEFAULT_PRIORITY):
        validPerks = {perkID:perkLevel for perkID, perkLevel in perksDict.iteritems() if perks.g_cache.perks().validatePerk(perkID)[0] and perkLevel > 0}
        if len(validPerks) != len(perksDict):
            LOG_DEBUG_DEV('AbilitiesManager.addBuild: build is empty or holds not valid perks: {}, {}, {}, {}'.format(vehInvID, scopeName, priority, perksDict))
        if validPerks:
            LOG_DEBUG_DEV('AbilitiesManager.addBuild:{}, {}, {}, {}'.format(vehInvID, scopeName, priority, validPerks))
            del_index = None
            for i, (pr, rec) in enumerate(self._scopes[vehInvID]):
                if rec.name == scopeName:
                    del_index = i
                    break

            if del_index is not None:
                del self._scopes[vehInvID][del_index]
            self._scopes[vehInvID].append((priority, _AbilityRecord(scopeName, validPerks)))
            return True
        else:
            return False

    def modifyBuild(self, vehInvID, scopeName, modDict, operator=add):
        build = None
        for pr, rec in self._scopes[vehInvID]:
            if rec.name == scopeName:
                build = rec.perks
                break

        if build is None:
            LOG_DEBUG_DEV('AbilitiesManager.modifyBuild: could not find build {} for vehicle {} to modify. Creating a new one'.format(scopeName, vehInvID))
            self.addBuild(vehInvID, scopeName, modDict)
            return
        else:
            for perkID, mod in modDict.iteritems():
                buildValue = build.get(perkID)
                if buildValue is None:
                    build[perkID] = mod
                build[perkID] = operator(buildValue, mod)

            return

    def getPerksByVehicle(self, vehInvID, perksMaxLevelConfig=None):
        vehiclePerks = self._scopes.get(vehInvID)
        if vehiclePerks is None:
            return {}
        else:
            vehBuilds = sorted(vehiclePerks, key=lambda e: e[0])
            return {vehBuild[1].name:tuple(((perkID, min(perksMaxLevelConfig.getMaxPerkLevel(perkID, level), level)) for perkID, level in vehBuild[1].perks.iteritems())) for vehBuild in vehBuilds} if perksMaxLevelConfig is not None else {vehBuild[1].name:tuple(vehBuild[1].perks.iteritems()) for vehBuild in vehBuilds}

    def getPerksListByVehicle(self, vehInvID):
        vehiclePerks = self._scopes.get(vehInvID)
        if vehiclePerks is None:
            return {}
        else:
            vehBuilds = sorted(vehiclePerks, key=lambda e: e[0])
            return {vehBuild[1].name:vehBuild[1].perks.keys() for vehBuild in vehBuilds}

    def getPerkLevelByVehicle(self, vehInvID, scopeName, perkID):
        for pr, rec in self._scopes[vehInvID]:
            if rec.name == scopeName:
                return rec.perks.get(perkID, 0)

    def getScopesNames(self, vehInvID):
        vehiclePerks = self._scopes.get(vehInvID)
        if vehiclePerks is None:
            return {}
        else:
            vehBuilds = sorted(vehiclePerks, key=lambda e: e[0])
            return {i:build[1].name for i, build in enumerate(vehBuilds)}

    def removePerksByVehicle(self, vehInvID):
        self._scopes.pop(vehInvID, None)
        return

    def reset(self):
        self._scopes.clear()


class PerksMaxLevelConfig(object):

    def __init__(self, config, bonusType=None):
        super(PerksMaxLevelConfig, self).__init__()
        self._config = config
        self._bonusType = bonusType

    def getMaxPerkLevel(self, perkID, default=None):
        maxLevel = None
        if self._bonusType in self._config['overrides']:
            maxLevel = self._getMaxPerkLevelFromConfig(self._config['overrides'][self._bonusType], perkID)
        if maxLevel is None:
            maxLevel = self._getMaxPerkLevelFromConfig(self._config['default'], perkID)
        return maxLevel if maxLevel is not None else default

    def _getMaxPerkLevelFromConfig(self, config, perkID):
        return config['maxPerkLevels'].get(perkID, config['maxLevel'])
