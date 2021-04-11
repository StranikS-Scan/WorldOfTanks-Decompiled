# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/field_separate_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FieldSeparateModel(ViewModel):
    __slots__ = ('onCleanError',)

    def __init__(self, properties=3, commands=1):
        super(FieldSeparateModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getErrorMessage(self):
        return self._getResource(1)

    def setErrorMessage(self, value):
        self._setResource(1, value)

    def getFieldNum(self):
        return self._getNumber(2)

    def setFieldNum(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FieldSeparateModel, self)._initialize()
        self._addStringProperty('value', '')
        self._addResourceProperty('errorMessage', R.invalid())
        self._addNumberProperty('fieldNum', 4)
        self.onCleanError = self._addCommand('onCleanError')
