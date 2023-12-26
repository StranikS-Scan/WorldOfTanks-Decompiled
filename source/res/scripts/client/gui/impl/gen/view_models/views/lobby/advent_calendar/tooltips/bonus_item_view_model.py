# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/tooltips/bonus_item_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BonusItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BonusItemViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getArray(1)

    def setValue(self, value):
        self._setArray(1, value)

    @staticmethod
    def getValueType():
        return unicode

    def getIconName(self):
        return self._getString(2)

    def setIconName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BonusItemViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addArrayProperty('value', Array())
        self._addStringProperty('iconName', '')
