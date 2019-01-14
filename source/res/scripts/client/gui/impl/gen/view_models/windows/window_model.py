# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/window_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from frameworks.wulf import View

class WindowModel(ViewModel):
    __slots__ = ('onClosed', 'onMinimized')

    def getContent(self):
        return self._getView(0)

    def setContent(self, value):
        self._setView(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getRawTitle(self):
        return self._getString(2)

    def setRawTitle(self, value):
        self._setString(2, value)

    def getCanMinimize(self):
        return self._getBool(3)

    def setCanMinimize(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WindowModel, self)._initialize()
        self._addViewProperty('content')
        self._addResourceProperty('title', R.invalid())
        self._addStringProperty('rawTitle', '')
        self._addBoolProperty('canMinimize', False)
        self.onClosed = self._addCommand('onClosed')
        self.onMinimized = self._addCommand('onMinimized')
