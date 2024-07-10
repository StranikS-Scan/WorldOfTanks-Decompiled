# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/crystals_packer.py
from gui.impl.gen import R
from gui.battle_results.presenters.packers.economics.base_currency_packer import BaseCurrencyPacker, CurrencyGroup
from gui.battle_results.presenters.packers.economics.crystals_records import ORIGINAL_CRYSTALS, EVENT_CRYSTALS, AUTO_EQUIP_CRYSTALS, TOTAL_CRYSTALS
_STR_PATH = R.strings.battle_results.details.calculations

class CrystalsPacker(BaseCurrencyPacker):
    __slots__ = ()
    _EARNED = CurrencyGroup(label=_STR_PATH.title.base, records=(ORIGINAL_CRYSTALS, EVENT_CRYSTALS))
    _EXPENSES = CurrencyGroup(label=_STR_PATH.title.expenses, records=(AUTO_EQUIP_CRYSTALS,))
    _TOTAL = CurrencyGroup(label=None, records=(TOTAL_CRYSTALS,))

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        return ((lambda _: battleResults.reusable.personal.getCrystalDetailsRecords(),), zip)
