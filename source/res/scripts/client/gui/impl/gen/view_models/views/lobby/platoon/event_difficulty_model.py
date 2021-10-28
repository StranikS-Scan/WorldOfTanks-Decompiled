# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/event_difficulty_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.difficulty_dropdown_item_model import DifficultyDropdownItemModel

class EventDifficultyModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=5, commands=1):
        super(EventDifficultyModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    def getSelected(self):
        return self._getArray(1)

    def setSelected(self, value):
        self._setArray(1, value)

    def getTooltipDifficulty(self):
        return self._getString(2)

    def setTooltipDifficulty(self, value):
        self._setString(2, value)

    def getTooltipDifficultyHeader(self):
        return self._getString(3)

    def setTooltipDifficultyHeader(self, value):
        self._setString(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EventDifficultyModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addArrayProperty('selected', Array())
        self._addStringProperty('tooltipDifficulty', '')
        self._addStringProperty('tooltipDifficultyHeader', '')
        self._addNumberProperty('level', 0)
        self.onChange = self._addCommand('onChange')
