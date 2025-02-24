# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/mentoring_license_tooltip_model.py
from frameworks.wulf import ViewModel

class MentoringLicenseTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(MentoringLicenseTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAmount(self):
        return self._getNumber(0)

    def setAmount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(MentoringLicenseTooltipModel, self)._initialize()
        self._addNumberProperty('amount', 0)
