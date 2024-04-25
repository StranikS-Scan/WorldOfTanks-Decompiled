# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_dropdown_item.py
from frameworks.wulf import ViewModel

class HbDropdownItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HbDropdownItem, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getString(1)

    def setLabel(self, value):
        self._setString(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(HbDropdownItem, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('label', '')
        self._addBoolProperty('isDisabled', False)
