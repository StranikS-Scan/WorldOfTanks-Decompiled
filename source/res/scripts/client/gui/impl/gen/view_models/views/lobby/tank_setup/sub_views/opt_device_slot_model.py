# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/opt_device_slot_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specializations_model import SpecializationsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel

class OptDeviceSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=28, commands=0):
        super(OptDeviceSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(19)

    @staticmethod
    def getBonusesType():
        return BonusesModel

    @property
    def specializations(self):
        return self._getViewModel(20)

    @staticmethod
    def getSpecializationsType():
        return SpecializationsModel

    def getWithDescription(self):
        return self._getBool(21)

    def setWithDescription(self, value):
        self._setBool(21, value)

    def getIsTrophy(self):
        return self._getBool(22)

    def setIsTrophy(self, value):
        self._setBool(22, value)

    def getIsModernized(self):
        return self._getBool(23)

    def setIsModernized(self, value):
        self._setBool(23, value)

    def getIsUpgradable(self):
        return self._getBool(24)

    def setIsUpgradable(self, value):
        self._setBool(24, value)

    def getEffect(self):
        return self._getResource(25)

    def setEffect(self, value):
        self._setResource(25, value)

    def getLevel(self):
        return self._getNumber(26)

    def setLevel(self, value):
        self._setNumber(26, value)

    def getActiveSpecsMask(self):
        return self._getNumber(27)

    def setActiveSpecsMask(self, value):
        self._setNumber(27, value)

    def _initialize(self):
        super(OptDeviceSlotModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addViewModelProperty('specializations', SpecializationsModel())
        self._addBoolProperty('withDescription', False)
        self._addBoolProperty('isTrophy', False)
        self._addBoolProperty('isModernized', False)
        self._addBoolProperty('isUpgradable', False)
        self._addResourceProperty('effect', R.invalid())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('activeSpecsMask', 0)
