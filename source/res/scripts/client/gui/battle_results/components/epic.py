# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/epic.py
from gui.battle_results.components.personal import TotalEfficiencyDetailsHeader, _UNDEFINED_EFFICIENCY_VALUE
from gui.shared.formatters import numbers

class EpicTotalEfficiencyDetailsHeader(TotalEfficiencyDetailsHeader):
    __slots__ = ('damageToSupplies', 'suppliesDestroyed', 'questsCompleted')

    def __init__(self, meta=None, field='', *path):
        super(EpicTotalEfficiencyDetailsHeader, self).__init__(meta, field, *path)
        self.damageToSupplies = None
        self.suppliesDestroyed = None
        self.questsCompleted = None
        return

    def setRecord(self, result, reusable):
        super(EpicTotalEfficiencyDetailsHeader, self).setRecord(result, reusable)
        info = reusable.getPersonalVehiclesInfo(result)
        value = info.damageToSupplies
        self.damageToSupplies = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
        value = info.suppliesDestroyed
        self.suppliesDestroyed = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
        value = info.questsCompleted
        self.questsCompleted = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
        value = self.hasEfficencyStats + info.damageToSupplies + info.suppliesDestroyed + info.questsCompleted
        self.hasEfficencyStats = value > 0
