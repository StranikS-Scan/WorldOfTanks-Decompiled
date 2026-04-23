# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_tabs_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_tab_item_model import CustomizationTabItemModel

class CustomizationTabsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CustomizationTabsModel, self).__init__(properties=properties, commands=commands)

    def getTabItemsList(self):
        return self._getArray(0)

    def setTabItemsList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTabItemsListType():
        return CustomizationTabItemModel

    def _initialize(self):
        super(CustomizationTabsModel, self)._initialize()
        self._addArrayProperty('tabItemsList', Array())
