# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/tooltips/critical_damage_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.critical_damage_group_model import CriticalDamageGroupModel

class CriticalDamageTooltipModel(ViewModel):
    __slots__ = ()
    CRITICAL_DAMAGE = 'criticalDamage'

    def __init__(self, properties=2, commands=0):
        super(CriticalDamageTooltipModel, self).__init__(properties=properties, commands=commands)

    def getParamType(self):
        return self._getString(0)

    def setParamType(self, value):
        self._setString(0, value)

    def getDetails(self):
        return self._getArray(1)

    def setDetails(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDetailsType():
        return CriticalDamageGroupModel

    def _initialize(self):
        super(CriticalDamageTooltipModel, self)._initialize()
        self._addStringProperty('paramType', '')
        self._addArrayProperty('details', Array())
