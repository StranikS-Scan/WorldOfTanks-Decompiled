# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/common_records.py
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getDeserterViolation, getAfkViolation, getSuicideViolation, getDecreasingMainFactor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
_STR_PATH = R.strings.battle_results.details.calculations
AOGAS_FACTOR = CurrencyRecord(recordNames=('aogasFactor10',), subtractRecords=(), valueExtractor=getDecreasingMainFactor, capsToBeChecked=None, label=_STR_PATH.aogasFactor, modifiers=(ValueModifiers.MUL, ValueModifiers.SHOW_NEGATIVE_IMPACT), showZeroValue=True, currencyType='')
DESERTER_VIOLATION = CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=getDeserterViolation, capsToBeChecked=None, label=_STR_PATH.fairPlayViolation.deserter, modifiers=(ValueModifiers.PROCENT,), showZeroValue=False, currencyType='')
AFK_VIOLATION = CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=getAfkViolation, capsToBeChecked=None, label=_STR_PATH.fairPlayViolation.afk, modifiers=(ValueModifiers.PROCENT,), showZeroValue=False, currencyType='')
SUICIDE_VIOLATION = CurrencyRecord(recordNames=(), subtractRecords=(), valueExtractor=getSuicideViolation, capsToBeChecked=None, label=_STR_PATH.fairPlayViolation.suicide, modifiers=(ValueModifiers.PROCENT,), showZeroValue=False, currencyType='')
