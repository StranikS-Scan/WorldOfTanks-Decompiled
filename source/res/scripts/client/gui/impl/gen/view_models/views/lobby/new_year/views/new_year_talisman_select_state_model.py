# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_talisman_select_state_model.py
from frameworks.wulf import ViewModel

class NewYearTalismanSelectStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NewYearTalismanSelectStateModel, self).__init__(properties=properties, commands=commands)

    def getTalismanType(self):
        return self._getString(0)

    def setTalismanType(self, value):
        self._setString(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NewYearTalismanSelectStateModel, self)._initialize()
        self._addStringProperty('talismanType', '')
        self._addBoolProperty('isSelected', False)
