# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/gf_drop_down_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem

class GfDropDownModel(ViewModel):
    __slots__ = ('onChange',)

    def __init__(self, properties=3, commands=1):
        super(GfDropDownModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return GfDropDownItem

    def getSelected(self):
        return self._getArray(1)

    def setSelected(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSelectedType():
        return str

    def getMultiple(self):
        return self._getBool(2)

    def setMultiple(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(GfDropDownModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addArrayProperty('selected', Array())
        self._addBoolProperty('multiple', False)
        self.onChange = self._addCommand('onChange')
