# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/prebattle_model.py
from frameworks.wulf import Map, ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class PrebattleModel(ViewModel):
    __slots__ = ('onAction',)
    PLAYER_CREATOR = 'playerCreator'
    PLAYER_READY = 'playerReady'
    READINESS_AVAILABLE = 'readinessAvailable'
    ACTION_ENABLED = 'actionEnabled'
    BATTLE_START_ACTION_TYPE = 'battleStartAction'
    BATTLE_READY_ACTION_TYPE = 'readyAction'
    BATTLE_EXIT_ACTION_TYPE = 'battleExitAction'
    BATTLE_STATE_IDLE = 'idle'
    BATTLE_STATE_SEARCHING = 'searchingBattle'
    BATTLE_STATE_READY = 'battleReady'
    E_SPORT = 'E_SPORT'
    TRAINING = 'TRAINING'
    BATTLE_SESSION = 'BATTLE_SESSION'
    RANDOM = 'RANDOM'
    EVENT = 'EVENT'
    STRONGHOLD = 'STRONGHOLD'
    RANKED = 'RANKED'
    EPIC_TRAINING = 'EPIC_TRAINING'
    TOURNAMENT = 'TOURNAMENT'
    EPIC = 'EPIC'
    BATTLE_ROYALE = 'BATTLE_ROYALE'
    MAPBOX = 'MAPBOX'
    MAPS_TRAINING = 'MAPS_TRAINING'
    BATTLE_ROYALE_TOURNAMENT = 'BATTLE_ROYALE_TOURNAMENT'

    def __init__(self, properties=5, commands=1):
        super(PrebattleModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleVehicleType():
        return VehicleModel

    def getStates(self):
        return self._getMap(1)

    def setStates(self, value):
        self._setMap(1, value)

    @staticmethod
    def getStatesType():
        return (unicode, bool)

    def getCurrentMode(self):
        return self._getString(2)

    def setCurrentMode(self, value):
        self._setString(2, value)

    def getQueueType(self):
        return self._getString(3)

    def setQueueType(self, value):
        self._setString(3, value)

    def getBattleStatus(self):
        return self._getString(4)

    def setBattleStatus(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(PrebattleModel, self)._initialize()
        self._addViewModelProperty('battleVehicle', VehicleModel())
        self._addMapProperty('states', Map(unicode, bool))
        self._addStringProperty('currentMode', '')
        self._addStringProperty('queueType', '')
        self._addStringProperty('battleStatus', '')
        self.onAction = self._addCommand('onAction')
