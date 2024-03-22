# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/sidebar_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.clan_supply.tab_model import TabModel

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
