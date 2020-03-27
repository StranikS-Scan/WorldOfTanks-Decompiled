# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/collector_vehicle.py


class CollectorVehicleConsts(object):
    CONFIG_NAME = 'collector_vehicle_config'
    COLLECTOR_VEHICLES_TAG = 'collectorVehicle'
    COLLECTOR_MEDAL_PREFIX = 'collectorVehicle'
    IS_ENABLED = 'enabled'


class CollectorVehicleConfig(object):
    __slots__ = ('__config',)

    def __init__(self, config):
        self.__config = config

    @property
    def isEnabled(self):
        return self.__config.get(CollectorVehicleConsts.IS_ENABLED, False)
