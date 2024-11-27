# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/ny_main_menu_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import NewYearMainWidgetModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel

class NyMainMenuModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onInfoBtnClick')

    def __init__(self, properties=4, commands=2):
        super(NyMainMenuModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(0)

    @staticmethod
    def getWidgetType():
        return NewYearMainWidgetModel

    def getItemsMenu(self):
        return self._getArray(1)

    def setItemsMenu(self, value):
        self._setArray(1, value)

    @staticmethod
    def getItemsMenuType():
        return NyMainMenuTabModel

    def getStartIndexMenu(self):
        return self._getNumber(2)

    def setStartIndexMenu(self, value):
        self._setNumber(2, value)

    def getIsExtendedAnim(self):
        return self._getBool(3)

    def setIsExtendedAnim(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyMainMenuModel, self)._initialize()
        self._addViewModelProperty('widget', NewYearMainWidgetModel())
        self._addArrayProperty('itemsMenu', Array())
        self._addNumberProperty('startIndexMenu', 0)
        self._addBoolProperty('isExtendedAnim', False)
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onInfoBtnClick = self._addCommand('onInfoBtnClick')
