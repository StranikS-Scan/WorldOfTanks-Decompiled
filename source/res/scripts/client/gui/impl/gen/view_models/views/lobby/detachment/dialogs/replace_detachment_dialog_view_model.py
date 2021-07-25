# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/replace_detachment_dialog_view_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ReplaceDetachmentDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=3):
        super(ReplaceDetachmentDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getFullBufferAmount(self):
        return self._getNumber(11)

    def setFullBufferAmount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(ReplaceDetachmentDialogViewModel, self)._initialize()
        self._addNumberProperty('fullBufferAmount', 100)
