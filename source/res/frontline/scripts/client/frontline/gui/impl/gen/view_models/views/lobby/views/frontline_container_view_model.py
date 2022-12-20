# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/frontline_container_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import FrontlineContainerTabModel

class FrontlineContainerViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(FrontlineContainerViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentTabId(self):
        return self._getNumber(0)

    def setCurrentTabId(self, value):
        self._setNumber(0, value)

    def getIsTopSubView(self):
        return self._getBool(1)

    def setIsTopSubView(self, value):
        self._setBool(1, value)

    def getTabs(self):
        return self._getArray(2)

    def setTabs(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTabsType():
        return FrontlineContainerTabModel

    def _initialize(self):
        super(FrontlineContainerViewModel, self)._initialize()
        self._addNumberProperty('currentTabId', 0)
        self._addBoolProperty('isTopSubView', False)
        self._addArrayProperty('tabs', Array())
        self.onTabChange = self._addCommand('onTabChange')
        self.onClose = self._addCommand('onClose')
