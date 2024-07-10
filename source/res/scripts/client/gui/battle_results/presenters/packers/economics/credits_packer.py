# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/credits_packer.py
from gui.battle_results.presenters.packers.economics import credits_records
from gui.battle_results.presenters.packers.economics.base_currency_packer import BaseCurrencyPacker, CurrencyGroup
from gui.battle_results.presenters.packers.economics.common_records import AOGAS_FACTOR, AFK_VIOLATION, DESERTER_VIOLATION, SUICIDE_VIOLATION
from gui.battle_results.presenters.packers.economics.gold_records import GOLD_PIGGY_BANK, GOLD_EVENT_PAYMENTS
from gui.battle_results.pbs_helpers.economics import getCreditsRecords
from gui.impl.gen import R
_STR_PATH = R.strings.battle_results.details.calculations

class CreditsPacker(BaseCurrencyPacker):
    __slots__ = ()
    _EARNED = CurrencyGroup(label=None, records=(credits_records.BASE_EARNED,
     credits_records.SQUAD_BONUS,
     credits_records.ACHIEVEMENTS,
     credits_records.BOOSTERS,
     credits_records.BATTLE_PAYMENTS,
     credits_records.EVENT_PAYMENTS,
     credits_records.REFERRAL_BONUS,
     credits_records.WOT_PLUS_BONUS,
     DESERTER_VIOLATION,
     SUICIDE_VIOLATION,
     AFK_VIOLATION,
     credits_records.FRIENDLY_FIRE_PENALTY,
     credits_records.FRIENDLY_FIRE_COMPENSATION,
     AOGAS_FACTOR))
    _EXPENSES = CurrencyGroup(label=_STR_PATH.title.expenses, records=(credits_records.AUTO_REPAIR_COST, credits_records.AUTO_LOAD_COST, credits_records.AUTO_EQUIP_COST))
    _TOTAL = CurrencyGroup(label=None, records=(credits_records.TOTAL_CREDITS,))
    _ADDITIONAL = CurrencyGroup(label=None, records=(credits_records.PIGGY_BANK, GOLD_PIGGY_BANK, GOLD_EVENT_PAYMENTS))

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        return ((getCreditsRecords,), zip)
