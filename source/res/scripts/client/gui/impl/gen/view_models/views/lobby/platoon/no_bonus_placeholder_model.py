# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/no_bonus_placeholder_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NoBonusPlaceholderModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NoBonusPlaceholderModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getResource(0)

    def setText(self, value):
        self._setResource(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(NoBonusPlaceholderModel, self)._initialize()
        self._addResourceProperty('text', R.invalid())
        self._addResourceProperty('icon', R.invalid())
