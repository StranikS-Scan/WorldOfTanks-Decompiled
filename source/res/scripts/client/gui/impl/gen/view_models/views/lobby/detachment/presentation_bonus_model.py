# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/presentation_bonus_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PresentationBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PresentationBonusModel, self).__init__(properties=properties, commands=commands)

    def getItemCD(self):
        return self._getNumber(0)

    def setItemCD(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PresentationBonusModel, self)._initialize()
        self._addNumberProperty('itemCD', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('amount', 0)
