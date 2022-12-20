# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/top_panel/top_panel_tabs_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TabID(IntEnum):
    NONE = 0
    VEHICLE = 1
    STYLE = 2
    BASE_VEHICLE = 3
    PERSONAL_NUMBER_VEHICLE = 4


class TopPanelTabsModel(ViewModel):
    __slots__ = ('onTabChanged',)

    def __init__(self, properties=3, commands=1):
        super(TopPanelTabsModel, self).__init__(properties=properties, commands=commands)

    def getTabIDs(self):
        return self._getArray(0)

    def setTabIDs(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTabIDsType():
        return TabID

    def getTabCustomNames(self):
        return self._getArray(1)

    def setTabCustomNames(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTabCustomNamesType():
        return unicode

    def getCurrentTabID(self):
        return TabID(self._getNumber(2))

    def setCurrentTabID(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(TopPanelTabsModel, self)._initialize()
        self._addArrayProperty('tabIDs', Array())
        self._addArrayProperty('tabCustomNames', Array())
        self._addNumberProperty('currentTabID')
        self.onTabChanged = self._addCommand('onTabChanged')
