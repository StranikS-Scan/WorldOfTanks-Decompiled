# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_sidebar_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NySidebarModel(ViewModel):
    __slots__ = ('onSideBarBtnClick',)
    VIEW_NAME_GLADE = 'glade'
    VIEW_NAME_REWARDS = 'rewards'
    VIEW_NAME_COLLECTIONS = 'collections'

    def __init__(self, properties=3, commands=1):
        super(NySidebarModel, self).__init__(properties=properties, commands=commands)

    def getItemsTabBar(self):
        return self._getArray(0)

    def setItemsTabBar(self, value):
        self._setArray(0, value)

    def getStartIndex(self):
        return self._getNumber(1)

    def setStartIndex(self, value):
        self._setNumber(1, value)

    def getViewName(self):
        return self._getString(2)

    def setViewName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NySidebarModel, self)._initialize()
        self._addArrayProperty('itemsTabBar', Array())
        self._addNumberProperty('startIndex', 0)
        self._addStringProperty('viewName', '')
        self.onSideBarBtnClick = self._addCommand('onSideBarBtnClick')
