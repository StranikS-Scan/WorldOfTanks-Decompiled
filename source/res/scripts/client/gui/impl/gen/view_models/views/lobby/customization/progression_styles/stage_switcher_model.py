# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progression_styles/stage_switcher_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class SwitcherType(IntEnum):
    DIGITAL = 0
    TEXT = 1


class StageSwitcherModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=6, commands=1):
        super(StageSwitcherModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getSelectedLevel(self):
        return self._getNumber(1)

    def setSelectedLevel(self, value):
        self._setNumber(1, value)

    def getNumberOfBullets(self):
        return self._getNumber(2)

    def setNumberOfBullets(self, value):
        self._setNumber(2, value)

    def getIsBulletsBeforeCurrentDisabled(self):
        return self._getBool(3)

    def setIsBulletsBeforeCurrentDisabled(self, value):
        self._setBool(3, value)

    def getSwitcherType(self):
        return SwitcherType(self._getNumber(4))

    def setSwitcherType(self, value):
        self._setNumber(4, value.value)

    def getStyleID(self):
        return self._getNumber(5)

    def setStyleID(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(StageSwitcherModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('selectedLevel', 0)
        self._addNumberProperty('numberOfBullets', 4)
        self._addBoolProperty('isBulletsBeforeCurrentDisabled', True)
        self._addNumberProperty('switcherType')
        self._addNumberProperty('styleID', 0)
        self.onChange = self._addCommand('onChange')
