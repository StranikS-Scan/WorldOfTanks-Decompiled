# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/opt_devices_setup_model.py
from frameworks.wulf import Array
from gui.impl.wrappers.user_hints_model import UserHintsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_filter_model import OptDeviceFilterModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel

class OptDevicesSetupModel(BaseSetupModel):
    __slots__ = ('onIntroPassed',)

    def __init__(self, properties=10, commands=9):
        super(OptDevicesSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def filter(self):
        return self._getViewModel(5)

    @property
    def hints(self):
        return self._getViewModel(6)

    def getSlots(self):
        return self._getArray(7)

    def setSlots(self, value):
        self._setArray(7, value)

    def getWithIntroduction(self):
        return self._getBool(8)

    def setWithIntroduction(self, value):
        self._setBool(8, value)

    def getIntroductionType(self):
        return self._getString(9)

    def setIntroductionType(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(OptDevicesSetupModel, self)._initialize()
        self._addViewModelProperty('filter', OptDeviceFilterModel())
        self._addViewModelProperty('hints', UserHintsModel())
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('withIntroduction', False)
        self._addStringProperty('introductionType', '')
        self.onIntroPassed = self._addCommand('onIntroPassed')
