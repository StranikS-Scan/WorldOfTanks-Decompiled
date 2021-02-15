# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/progression_styles/stage_switcher_model.py
from frameworks.wulf import ViewModel

class StageSwitcherModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=2, commands=1):
        super(StageSwitcherModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getSelectedLevel(self):
        return self._getNumber(1)

    def setSelectedLevel(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(StageSwitcherModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('selectedLevel', 0)
        self.onChange = self._addCommand('onChange')
