# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/crystals_records.py
from gui.impl.gen import R
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getCrystalValue, getCrystalTotalValue
from gui.battle_results.settings import CurrenciesConstants
_STR_PATH = R.strings.battle_results.details.calculations
ORIGINAL_CRYSTALS = CurrencyRecord(recordNames=('originalCrystal',), subtractRecords=(), valueExtractor=getCrystalValue, capsToBeChecked=None, label=_STR_PATH.crystal.total, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
EVENT_CRYSTALS = CurrencyRecord(recordNames=('events',), subtractRecords=(), valueExtractor=getCrystalValue, capsToBeChecked=None, label=_STR_PATH.crystal.events, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
AUTO_EQUIP_CRYSTALS = CurrencyRecord(recordNames=('autoEquipCrystals',), subtractRecords=(), valueExtractor=getCrystalValue, capsToBeChecked=None, label=_STR_PATH.autoBoosters, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
TOTAL_CRYSTALS = CurrencyRecord(recordNames=('originalCrystal', 'events'), subtractRecords=('autoEquipCrystals',), valueExtractor=getCrystalTotalValue, capsToBeChecked=None, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.CRYSTAL)
