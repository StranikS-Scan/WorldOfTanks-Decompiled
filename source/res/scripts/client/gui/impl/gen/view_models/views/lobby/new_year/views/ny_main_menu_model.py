# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_main_menu_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel

class NyMainMenuModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onInfoBtnClick')

    def __init__(self, properties=3, commands=2):
        super(NyMainMenuModel, self).__init__(properties=properties, commands=commands)

    def getItemsMenu(self):
        return self._getArray(0)

    def setItemsMenu(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsMenuType():
        return NyMainMenuTabModel

    def getStartIndexMenu(self):
        return self._getNumber(1)

    def setStartIndexMenu(self, value):
        self._setNumber(1, value)

    def getIsExtendedAnim(self):
        return self._getBool(2)

    def setIsExtendedAnim(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NyMainMenuModel, self)._initialize()
        self._addArrayProperty('itemsMenu', Array())
        self._addNumberProperty('startIndexMenu', 0)
        self._addBoolProperty('isExtendedAnim', False)
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onInfoBtnClick = self._addCommand('onInfoBtnClick')
