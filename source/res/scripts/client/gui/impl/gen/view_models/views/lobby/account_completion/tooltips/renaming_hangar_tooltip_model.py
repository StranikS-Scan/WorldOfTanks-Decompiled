# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/tooltips/renaming_hangar_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RenamingHangarTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RenamingHangarTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getText(self):
        return self._getResource(1)

    def setText(self, value):
        self._setResource(1, value)

    def getTextInner(self):
        return self._getResource(2)

    def setTextInner(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(RenamingHangarTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('text', R.invalid())
        self._addResourceProperty('textInner', R.invalid())
