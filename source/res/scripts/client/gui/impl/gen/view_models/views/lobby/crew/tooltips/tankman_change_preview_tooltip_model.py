# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/tankman_change_preview_tooltip_model.py
from frameworks.wulf import ViewModel

class TankmanChangePreviewTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankmanChangePreviewTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCredits(self):
        return self._getNumber(0)

    def setCredits(self, value):
        self._setNumber(0, value)

    def getRetrainingGold(self):
        return self._getNumber(1)

    def setRetrainingGold(self, value):
        self._setNumber(1, value)

    def getSpecialityGold(self):
        return self._getNumber(2)

    def setSpecialityGold(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(TankmanChangePreviewTooltipModel, self)._initialize()
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('retrainingGold', 0)
        self._addNumberProperty('specialityGold', 0)
