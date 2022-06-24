# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/select_slot_spec_dialog_content_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_slot_model import SelectSlotSpecDialogSlotModel
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_spec_model import SelectSlotSpecDialogSpecModel

class SelectSlotSpecDialogContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SelectSlotSpecDialogContentModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getSlots(self):
        return self._getArray(1)

    def setSlots(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSlotsType():
        return SelectSlotSpecDialogSlotModel

    def getTargetSlotIdx(self):
        return self._getNumber(2)

    def setTargetSlotIdx(self, value):
        self._setNumber(2, value)

    def getAvailableSpecs(self):
        return self._getArray(3)

    def setAvailableSpecs(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAvailableSpecsType():
        return SelectSlotSpecDialogSpecModel

    def getSelectedSpecIdx(self):
        return self._getNumber(4)

    def setSelectedSpecIdx(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(SelectSlotSpecDialogContentModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addArrayProperty('slots', Array())
        self._addNumberProperty('targetSlotIdx', 0)
        self._addArrayProperty('availableSpecs', Array())
        self._addNumberProperty('selectedSpecIdx', -1)
