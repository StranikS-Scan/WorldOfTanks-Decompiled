# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/opt_device_slot_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specializations_model import SpecializationsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel

class OptDeviceSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(OptDeviceSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(13)

    @property
    def specializations(self):
        return self._getViewModel(14)

    def getWithDescription(self):
        return self._getBool(15)

    def setWithDescription(self, value):
        self._setBool(15, value)

    def getIsTrophy(self):
        return self._getBool(16)

    def setIsTrophy(self, value):
        self._setBool(16, value)

    def getIsUpgradable(self):
        return self._getBool(17)

    def setIsUpgradable(self, value):
        self._setBool(17, value)

    def getEffect(self):
        return self._getResource(18)

    def setEffect(self, value):
        self._setResource(18, value)

    def getActiveSpecsMask(self):
        return self._getNumber(19)

    def setActiveSpecsMask(self, value):
        self._setNumber(19, value)

    def _initialize(self):
        super(OptDeviceSlotModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addViewModelProperty('specializations', SpecializationsModel())
        self._addBoolProperty('withDescription', False)
        self._addBoolProperty('isTrophy', False)
        self._addBoolProperty('isUpgradable', False)
        self._addResourceProperty('effect', R.invalid())
        self._addNumberProperty('activeSpecsMask', 0)
