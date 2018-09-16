# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/simple_dialog_window_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class SimpleDialogWindowModel(ViewModel):
    __slots__ = ()

    def getHeader(self):
        return self._getResource(0)

    def setHeader(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(SimpleDialogWindowModel, self)._initialize()
        self._addResourceProperty('header', Resource.INVALID)
        self._addResourceProperty('description', Resource.INVALID)
