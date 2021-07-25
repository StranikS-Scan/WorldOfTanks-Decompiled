# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/restore_detachment_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_base_model import DetachmentBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class RestoreDetachmentDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()
    PRICE_TOOLTIP = 'priceTooltip'

    def __init__(self, properties=14, commands=3):
        super(RestoreDetachmentDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentLine(self):
        return self._getViewModel(11)

    @property
    def price(self):
        return self._getViewModel(12)

    def getEndRestoreTime(self):
        return self._getNumber(13)

    def setEndRestoreTime(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(RestoreDetachmentDialogViewModel, self)._initialize()
        self._addViewModelProperty('detachmentLine', DetachmentBaseModel())
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('endRestoreTime', 0)
