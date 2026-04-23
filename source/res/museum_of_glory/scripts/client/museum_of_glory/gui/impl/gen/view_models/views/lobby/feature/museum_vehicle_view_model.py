# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/impl/gen/view_models/views/lobby/feature/museum_vehicle_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from museum_of_glory.gui.impl.gen.view_models.views.lobby.feature.museum_vehicle_model import MuseumVehicleModel

class MuseumVehicleViewModel(ViewModel):
    __slots__ = ('onSelectVehicle', 'onBackToHangar', 'onMoveSpace', 'onStartMoving', 'onAudioCheckboxToggle', 'onExcursionPlay', 'onExcursionPause', 'onVehiclePlayTimeLog', 'onExcursionEnd')
    ARG_VEHICLE_INDEX = 'vehicleIndex'

    def __init__(self, properties=9, commands=9):
        super(MuseumVehicleViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentVehicleIndex(self):
        return self._getNumber(0)

    def setCurrentVehicleIndex(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return MuseumVehicleModel

    def getIsAudioChecked(self):
        return self._getBool(2)

    def setIsAudioChecked(self, value):
        self._setBool(2, value)

    def getIsAudioEnabled(self):
        return self._getBool(3)

    def setIsAudioEnabled(self, value):
        self._setBool(3, value)

    def getIsWindowAccessible(self):
        return self._getBool(4)

    def setIsWindowAccessible(self, value):
        self._setBool(4, value)

    def getIsExcursionPlaying(self):
        return self._getBool(5)

    def setIsExcursionPlaying(self, value):
        self._setBool(5, value)

    def getIsExcursionPaused(self):
        return self._getBool(6)

    def setIsExcursionPaused(self, value):
        self._setBool(6, value)

    def getIsAllBlocked(self):
        return self._getBool(7)

    def setIsAllBlocked(self, value):
        self._setBool(7, value)

    def getIsIntroPlay(self):
        return self._getBool(8)

    def setIsIntroPlay(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(MuseumVehicleViewModel, self)._initialize()
        self._addNumberProperty('currentVehicleIndex', 0)
        self._addArrayProperty('vehicles', Array())
        self._addBoolProperty('isAudioChecked', False)
        self._addBoolProperty('isAudioEnabled', False)
        self._addBoolProperty('isWindowAccessible', True)
        self._addBoolProperty('isExcursionPlaying', False)
        self._addBoolProperty('isExcursionPaused', False)
        self._addBoolProperty('isAllBlocked', False)
        self._addBoolProperty('isIntroPlay', False)
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
        self.onBackToHangar = self._addCommand('onBackToHangar')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onAudioCheckboxToggle = self._addCommand('onAudioCheckboxToggle')
        self.onExcursionPlay = self._addCommand('onExcursionPlay')
        self.onExcursionPause = self._addCommand('onExcursionPause')
        self.onVehiclePlayTimeLog = self._addCommand('onVehiclePlayTimeLog')
        self.onExcursionEnd = self._addCommand('onExcursionEnd')
