# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progression_styles/stage_switcher_widget_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class SwitcherType(IntEnum):
    DIGITAL = 0
    TEXT = 1


class StageSwitcherWidgetModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=7, commands=1):
        super(StageSwitcherWidgetModel, self).__init__(properties=properties, commands=commands)

    def getIsVisible(self):
        return self._getBool(0)

    def setIsVisible(self, value):
        self._setBool(0, value)

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getSelectedLevel(self):
        return self._getNumber(2)

    def setSelectedLevel(self, value):
        self._setNumber(2, value)

    def getNumberOfBullets(self):
        return self._getNumber(3)

    def setNumberOfBullets(self, value):
        self._setNumber(3, value)

    def getIsBulletsBeforeCurrentDisabled(self):
        return self._getBool(4)

    def setIsBulletsBeforeCurrentDisabled(self, value):
        self._setBool(4, value)

    def getSwitcherType(self):
        return SwitcherType(self._getNumber(5))

    def setSwitcherType(self, value):
        self._setNumber(5, value.value)

    def getStyleID(self):
        return self._getNumber(6)

    def setStyleID(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(StageSwitcherWidgetModel, self)._initialize()
        self._addBoolProperty('isVisible', False)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('selectedLevel', 0)
        self._addNumberProperty('numberOfBullets', 4)
        self._addBoolProperty('isBulletsBeforeCurrentDisabled', True)
        self._addNumberProperty('switcherType')
        self._addNumberProperty('styleID', 0)
        self.onChange = self._addCommand('onChange')
