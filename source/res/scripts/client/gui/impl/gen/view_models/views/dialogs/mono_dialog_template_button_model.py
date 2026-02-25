# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/mono_dialog_template_button_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class ButtonType(Enum):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    CUSTOM = 'custom'


class MonoDialogTemplateButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MonoDialogTemplateButtonModel, self).__init__(properties=properties, commands=commands)

    def getAction(self):
        return self._getString(0)

    def setAction(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getSoundTarget(self):
        return self._getString(2)

    def setSoundTarget(self, value):
        self._setString(2, value)

    def getIsDisabled(self):
        return self._getBool(3)

    def setIsDisabled(self, value):
        self._setBool(3, value)

    def getType(self):
        return ButtonType(self._getString(4))

    def setType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(MonoDialogTemplateButtonModel, self)._initialize()
        self._addStringProperty('action', '')
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('soundTarget', '')
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('type')
