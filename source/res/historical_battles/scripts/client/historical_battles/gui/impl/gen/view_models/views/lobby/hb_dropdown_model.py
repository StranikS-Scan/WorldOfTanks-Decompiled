# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_dropdown_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_dropdown_item import HbDropdownItem

class HbDropdownModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=4, commands=1):
        super(HbDropdownModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return HbDropdownItem

    def getSelectedLabel(self):
        return self._getResource(1)

    def setSelectedLabel(self, value):
        self._setResource(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getSelectedId(self):
        return self._getString(3)

    def setSelectedId(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(HbDropdownModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addResourceProperty('selectedLabel', R.invalid())
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('selectedId', '')
        self.onChange = self._addCommand('onChange')
