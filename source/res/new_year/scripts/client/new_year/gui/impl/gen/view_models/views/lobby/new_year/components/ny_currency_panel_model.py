# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/ny_currency_panel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_currency_panel_item_model import NyCurrencyPanelItemModel

class NyCurrencyPanelModel(ViewModel):
    __slots__ = ('onItemClick',)

    def __init__(self, properties=1, commands=1):
        super(NyCurrencyPanelModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return NyCurrencyPanelItemModel

    def _initialize(self):
        super(NyCurrencyPanelModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self.onItemClick = self._addCommand('onItemClick')
