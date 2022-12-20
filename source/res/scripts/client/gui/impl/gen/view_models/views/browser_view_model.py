# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/browser_view_model.py
from gui.impl.gen.view_models.common.browser_model import BrowserModel

class BrowserViewModel(BrowserModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=7, commands=4):
        super(BrowserViewModel, self).__init__(properties=properties, commands=commands)

    def getIsClosable(self):
        return self._getBool(6)

    def setIsClosable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BrowserViewModel, self)._initialize()
        self._addBoolProperty('isClosable', False)
        self.onClose = self._addCommand('onClose')
