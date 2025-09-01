# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/gold_records.py
from gui.battle_results.pbs_helpers.economics import isPiggyBankGoldAvailable
from gui.battle_results.presenters.packers.economics.currency_packers import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getGoldEventValue, getGoldPiggyBank, getTotalGoldValue, getIntermediateTotalGoldValue
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
from gui.battle_results.settings import CurrenciesConstants
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
_STR_PATH = R.strings.battle_results.details.calculations
GOLD_EVENT_PAYMENTS = CurrencyRecord(recordNames=('eventGoldList_',), subtractRecords=(), baseAccountValueExtractor=getGoldEventValue, premiumAccountValueExtractor=getGoldEventValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.GOLD_EVENT_PAYMENTS, label=_STR_PATH.event, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.GOLD)
GOLD_PIGGY_BANK = CurrencyRecord(recordNames=(), subtractRecords=(), baseAccountValueExtractor=getGoldPiggyBank, premiumAccountValueExtractor=getGoldPiggyBank, detailsValuesExtractors=(isPiggyBankGoldAvailable,), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.GOLD_PIGGY_BANK, label=_STR_PATH.piggyBankInfo, modifiers=(ValueModifiers.ADD,), showZeroValue=False, currencyType=CurrenciesConstants.GOLD)
INTERMEDIATE_TOTAL_GOLD = CurrencyRecord(recordNames=('gold',), subtractRecords=(), baseAccountValueExtractor=getIntermediateTotalGoldValue, premiumAccountValueExtractor=getIntermediateTotalGoldValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.INTERMEDIATE_TOTAL_GOLD, label=_STR_PATH.intermediateTotal, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.GOLD)
TOTAL_GOLD = CurrencyRecord(recordNames=('gold',), subtractRecords=('autoLoadGold', 'autoEquipGold'), baseAccountValueExtractor=getTotalGoldValue, premiumAccountValueExtractor=getTotalGoldValue, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.TOTAL_GOLD, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.GOLD)
