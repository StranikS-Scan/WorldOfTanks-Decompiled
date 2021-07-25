# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/train_vehicle_confirm_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_info_animated_model import DetachmentInfoAnimatedModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.buy_block_model import BuyBlockModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.train_slot_model import TrainSlotModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class TrainVehicleConfirmViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onSelectionChanged', 'onNotResetChanged')
    TRAIN = 'train'
    CHANGE = 'change'
    RETRAIN = 'retrain'

    def __init__(self, properties=21, commands=5):
        super(TrainVehicleConfirmViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(11)

    @property
    def prevVehicle(self):
        return self._getViewModel(12)

    @property
    def slots(self):
        return self._getViewModel(13)

    @property
    def detachmentInfo(self):
        return self._getViewModel(14)

    @property
    def blocks(self):
        return self._getViewModel(15)

    def getOperationType(self):
        return self._getString(16)

    def setOperationType(self, value):
        self._setString(16, value)

    def getSelectedBlock(self):
        return self._getString(17)

    def setSelectedBlock(self, value):
        self._setString(17, value)

    def getPercentExp(self):
        return self._getNumber(18)

    def setPercentExp(self, value):
        self._setNumber(18, value)

    def getIsReset(self):
        return self._getBool(19)

    def setIsReset(self, value):
        self._setBool(19, value)

    def getIsTrainToPremium(self):
        return self._getBool(20)

    def setIsTrainToPremium(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(TrainVehicleConfirmViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('prevVehicle', VehicleModel())
        self._addViewModelProperty('slots', UserListModel())
        self._addViewModelProperty('detachmentInfo', DetachmentInfoAnimatedModel())
        self._addViewModelProperty('blocks', UserListModel())
        self._addStringProperty('operationType', '')
        self._addStringProperty('selectedBlock', '')
        self._addNumberProperty('percentExp', 0)
        self._addBoolProperty('isReset', False)
        self._addBoolProperty('isTrainToPremium', False)
        self.onSelectionChanged = self._addCommand('onSelectionChanged')
        self.onNotResetChanged = self._addCommand('onNotResetChanged')
