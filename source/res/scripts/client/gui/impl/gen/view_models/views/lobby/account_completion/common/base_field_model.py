# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/base_field_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseFieldModel(ViewModel):
    __slots__ = ('onChange', 'onLostFocus')

    def __init__(self, properties=4, commands=2):
        super(BaseFieldModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getErrorMessage(self):
        return self._getString(2)

    def setErrorMessage(self, value):
        self._setString(2, value)

    def getPlaceholder(self):
        return self._getString(3)

    def setPlaceholder(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BaseFieldModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addStringProperty('value', '')
        self._addStringProperty('errorMessage', '')
        self._addStringProperty('placeholder', '')
        self.onChange = self._addCommand('onChange')
        self.onLostFocus = self._addCommand('onLostFocus')
