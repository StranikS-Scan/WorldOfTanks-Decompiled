# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/difficulty_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import DifficultyItemModel

class DifficultyViewModel(ViewModel):
    __slots__ = ('onSwichLevel',)

    def __init__(self, properties=2, commands=1):
        super(DifficultyViewModel, self).__init__(properties=properties, commands=commands)

    def getDifficulties(self):
        return self._getArray(0)

    def setDifficulties(self, value):
        self._setArray(0, value)

    @staticmethod
    def getDifficultiesType():
        return DifficultyItemModel

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(DifficultyViewModel, self)._initialize()
        self._addArrayProperty('difficulties', Array())
        self._addBoolProperty('isDisabled', False)
        self.onSwichLevel = self._addCommand('onSwichLevel')
