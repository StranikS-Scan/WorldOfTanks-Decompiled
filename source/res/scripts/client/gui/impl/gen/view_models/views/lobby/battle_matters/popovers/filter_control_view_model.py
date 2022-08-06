# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/popovers/filter_control_view_model.py
from frameworks.wulf import ViewModel

class FilterControlViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FilterControlViewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(FilterControlViewModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBoolProperty('isSelected', False)
