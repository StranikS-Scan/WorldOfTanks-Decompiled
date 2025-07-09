# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dismiss_or_restore_dialog_model.py
from enum import Enum
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class DialogType(Enum):
    DISMISS = 'dismiss'
    RESTORE = 'restore'


class DismissOrRestoreDialogModel(DialogTemplateViewModel):
    __slots__ = ('onChangeCaptcha',)

    def __init__(self, properties=11, commands=3):
        super(DismissOrRestoreDialogModel, self).__init__(properties=properties, commands=commands)

    def getTankmans(self):
        return self._getNumber(6)

    def setTankmans(self, value):
        self._setNumber(6, value)

    def getTankmansWithPerk(self):
        return self._getNumber(7)

    def setTankmansWithPerk(self, value):
        self._setNumber(7, value)

    def getDisabled(self):
        return self._getBool(8)

    def setDisabled(self, value):
        self._setBool(8, value)

    def getDialogType(self):
        return DialogType(self._getString(9))

    def setDialogType(self, value):
        self._setString(9, value.value)

    def getLimitOverCount(self):
        return self._getNumber(10)

    def setLimitOverCount(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(DismissOrRestoreDialogModel, self)._initialize()
        self._addNumberProperty('tankmans', 0)
        self._addNumberProperty('tankmansWithPerk', 0)
        self._addBoolProperty('disabled', False)
        self._addStringProperty('dialogType')
        self._addNumberProperty('limitOverCount', 0)
        self.onChangeCaptcha = self._addCommand('onChangeCaptcha')
