# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/detailed_stats_crystals.py
from collections import namedtuple
from enum import Enum
import typing
from gui.battle_results.presenter.getter.detailed_stats import CurrencyField, EventField, StatsCurrencyBlock
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_record_model import DetailsRecordModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.battle_results.reusable.records import ReplayRecords

class _CrystalBlockIndexes(Enum):
    EARNED = 0
    TOTAL = 1


class _CrystalEarningsBlockIndexes(Enum):
    ACHIEVEMENTS = 0
    TOTAL_EARNED = 1


class _CrystalExpensesBlockIndexes(Enum):
    EXPENSES = 0
    TOTAL_EXPENSES = 1


_CRYSTAL_STRINGS = R.strings.postbattle_screen.detailsStats.crystals
DetailedStatsCrystalFields = namedtuple('crystalFields', ('earned', 'expenses', 'earnings', 'total'))
DetailedStatsCrystalExpenses = namedtuple('crystalFields', ('autoBooster',))
DetailedStatsCrystalEarnings = namedtuple('crystalFields', ('achievement',))

class CrystalsField(CurrencyField):
    __slots__ = ()

    def __init__(self, stringID, blockIdx, recordItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CrystalsField, self).__init__(stringID, blockIdx, recordItems, CurrencyModel.CRYSTALS, tags, isShown, tooltipString)
        self._recordItems = recordItems

    def getFieldValues(self, record):
        return self._getRecord(self._getValue(record))

    def _getValue(self, record):
        return record.getRecord(*self._recordItems)


class CrystalsTotalField(CurrencyField):
    __slots__ = ('_recordSubtractItems',)

    def __init__(self, stringID, blockIdx, recordItems, recordSubtractItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CrystalsTotalField, self).__init__(stringID, blockIdx, recordItems, CurrencyModel.CRYSTALS, tags, isShown, tooltipString)
        self._recordSubtractItems = recordSubtractItems

    def getFieldValues(self, record, additionalRecord):
        return self._getRecord(self._getValue(record, additionalRecord))

    def _getValue(self, record, additionalRecord):
        return record.getRecord(*self._recordItems) + additionalRecord.getRecord(*self._recordSubtractItems)


def getCrystalFields():
    return DetailedStatsCrystalFields(earned=_getEarnedCrystal(), earnings=_getCrystalEarnings(), expenses=_getCrystalExpenses(), total=_getTotalCrystal())


def _getEarnedCrystal():
    return CrystalsField(blockIdx=_CrystalBlockIndexes.EARNED, stringID=_CRYSTAL_STRINGS.earned(), tooltipString=_CRYSTAL_STRINGS.earned.descr(), tags=(DetailsRecordModel.EARNED,), recordItems=('originalCrystal',), isShown=True)


def _getDetailedCrystalExpenses():
    return DetailedStatsCrystalExpenses(autoBooster=CrystalsField(blockIdx=_CrystalExpensesBlockIndexes.EXPENSES, stringID=_CRYSTAL_STRINGS.expenses.autoBooster(), tooltipString=_CRYSTAL_STRINGS.expenses.autoBooster.descr(), recordItems=('autoBoostersCrystal',), isShown=True))


def _getTotalCrystalExpenses():
    return CrystalsField(blockIdx=_CrystalExpensesBlockIndexes.TOTAL_EXPENSES, stringID=_CRYSTAL_STRINGS.expenses.total(), tooltipString=_CRYSTAL_STRINGS.expenses.total.descr(), tags=(DetailsRecordModel.SUBGROUP_TOTAL,), recordItems=('autoBoostersCrystal',), isShown=True)


def _getCrystalExpenses():
    return StatsCurrencyBlock(detailed=_getDetailedCrystalExpenses(), total=_getTotalCrystalExpenses())


def _getCrystalEarnings():
    return StatsCurrencyBlock(detailed=_getDetailedCrystalEarnings(), total=_getTotalCrystalEarnings())


def _getDetailedCrystalEarnings():
    return DetailedStatsCrystalEarnings(achievement=EventField(blockIdx=_CrystalEarningsBlockIndexes.ACHIEVEMENTS, stringID=_CRYSTAL_STRINGS.achievement(), tooltipString=_CRYSTAL_STRINGS.achievement.descr(), recordItems=('eventCrystalList',), valueType=CurrencyModel.CRYSTALS, isShown=True))


def _getTotalCrystalEarnings():
    return CrystalsField(blockIdx=_CrystalEarningsBlockIndexes.TOTAL_EARNED, stringID=_CRYSTAL_STRINGS.totalEarnings(), tooltipString=_CRYSTAL_STRINGS.totalEarnings.descr(), tags=(DetailsRecordModel.SUBGROUP_TOTAL,), recordItems=('crystal',), isShown=True)


def _getTotalCrystal():
    return CrystalsTotalField(blockIdx=_CrystalBlockIndexes.TOTAL, stringID=_CRYSTAL_STRINGS.total(), tooltipString=_CRYSTAL_STRINGS.total.descr(), tags=(DetailsRecordModel.TOTAL,), recordItems=('crystal',), recordSubtractItems=('autoBoostersCrystal',), isShown=True)
