# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/simple_dialog_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SimpleDialogWindowModel(ViewModel):
    __slots__ = ()

    def getMessage(self):
        return self._getResource(0)

    def setMessage(self, value):
        self._setResource(0, value)

    def getMessageArgs(self):
        return self._getArray(1)

    def setMessageArgs(self, value):
        self._setArray(1, value)

    def getMessageFmtArgs(self):
        return self._getArray(2)

    def setMessageFmtArgs(self, value):
        self._setArray(2, value)

    def getIsMessageFmtArgsNamed(self):
        return self._getBool(3)

    def setIsMessageFmtArgsNamed(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SimpleDialogWindowModel, self)._initialize()
        self._addResourceProperty('message', R.invalid())
        self._addArrayProperty('messageArgs', Array())
        self._addArrayProperty('messageFmtArgs', Array())
        self._addBoolProperty('isMessageFmtArgsNamed', True)
