# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_header_model.py
from frameworks.wulf import ViewModel

class CrewHeaderModel(ViewModel):
    __slots__ = ('onCrewOperationsClick', 'onAccelerateCrewTrainingToggle', 'onIdleCrewBonusToggle')

    def __init__(self, properties=5, commands=3):
        super(CrewHeaderModel, self).__init__(properties=properties, commands=commands)

    def getIsAccelerateCrewTrainingActive(self):
        return self._getBool(0)

    def setIsAccelerateCrewTrainingActive(self, value):
        self._setBool(0, value)

    def getIsAccelerateCrewTrainingAvailable(self):
        return self._getBool(1)

    def setIsAccelerateCrewTrainingAvailable(self, value):
        self._setBool(1, value)

    def getIsIdleCrewBonusActive(self):
        return self._getBool(2)

    def setIsIdleCrewBonusActive(self, value):
        self._setBool(2, value)

    def getIsIdleCrewBonusAvailable(self):
        return self._getBool(3)

    def setIsIdleCrewBonusAvailable(self, value):
        self._setBool(3, value)

    def getIsIdleCrewCompatible(self):
        return self._getBool(4)

    def setIsIdleCrewCompatible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CrewHeaderModel, self)._initialize()
        self._addBoolProperty('isAccelerateCrewTrainingActive', False)
        self._addBoolProperty('isAccelerateCrewTrainingAvailable', False)
        self._addBoolProperty('isIdleCrewBonusActive', False)
        self._addBoolProperty('isIdleCrewBonusAvailable', False)
        self._addBoolProperty('isIdleCrewCompatible', False)
        self.onCrewOperationsClick = self._addCommand('onCrewOperationsClick')
        self.onAccelerateCrewTrainingToggle = self._addCommand('onAccelerateCrewTrainingToggle')
        self.onIdleCrewBonusToggle = self._addCommand('onIdleCrewBonusToggle')
