# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/field_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FieldModel(ViewModel):
    __slots__ = ('onCleanError',)
    TYPE_NAME = 'Name'
    TYPE_EMAIL = 'Email'
    TYPE_CODE = 'Code'
    VALUE_LEN_MAX = 50

    def __init__(self, properties=6, commands=1):
        super(FieldModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getPlaceholder(self):
        return self._getResource(2)

    def setPlaceholder(self, value):
        self._setResource(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getErrorMessage(self):
        return self._getResource(4)

    def setErrorMessage(self, value):
        self._setResource(4, value)

    def getErrorTime(self):
        return self._getNumber(5)

    def setErrorTime(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(FieldModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addStringProperty('value', '')
        self._addResourceProperty('placeholder', R.invalid())
        self._addStringProperty('type', '')
        self._addResourceProperty('errorMessage', R.invalid())
        self._addNumberProperty('errorTime', 0)
        self.onCleanError = self._addCommand('onCleanError')
