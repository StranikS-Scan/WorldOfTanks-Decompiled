# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_view_model.py
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_antiduplicator_model import NyCraftAntiduplicatorModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_monitor_model import NyCraftMonitorModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_regular_config_model import NyCraftRegularConfigModel

class NyCraftViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onCraftBtnClick', 'onAddCraftDecoration', 'onSnowflakeAnimationEnd')

    def __init__(self, properties=12, commands=3):
        super(NyCraftViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def craftCarousel(self):
        return self._getViewModel(1)

    @staticmethod
    def getCraftCarouselType():
        return ListModel

    @property
    def regularConfig(self):
        return self._getViewModel(2)

    @staticmethod
    def getRegularConfigType():
        return NyCraftRegularConfigModel

    @property
    def antiduplicator(self):
        return self._getViewModel(3)

    @staticmethod
    def getAntiduplicatorType():
        return NyCraftAntiduplicatorModel

    @property
    def monitor(self):
        return self._getViewModel(4)

    @staticmethod
    def getMonitorType():
        return NyCraftMonitorModel

    def getEnableCraftBtn(self):
        return self._getBool(5)

    def setEnableCraftBtn(self, value):
        self._setBool(5, value)

    def getCraftPrice(self):
        return self._getNumber(6)

    def setCraftPrice(self, value):
        self._setNumber(6, value)

    def getHasShards(self):
        return self._getBool(7)

    def setHasShards(self, value):
        self._setBool(7, value)

    def getAtmospherePoints(self):
        return self._getNumber(8)

    def setAtmospherePoints(self, value):
        self._setNumber(8, value)

    def getCraftIconName(self):
        return self._getString(9)

    def setCraftIconName(self, value):
        self._setString(9, value)

    def getIsCrafting(self):
        return self._getBool(10)

    def setIsCrafting(self, value):
        self._setBool(10, value)

    def getCraftState(self):
        return self._getNumber(11)

    def setCraftState(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(NyCraftViewModel, self)._initialize()
        self._addViewModelProperty('craftCarousel', ListModel())
        self._addViewModelProperty('regularConfig', NyCraftRegularConfigModel())
        self._addViewModelProperty('antiduplicator', NyCraftAntiduplicatorModel())
        self._addViewModelProperty('monitor', NyCraftMonitorModel())
        self._addBoolProperty('enableCraftBtn', False)
        self._addNumberProperty('craftPrice', 0)
        self._addBoolProperty('hasShards', False)
        self._addNumberProperty('atmospherePoints', 0)
        self._addStringProperty('craftIconName', '')
        self._addBoolProperty('isCrafting', False)
        self._addNumberProperty('craftState', -1)
        self.onCraftBtnClick = self._addCommand('onCraftBtnClick')
        self.onAddCraftDecoration = self._addCommand('onAddCraftDecoration')
        self.onSnowflakeAnimationEnd = self._addCommand('onSnowflakeAnimationEnd')
