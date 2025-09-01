# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/navigation_bar_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.page.header.navigation_bar_info_button import NavigationBarInfoButton

class NavigationBarModel(ViewModel):
    __slots__ = ('onNavigate', 'onInfoAction')
    BACK_NAVIGATION = 'back'
    GARAGE_NAVIGATION = 'garage'

    def __init__(self, properties=4, commands=2):
        super(NavigationBarModel, self).__init__(properties=properties, commands=commands)

    def getPageTitle(self):
        return self._getString(0)

    def setPageTitle(self, value):
        self._setString(0, value)

    def getBackNavigationDescription(self):
        return self._getString(1)

    def setBackNavigationDescription(self, value):
        self._setString(1, value)

    def getBackNavigationAllowed(self):
        return self._getBool(2)

    def setBackNavigationAllowed(self, value):
        self._setBool(2, value)

    def getInfoButtons(self):
        return self._getArray(3)

    def setInfoButtons(self, value):
        self._setArray(3, value)

    @staticmethod
    def getInfoButtonsType():
        return NavigationBarInfoButton

    def _initialize(self):
        super(NavigationBarModel, self)._initialize()
        self._addStringProperty('pageTitle', '')
        self._addStringProperty('backNavigationDescription', '')
        self._addBoolProperty('backNavigationAllowed', False)
        self._addArrayProperty('infoButtons', Array())
        self.onNavigate = self._addCommand('onNavigate')
        self.onInfoAction = self._addCommand('onInfoAction')
