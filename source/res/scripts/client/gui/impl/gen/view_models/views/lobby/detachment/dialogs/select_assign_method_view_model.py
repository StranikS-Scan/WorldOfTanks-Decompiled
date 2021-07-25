# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/select_assign_method_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.vehicle_slot_model import VehicleSlotModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class SelectAssignMethodViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onSlotClick',)

    def __init__(self, properties=14, commands=4):
        super(SelectAssignMethodViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedCardIndex(self):
        return self._getReal(11)

    def setSelectedCardIndex(self, value):
        self._setReal(11, value)

    def getCurrentVehicleName(self):
        return self._getString(12)

    def setCurrentVehicleName(self, value):
        self._setString(12, value)

    def getVehicleSlotList(self):
        return self._getArray(13)

    def setVehicleSlotList(self, value):
        self._setArray(13, value)

    def _initialize(self):
        super(SelectAssignMethodViewModel, self)._initialize()
        self._addRealProperty('selectedCardIndex', -1)
        self._addStringProperty('currentVehicleName', '')
        self._addArrayProperty('vehicleSlotList', Array())
        self.onSlotClick = self._addCommand('onSlotClick')
