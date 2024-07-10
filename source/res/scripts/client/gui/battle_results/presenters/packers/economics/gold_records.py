# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/gold_records.py
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getGoldEventValue, getGoldPiggyBank
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
from gui.battle_results.settings import CurrenciesConstants
_STR_PATH = R.strings.battle_results.details.calculations
GOLD_EVENT_PAYMENTS = CurrencyRecord(recordNames=('eventGoldList_',), subtractRecords=(), valueExtractor=getGoldEventValue, capsToBeChecked=None, label=_STR_PATH.event, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.GOLD)
GOLD_PIGGY_BANK = CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=getGoldPiggyBank, capsToBeChecked=None, label=_STR_PATH.piggyBankInfo, modifiers=(ValueModifiers.ADD,), showZeroValue=False, currencyType=CurrenciesConstants.GOLD)
