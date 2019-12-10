# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_talisman_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyTalismanTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyTalismanTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTalismanImage(self):
        return self._getResource(0)

    def setTalismanImage(self, value):
        self._setResource(0, value)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyTalismanTooltipModel, self)._initialize()
        self._addResourceProperty('talismanImage', R.invalid())
        self._addBoolProperty('isAvailable', False)
