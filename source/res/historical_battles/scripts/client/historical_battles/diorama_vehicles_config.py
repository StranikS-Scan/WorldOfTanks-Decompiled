# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/diorama_vehicles_config.py
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.historical_battles_hangar_vehicles_config import ConfigDataReader

class DioramaVehiclesConfig(object):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        reader = ConfigDataReader()
        reader.readConfigFile()
        self.__effects = reader.effectsStorage
        self.__frontConfigs = reader.frontConfigs

    @property
    def effects(self):
        return self.__effects

    def getSelectedFrontConfig(self):
        frontId = self._gameEventController.frontController.getSelectedFrontID()
        return self.__frontConfigs[frontId]

    @staticmethod
    def getSelectedFrontVehicle(intCD, index=0):
        frontConfig = DioramaVehiclesConfig.__getFrontConfig()
        return frontConfig.getVehicleData(intCD, index)

    @staticmethod
    def getSelectedFrontLayoutVehicle(index):
        frontConfig = DioramaVehiclesConfig.__getFrontConfig()
        return frontConfig.getDefaultSlotVehicleData(index)

    @staticmethod
    def getSelectedFrontVehicleEffects(intCD, index):
        frontConfig = DioramaVehiclesConfig.__getFrontConfig()
        return frontConfig.getVehicleEffects(intCD, index)

    @staticmethod
    def getTankEffectConfig(name):
        config = DioramaVehiclesConfig.__getInstance()
        return config.effects.get(name, None)

    @classmethod
    def __getInstance(cls):
        if not hasattr(cls, 'configInstance'):
            cls.configInstance = DioramaVehiclesConfig()
        return cls.configInstance

    @staticmethod
    def __getFrontConfig():
        config = DioramaVehiclesConfig.__getInstance()
        return config.getSelectedFrontConfig()
