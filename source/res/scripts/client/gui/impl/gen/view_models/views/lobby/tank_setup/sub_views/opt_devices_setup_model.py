# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/opt_devices_setup_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_filter_model import OptDeviceFilterModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.special_currency_model import SpecialCurrencyModel

class OptDevicesSetupModel(BaseSetupModel):
    __slots__ = ('onIntroPassed',)

    def __init__(self, properties=11, commands=8):
        super(OptDevicesSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def filter(self):
        return self._getViewModel(5)

    @staticmethod
    def getFilterType():
        return OptDeviceFilterModel

    @property
    def specialCurrency(self):
        return self._getViewModel(6)

    @staticmethod
    def getSpecialCurrencyType():
        return SpecialCurrencyModel

    def getHasUnfitItems(self):
        return self._getBool(7)

    def setHasUnfitItems(self, value):
        self._setBool(7, value)

    def getSlots(self):
        return self._getArray(8)

    def setSlots(self, value):
        self._setArray(8, value)

    @staticmethod
    def getSlotsType():
        return OptDeviceSlotModel

    def getWithIntroduction(self):
        return self._getBool(9)

    def setWithIntroduction(self, value):
        self._setBool(9, value)

    def getIntroductionType(self):
        return self._getString(10)

    def setIntroductionType(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(OptDevicesSetupModel, self)._initialize()
        self._addViewModelProperty('filter', OptDeviceFilterModel())
        self._addViewModelProperty('specialCurrency', SpecialCurrencyModel())
        self._addBoolProperty('hasUnfitItems', False)
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('withIntroduction', False)
        self._addStringProperty('introductionType', '')
        self.onIntroPassed = self._addCommand('onIntroPassed')
