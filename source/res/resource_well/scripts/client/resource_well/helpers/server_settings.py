# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/helpers/server_settings.py
import logging
from collections import namedtuple
from typing import Tuple, List
from shared_utils import makeTupleByDict
_logger = logging.getLogger(__name__)

class RewardConfig(namedtuple('RewardConfig', ('bonus', 'limit', 'isSerial', 'sequence', 'resources', 'availableAfter', 'points', 'order'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(bonus={}, limit=0, isSerial=False, sequence='', resources={}, availableAfter='', points=0, order=0)
        defaults.update(kwargs)
        cls.__packResourceConfigs(defaults)
        return super(RewardConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    @classmethod
    def __packResourceConfigs(cls, data):
        resources = {}
        for resourceType, resourceConfig in data['resources'].iteritems():
            resources[resourceType] = {name:_ResourceConfig(name=name, rate=resourceData.get('rate'), limit=resourceData.get('limit')) for name, resourceData in resourceConfig.iteritems()}

        data['resources'] = resources


class _ResourceConfig(namedtuple('_ResourceConfig', ('name', 'rate', 'limit'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(name='', rate=0, limit=0)
        defaults.update(kwargs)
        return super(_ResourceConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()


class ResourceWellConfig(namedtuple('_ResourceWellConfig', ('isEnabled', 'season', 'finishTime', 'remindTime', 'rewards', 'startTime', 'infoPageUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, season=0, startTime=0, finishTime=0, remindTime=0, rewards={}, infoPageUrl='')
        defaults.update(kwargs)
        cls.__packRewardsConfigs(defaults)
        return super(ResourceWellConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        self.__packRewardsConfigs(dataToUpdate)
        return self._replace(**dataToUpdate)

    def getRewardConfig(self, rewardID):
        if rewardID not in self.rewards:
            _logger.error('Invalid rewardID - %s. Available IDs: %s', rewardID, str(self.rewards.keys()))
            return RewardConfig()
        return self.rewards[rewardID]

    def getParentRewardID(self, rewardID):
        reward = self.getRewardConfig(rewardID)
        return reward.availableAfter

    def getSortedRewardsByOrder(self):
        return sorted(self.rewards.items(), key=lambda item: item[1].order)

    @classmethod
    def __packRewardsConfigs(cls, data):
        if 'rewards' not in data:
            return
        data['rewards'] = {rewardID:makeTupleByDict(RewardConfig, reward) for rewardID, reward in data['rewards'].iteritems()}
