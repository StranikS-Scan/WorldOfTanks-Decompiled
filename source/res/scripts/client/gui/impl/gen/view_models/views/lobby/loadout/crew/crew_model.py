# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/crew_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.tankman_model import TankmanModel

class CrewModel(ViewModel):
    __slots__ = ('onOpenCrew', 'onOpenBarracks', 'onToggleAcceleratedTraining', 'onToggleIntensiveTraining', 'onDogMoreInfoClick')
    DEFAULT_STATE = 'default'
    DISABLED_STATE = 'disabled'
    ON_TRAINING_STATE = 'on'
    OFF_TRAINING_STATE = 'off'
    DISABLED_TRAINING_STATE = 'disabled'

    def __init__(self, properties=8, commands=5):
        super(CrewModel, self).__init__(properties=properties, commands=commands)

    def getHasDog(self):
        return self._getBool(0)

    def setHasDog(self, value):
        self._setBool(0, value)

    def getCrew(self):
        return self._getArray(1)

    def setCrew(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCrewType():
        return TankmanModel

    def getSlots(self):
        return self._getArray(2)

    def setSlots(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSlotsType():
        return SlotModel

    def getState(self):
        return self._getString(3)

    def setState(self, value):
        self._setString(3, value)

    def getBerthsCount(self):
        return self._getNumber(4)

    def setBerthsCount(self, value):
        self._setNumber(4, value)

    def getAcceleratedTraining(self):
        return self._getString(5)

    def setAcceleratedTraining(self, value):
        self._setString(5, value)

    def getIntensiveTraining(self):
        return self._getString(6)

    def setIntensiveTraining(self, value):
        self._setString(6, value)

    def getVehicleNation(self):
        return self._getString(7)

    def setVehicleNation(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(CrewModel, self)._initialize()
        self._addBoolProperty('hasDog', False)
        self._addArrayProperty('crew', Array())
        self._addArrayProperty('slots', Array())
        self._addStringProperty('state', 'default')
        self._addNumberProperty('berthsCount', 0)
        self._addStringProperty('acceleratedTraining', '')
        self._addStringProperty('intensiveTraining', '')
        self._addStringProperty('vehicleNation', '')
        self.onOpenCrew = self._addCommand('onOpenCrew')
        self.onOpenBarracks = self._addCommand('onOpenBarracks')
        self.onToggleAcceleratedTraining = self._addCommand('onToggleAcceleratedTraining')
        self.onToggleIntensiveTraining = self._addCommand('onToggleIntensiveTraining')
        self.onDogMoreInfoClick = self._addCommand('onDogMoreInfoClick')
