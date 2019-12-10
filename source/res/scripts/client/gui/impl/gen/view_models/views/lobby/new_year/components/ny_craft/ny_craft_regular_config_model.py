# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_craft/ny_craft_regular_config_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_craft.ny_craft_tab_type_item_model import NyCraftTabTypeItemModel

class NyCraftRegularConfigModel(ViewModel):
    __slots__ = ('onConfigChanged',)
    LEVEL = 0
    SETTING = 1
    TYPE = 2

    def __init__(self, properties=7, commands=1):
        super(NyCraftRegularConfigModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevelIndex(self):
        return self._getNumber(0)

    def setCurrentLevelIndex(self, value):
        self._setNumber(0, value)

    def getCurrentSettingIndex(self):
        return self._getNumber(1)

    def setCurrentSettingIndex(self, value):
        self._setNumber(1, value)

    def getCurrentTypeIndex(self):
        return self._getNumber(2)

    def setCurrentTypeIndex(self, value):
        self._setNumber(2, value)

    def getTabTypes(self):
        return self._getArray(3)

    def setTabTypes(self, value):
        self._setArray(3, value)

    def getTabGroupNames(self):
        return self._getArray(4)

    def setTabGroupNames(self, value):
        self._setArray(4, value)

    def getState(self):
        return self._getString(5)

    def setState(self, value):
        self._setString(5, value)

    def getEnabled(self):
        return self._getBool(6)

    def setEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyCraftRegularConfigModel, self)._initialize()
        self._addNumberProperty('currentLevelIndex', -1)
        self._addNumberProperty('currentSettingIndex', -1)
        self._addNumberProperty('currentTypeIndex', -1)
        self._addArrayProperty('tabTypes', Array())
        self._addArrayProperty('tabGroupNames', Array())
        self._addStringProperty('state', '')
        self._addBoolProperty('enabled', True)
        self.onConfigChanged = self._addCommand('onConfigChanged')
