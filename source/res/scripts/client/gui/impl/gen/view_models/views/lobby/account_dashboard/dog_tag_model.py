# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/dog_tag_model.py
from frameworks.wulf import ViewModel

class DogTagModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(DogTagModel, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(0)

    def setIsSelected(self, value):
        self._setBool(0, value)

    def getIsHighlighted(self):
        return self._getBool(1)

    def setIsHighlighted(self, value):
        self._setBool(1, value)

    def getBackground(self):
        return self._getString(2)

    def setBackground(self, value):
        self._setString(2, value)

    def getEngraving(self):
        return self._getString(3)

    def setEngraving(self, value):
        self._setString(3, value)

    def getCounter(self):
        return self._getNumber(4)

    def setCounter(self, value):
        self._setNumber(4, value)

    def getIsEmptyCounter(self):
        return self._getBool(5)

    def setIsEmptyCounter(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(DogTagModel, self)._initialize()
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isHighlighted', False)
        self._addStringProperty('background', '')
        self._addStringProperty('engraving', '')
        self._addNumberProperty('counter', -1)
        self._addBoolProperty('isEmptyCounter', False)
        self.onClick = self._addCommand('onClick')
