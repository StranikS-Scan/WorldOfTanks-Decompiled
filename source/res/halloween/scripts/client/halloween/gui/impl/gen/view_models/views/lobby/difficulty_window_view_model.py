# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/difficulty_window_view_model.py
from frameworks.wulf import ViewModel

class DifficultyWindowViewModel(ViewModel):
    __slots__ = ('onClose', 'onToAnomalies')

    def __init__(self, properties=2, commands=2):
        super(DifficultyWindowViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getHasNewRecipes(self):
        return self._getBool(1)

    def setHasNewRecipes(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(DifficultyWindowViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('hasNewRecipes', False)
        self.onClose = self._addCommand('onClose')
        self.onToAnomalies = self._addCommand('onToAnomalies')
