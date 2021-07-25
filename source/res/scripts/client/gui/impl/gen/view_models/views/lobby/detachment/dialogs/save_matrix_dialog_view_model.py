# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/save_matrix_dialog_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.gen.view_models.windows.selector_dialog_model import SelectorDialogModel

class SaveMatrixDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()
    ADD = 'add'
    EDIT = 'edit'
    CLEAR_ALL = 'clearAll'
    EXIT_CONFIRM = 'exitConfirm'
    BLANK = 'blank'
    CREDITS = 'credits'

    def __init__(self, properties=18, commands=3):
        super(SaveMatrixDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selector(self):
        return self._getViewModel(11)

    def getOperationType(self):
        return self._getString(12)

    def setOperationType(self, value):
        self._setString(12, value)

    def getIsOperationChargeable(self):
        return self._getBool(13)

    def setIsOperationChargeable(self, value):
        self._setBool(13, value)

    def getIsChargeableOperationFreeByDiscount(self):
        return self._getBool(14)

    def setIsChargeableOperationFreeByDiscount(self, value):
        self._setBool(14, value)

    def getPoints(self):
        return self._getNumber(15)

    def setPoints(self, value):
        self._setNumber(15, value)

    def getDiscountMessage(self):
        return self._getString(16)

    def setDiscountMessage(self, value):
        self._setString(16, value)

    def getPerksList(self):
        return self._getArray(17)

    def setPerksList(self, value):
        self._setArray(17, value)

    def _initialize(self):
        super(SaveMatrixDialogViewModel, self)._initialize()
        self._addViewModelProperty('selector', SelectorDialogModel())
        self._addStringProperty('operationType', '')
        self._addBoolProperty('isOperationChargeable', False)
        self._addBoolProperty('isChargeableOperationFreeByDiscount', False)
        self._addNumberProperty('points', 0)
        self._addStringProperty('discountMessage', '')
        self._addArrayProperty('perksList', Array())
