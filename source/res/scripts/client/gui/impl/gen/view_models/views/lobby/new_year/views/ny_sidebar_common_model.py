# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_sidebar_common_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel

class NySidebarCommonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NySidebarCommonModel, self).__init__(properties=properties, commands=commands)

    def getItemsTabBar(self):
        return self._getArray(0)

    def setItemsTabBar(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsTabBarType():
        return NewYearTabModel

    def getStartIndex(self):
        return self._getNumber(1)

    def setStartIndex(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NySidebarCommonModel, self)._initialize()
        self._addArrayProperty('itemsTabBar', Array())
        self._addNumberProperty('startIndex', 0)
