# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/common/base_overlay_view_model.py
from frameworks.wulf import ViewModel

class BaseOverlayViewModel(ViewModel):
    __slots__ = ('onCloseClicked', 'onEscapePressed')

    def __init__(self, properties=2, commands=2):
        super(BaseOverlayViewModel, self).__init__(properties=properties, commands=commands)

    def getIsCloseVisible(self):
        return self._getBool(0)

    def setIsCloseVisible(self, value):
        self._setBool(0, value)

    def getIsHidden(self):
        return self._getBool(1)

    def setIsHidden(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(BaseOverlayViewModel, self)._initialize()
        self._addBoolProperty('isCloseVisible', True)
        self._addBoolProperty('isHidden', False)
        self.onCloseClicked = self._addCommand('onCloseClicked')
        self.onEscapePressed = self._addCommand('onEscapePressed')
