# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/sidebar_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.tab_model import TabModel

class SidebarModel(ViewModel):
    __slots__ = ('onSideBarTabChange',)

    def __init__(self, properties=1, commands=1):
        super(SidebarModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return TabModel

    def _initialize(self):
        super(SidebarModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self.onSideBarTabChange = self._addCommand('onSideBarTabChange')
