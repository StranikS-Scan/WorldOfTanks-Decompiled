# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/progression_button_model.py
from frameworks.wulf import ViewModel

class ProgressionButtonModel(ViewModel):
    __slots__ = ('onProgressionButtonClick',)

    def __init__(self, properties=2, commands=1):
        super(ProgressionButtonModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(0)

    def setIsNew(self, value):
        self._setBool(0, value)

    def getIsHighlighted(self):
        return self._getBool(1)

    def setIsHighlighted(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ProgressionButtonModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isHighlighted', False)
        self.onProgressionButtonClick = self._addCommand('onProgressionButtonClick')
