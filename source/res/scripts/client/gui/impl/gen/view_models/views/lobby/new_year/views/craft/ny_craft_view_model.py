# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_view_model.py
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_antiduplicator_model import NyCraftAntiduplicatorModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_mega_device_model import NyCraftMegaDeviceModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_monitor_model import NyCraftMonitorModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_regular_config_model import NyCraftRegularConfigModel

class NyCraftViewModel(NyWithRomanNumbersModel):
    __slots__ = ('onCraftBtnClick', 'onAddCraftDecoration')

    def __init__(self, properties=14, commands=2):
        super(NyCraftViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def craftCarousel(self):
        return self._getViewModel(1)

    @property
    def regularConfig(self):
        return self._getViewModel(2)

    @property
    def megaDevice(self):
        return self._getViewModel(3)

    @property
    def antiduplicator(self):
        return self._getViewModel(4)

    @property
    def monitor(self):
        return self._getViewModel(5)

    def getEnableCraftBtn(self):
        return self._getBool(6)

    def setEnableCraftBtn(self, value):
        self._setBool(6, value)

    def getCraftPrice(self):
        return self._getNumber(7)

    def setCraftPrice(self, value):
        self._setNumber(7, value)

    def getHasShards(self):
        return self._getBool(8)

    def setHasShards(self, value):
        self._setBool(8, value)

    def getAtmospherePoints(self):
        return self._getNumber(9)

    def setAtmospherePoints(self, value):
        self._setNumber(9, value)

    def getCraftIconName(self):
        return self._getString(10)

    def setCraftIconName(self, value):
        self._setString(10, value)

    def getIsCrafting(self):
        return self._getBool(11)

    def setIsCrafting(self, value):
        self._setBool(11, value)

    def getCraftState(self):
        return self._getNumber(12)

    def setCraftState(self, value):
        self._setNumber(12, value)

    def getRealm(self):
        return self._getString(13)

    def setRealm(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(NyCraftViewModel, self)._initialize()
        self._addViewModelProperty('craftCarousel', ListModel())
        self._addViewModelProperty('regularConfig', NyCraftRegularConfigModel())
        self._addViewModelProperty('megaDevice', NyCraftMegaDeviceModel())
        self._addViewModelProperty('antiduplicator', NyCraftAntiduplicatorModel())
        self._addViewModelProperty('monitor', NyCraftMonitorModel())
        self._addBoolProperty('enableCraftBtn', False)
        self._addNumberProperty('craftPrice', 0)
        self._addBoolProperty('hasShards', False)
        self._addNumberProperty('atmospherePoints', 0)
        self._addStringProperty('craftIconName', '')
        self._addBoolProperty('isCrafting', False)
        self._addNumberProperty('craftState', -1)
        self._addStringProperty('realm', '')
        self.onCraftBtnClick = self._addCommand('onCraftBtnClick')
        self.onAddCraftDecoration = self._addCommand('onAddCraftDecoration')
