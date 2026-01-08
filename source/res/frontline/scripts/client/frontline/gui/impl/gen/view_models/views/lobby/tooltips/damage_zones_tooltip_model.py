# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/damage_zones_tooltip_model.py
from frameworks.wulf import ViewModel

class DamageZonesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DamageZonesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSupplyHullDamageFactor(self):
        return self._getReal(0)

    def setSupplyHullDamageFactor(self, value):
        self._setReal(0, value)

    def getSupplyTurretDamageFactor(self):
        return self._getReal(1)

    def setSupplyTurretDamageFactor(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(DamageZonesTooltipModel, self)._initialize()
        self._addRealProperty('supplyHullDamageFactor', 0.0)
        self._addRealProperty('supplyTurretDamageFactor', 0.0)
