# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/base_dialog_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseDialogModel(ViewModel):
    __slots__ = ('onAcceptClicked', 'onCancelClicked')

    def __init__(self, properties=3, commands=2):
        super(BaseDialogModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getSubTitle(self):
        return self._getResource(1)

    def setSubTitle(self, value):
        self._setResource(1, value)

    def getIsServerUnavailable(self):
        return self._getBool(2)

    def setIsServerUnavailable(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BaseDialogModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addBoolProperty('isServerUnavailable', False)
        self.onAcceptClicked = self._addCommand('onAcceptClicked')
        self.onCancelClicked = self._addCommand('onCancelClicked')
