# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_regular_config_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_tab_type_model import NyCraftTabTypeModel

class CollectionIndex(IntEnum):
    RANDOM = 0
    NEWYEAR = 1
    CHRISTMAS = 2
    ORIENTAL = 3
    FAIRYTALE = 4


class NyCraftRegularConfigModel(ViewModel):
    __slots__ = ('onSettingChanged', 'onLevelChanged', 'onTypeChanged')
    LEVEL = 0
    SETTING = 1
    TYPE = 2

    def __init__(self, properties=8, commands=3):
        super(NyCraftRegularConfigModel, self).__init__(properties=properties, commands=commands)

    def getSelectedCollectionIndex(self):
        return self._getNumber(0)

    def setSelectedCollectionIndex(self, value):
        self._setNumber(0, value)

    def getCurrentToyLevelIndex(self):
        return self._getNumber(1)

    def setCurrentToyLevelIndex(self, value):
        self._setNumber(1, value)

    def getSelectedToyType(self):
        return self._getString(2)

    def setSelectedToyType(self, value):
        self._setString(2, value)

    def getCurrentToyCategory(self):
        return self._getString(3)

    def setCurrentToyCategory(self, value):
        self._setString(3, value)

    def getTabsTypes(self):
        return self._getArray(4)

    def setTabsTypes(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTabsTypesType():
        return NyCraftTabTypeModel

    def getState(self):
        return self._getString(5)

    def setState(self, value):
        self._setString(5, value)

    def getIsEnabled(self):
        return self._getBool(6)

    def setIsEnabled(self, value):
        self._setBool(6, value)

    def getFillerShardsCost(self):
        return self._getNumber(7)

    def setFillerShardsCost(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NyCraftRegularConfigModel, self)._initialize()
        self._addNumberProperty('selectedCollectionIndex', 0)
        self._addNumberProperty('currentToyLevelIndex', 0)
        self._addStringProperty('selectedToyType', 'random')
        self._addStringProperty('currentToyCategory', 'random')
        self._addArrayProperty('tabsTypes', Array())
        self._addStringProperty('state', '')
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('fillerShardsCost', 0)
        self.onSettingChanged = self._addCommand('onSettingChanged')
        self.onLevelChanged = self._addCommand('onLevelChanged')
        self.onTypeChanged = self._addCommand('onTypeChanged')
