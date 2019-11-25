# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/full_screen_dialog_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FullScreenDialogWindowModel(ViewModel):
    __slots__ = ('onAcceptClicked', 'onCancelClicked')

    def __init__(self, properties=8, commands=2):
        super(FullScreenDialogWindowModel, self).__init__(properties=properties, commands=commands)

    def getDialogType(self):
        return self._getString(0)

    def setDialogType(self, value):
        self._setString(0, value)

    def getCredits(self):
        return self._getNumber(1)

    def setCredits(self, value):
        self._setNumber(1, value)

    def getGolds(self):
        return self._getNumber(2)

    def setGolds(self, value):
        self._setNumber(2, value)

    def getCrystals(self):
        return self._getNumber(3)

    def setCrystals(self, value):
        self._setNumber(3, value)

    def getFreexp(self):
        return self._getNumber(4)

    def setFreexp(self, value):
        self._setNumber(4, value)

    def getIsAcceptDisabled(self):
        return self._getBool(5)

    def setIsAcceptDisabled(self, value):
        self._setBool(5, value)

    def getTitleBody(self):
        return self._getResource(6)

    def setTitleBody(self, value):
        self._setResource(6, value)

    def getTitleArgs(self):
        return self._getArray(7)

    def setTitleArgs(self, value):
        self._setArray(7, value)

    def _initialize(self):
        super(FullScreenDialogWindowModel, self)._initialize()
        self._addStringProperty('dialogType', 'simple')
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('golds', 0)
        self._addNumberProperty('crystals', 0)
        self._addNumberProperty('freexp', 0)
        self._addBoolProperty('isAcceptDisabled', False)
        self._addResourceProperty('titleBody', R.invalid())
        self._addArrayProperty('titleArgs', Array())
        self.onAcceptClicked = self._addCommand('onAcceptClicked')
        self.onCancelClicked = self._addCommand('onCancelClicked')
