# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_regular_config_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_tab_type_model import NyCraftTabTypeModel

class CraftSwitcherOrder(IntEnum):
    RANDOM = 0
    NEWYEAR = 1
    CHRISTMAS = 2
    ORIENTAL = 3
    FAIRYTALE = 4


class NyCraftRegularConfigModel(ViewModel):
    __slots__ = ('onSettingChanged', 'onTypeChanged')
    LEVEL = 0
    SETTING = 1
    TYPE = 2

    def __init__(self, properties=8, commands=2):
        super(NyCraftRegularConfigModel, self).__init__(properties=properties, commands=commands)

    def getCurrentSettingIndex(self):
        return self._getNumber(0)

    def setCurrentSettingIndex(self, value):
        self._setNumber(0, value)

    def getCurrentLevelIndex(self):
        return self._getNumber(1)

    def setCurrentLevelIndex(self, value):
        self._setNumber(1, value)

    def getSelectedType(self):
        return self._getString(2)

    def setSelectedType(self, value):
        self._setString(2, value)

    def getCurrentCategory(self):
        return self._getString(3)

    def setCurrentCategory(self, value):
        self._setString(3, value)

    def getTabsTypes(self):
        return self._getArray(4)

    def setTabsTypes(self, value):
        self._setArray(4, value)

    def getState(self):
        return self._getString(5)

    def setState(self, value):
        self._setString(5, value)

    def getEnabled(self):
        return self._getBool(6)

    def setEnabled(self, value):
        self._setBool(6, value)

    def getFillerShardsCost(self):
        return self._getNumber(7)

    def setFillerShardsCost(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NyCraftRegularConfigModel, self)._initialize()
        self._addNumberProperty('currentSettingIndex', 0)
        self._addNumberProperty('currentLevelIndex', 0)
        self._addStringProperty('selectedType', 'random')
        self._addStringProperty('currentCategory', 'random')
        self._addArrayProperty('tabsTypes', Array())
        self._addStringProperty('state', '')
        self._addBoolProperty('enabled', True)
        self._addNumberProperty('fillerShardsCost', 0)
        self.onSettingChanged = self._addCommand('onSettingChanged')
        self.onTypeChanged = self._addCommand('onTypeChanged')
