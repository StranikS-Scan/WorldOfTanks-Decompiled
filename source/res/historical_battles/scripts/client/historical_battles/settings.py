# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/settings.py
from collections import namedtuple

class HBConfig(namedtuple('HBConfig', ('startDate', 'fronts', 'points', 'endDate', 'eventProgression', 'divisions', 'isBattlesEnabled', 'isEnabled', 'heroVehicle', 'hangarEnvironmentSettings', 'mainDiscount', 'mainRewardToken'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(startDate={}, fronts={}, points={}, endDate={}, eventProgression={}, divisions={}, isBattlesEnabled=False, isEnabled=False, heroVehicle=False, hangarEnvironmentSettings={}, mainDiscount={}, mainRewardToken='')
        defaults.update(kwargs)
        return super(HBConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class HBShop(namedtuple('HBShop', ('enabled', 'shopBundles', 'groups'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, shopBundles={}, groups={})
        defaults.update(kwargs)
        return super(HBShop, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()
