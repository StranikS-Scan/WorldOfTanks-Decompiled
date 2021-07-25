# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/demobilize_detachment_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_base_model import DetachmentBaseModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class DemobilizeDetachmentDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onInputChange',)
    INPUT_STATE_CORRECT = 'inputCorrect'
    INPUT_STATE_INCORRECT = 'inputIncorrect'
    INPUT_STATE_DEFAULT = ''

    def __init__(self, properties=19, commands=4):
        super(DemobilizeDetachmentDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentLine(self):
        return self._getViewModel(11)

    def getCanRestore(self):
        return self._getBool(12)

    def setCanRestore(self, value):
        self._setBool(12, value)

    def getRestoreDaysLimit(self):
        return self._getNumber(13)

    def setRestoreDaysLimit(self, value):
        self._setNumber(13, value)

    def getInputState(self):
        return self._getString(14)

    def setInputState(self, value):
        self._setString(14, value)

    def getIsInstructorsAvailable(self):
        return self._getBool(15)

    def setIsInstructorsAvailable(self, value):
        self._setBool(15, value)

    def getIsSkin(self):
        return self._getBool(16)

    def setIsSkin(self, value):
        self._setBool(16, value)

    def getIsFullBuffer(self):
        return self._getBool(17)

    def setIsFullBuffer(self, value):
        self._setBool(17, value)

    def getIsLowLevelDetachment(self):
        return self._getBool(18)

    def setIsLowLevelDetachment(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(DemobilizeDetachmentDialogViewModel, self)._initialize()
        self._addViewModelProperty('detachmentLine', DetachmentBaseModel())
        self._addBoolProperty('canRestore', False)
        self._addNumberProperty('restoreDaysLimit', 0)
        self._addStringProperty('inputState', '')
        self._addBoolProperty('isInstructorsAvailable', False)
        self._addBoolProperty('isSkin', False)
        self._addBoolProperty('isFullBuffer', False)
        self._addBoolProperty('isLowLevelDetachment', False)
        self.onInputChange = self._addCommand('onInputChange')
