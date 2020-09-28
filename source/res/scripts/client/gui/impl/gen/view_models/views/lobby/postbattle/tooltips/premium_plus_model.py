# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/tooltips/premium_plus_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.premium_benefit_model import PremiumBenefitModel

class PremiumPlusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PremiumPlusModel, self).__init__(properties=properties, commands=commands)

    def getPremiumBenefits(self):
        return self._getArray(0)

    def setPremiumBenefits(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(PremiumPlusModel, self)._initialize()
        self._addArrayProperty('premiumBenefits', Array())
