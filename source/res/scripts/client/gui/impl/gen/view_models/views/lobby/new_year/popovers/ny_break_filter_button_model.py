# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_break_filter_button_model.py
from frameworks.wulf import ViewModel

class NyBreakFilterButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyBreakFilterButtonModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyBreakFilterButtonModel, self)._initialize()
        self._addStringProperty('label', '')
        self._addBoolProperty('isSelected', False)
