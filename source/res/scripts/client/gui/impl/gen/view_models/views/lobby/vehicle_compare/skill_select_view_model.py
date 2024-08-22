# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/skill_select_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.skill_select_row_model import SkillSelectRowModel

class SkillSelectViewModel(ViewModel):
    __slots__ = ('onRestore', 'onCancel', 'onClose', 'onConfirm', 'onClick')

    def __init__(self, properties=4, commands=5):
        super(SkillSelectViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getMajorSkillRows(self):
        return self._getArray(1)

    def setMajorSkillRows(self, value):
        self._setArray(1, value)

    @staticmethod
    def getMajorSkillRowsType():
        return SkillSelectRowModel

    def getBonusSkillRows(self):
        return self._getArray(2)

    def setBonusSkillRows(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusSkillRowsType():
        return SkillSelectRowModel

    def getIsActionsDisable(self):
        return self._getBool(3)

    def setIsActionsDisable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SkillSelectViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addArrayProperty('majorSkillRows', Array())
        self._addArrayProperty('bonusSkillRows', Array())
        self._addBoolProperty('isActionsDisable', False)
        self.onRestore = self._addCommand('onRestore')
        self.onCancel = self._addCommand('onCancel')
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
        self.onClick = self._addCommand('onClick')
