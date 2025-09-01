# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/crystals_records.py
from gui.impl.gen import R
from gui.battle_results.presenters.packers.economics.currency_packers import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getCrystalValue, getCrystalTotalValue
from gui.battle_results.settings import CurrenciesConstants
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
_STR_PATH = R.strings.battle_results.details.calculations
ORIGINAL_CRYSTALS = CurrencyRecord(recordNames=('originalCrystal',), subtractRecords=(), baseAccountValueExtractor=getCrystalValue, premiumAccountValueExtractor=getCrystalValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.ORIGINAL_CRYSTALS, label=_STR_PATH.crystal.total, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
EVENT_CRYSTALS = CurrencyRecord(recordNames=('events',), subtractRecords=(), baseAccountValueExtractor=getCrystalValue, premiumAccountValueExtractor=getCrystalValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.EVENT_CRYSTALS, label=_STR_PATH.crystal.events, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
AUTO_EQUIP_CRYSTALS = CurrencyRecord(recordNames=('autoEquipCrystals',), subtractRecords=(), baseAccountValueExtractor=getCrystalValue, premiumAccountValueExtractor=getCrystalValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.AUTO_EQUIP_CRYSTALS, label=_STR_PATH.autoBoosters, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.CRYSTAL)
TOTAL_CRYSTALS = CurrencyRecord(recordNames=('originalCrystal', 'events'), subtractRecords=('autoEquipCrystals',), baseAccountValueExtractor=getCrystalTotalValue, premiumAccountValueExtractor=getCrystalTotalValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.TOTAL_CRYSTALS, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.CRYSTAL)
