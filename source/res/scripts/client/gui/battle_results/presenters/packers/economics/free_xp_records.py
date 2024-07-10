# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/free_xp_records.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getMainEarnedValue, getMainValue, getIncreasingMainFactor, getEventValue, getWotPlusBonusValue
from gui.battle_results.settings import CurrenciesConstants
_STR_PATH = R.strings.battle_results.details.calculations
ORIGINAL_FREE_XP = CurrencyRecord(recordNames=('originalFreeXP', 'appliedPremiumXPFactor100'), subtractRecords=('achievementFreeXP',), valueExtractor=getMainEarnedValue, capsToBeChecked=None, label=_STR_PATH.base, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
ACHIEVEMENT_FREE_XP = CurrencyRecord(recordNames=('achievementFreeXP',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.noPenalty, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
IGR_BONUS_FREE_XP = CurrencyRecord(recordNames=('igrXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked=None, label=_STR_PATH.igrBonus.simpleLabel, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
DAILY_BONUS_FREE_XP = CurrencyRecord(recordNames=('dailyXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked={_CAPS.DAILY_MULTIPLIED_XP}, label=_STR_PATH.firstWin, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.MULTY_FREE_XP)
ADDITIONAL_BONUS_FREE_XP = CurrencyRecord(recordNames=('additionalXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked={_CAPS.ADDITIONAL_XP_POSTBATTLE}, label=_STR_PATH.additionalBonus, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
BOOSTERS_FREE_XP = CurrencyRecord(recordNames=('boosterFreeXP', 'boosterFreeXPFactor100'), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.boosters, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
MILITARY_MANEUVERS_FREE_XP = CurrencyRecord(recordNames=('orderFreeXPFactor100',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.militaryManeuvers, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
EVENT_FREE_XP = CurrencyRecord(recordNames=('eventFreeXPList_', 'eventFreeXPFactor100List_'), subtractRecords=(), valueExtractor=getEventValue, capsToBeChecked=None, label=_STR_PATH.event, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
PREMIUM_VEHICLE_FREE_XP = CurrencyRecord(recordNames=('premiumVehicleXPFactor100',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.premiumVehicleXP, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
WOT_PLUS_BONUS_FREE_XP = CurrencyRecord(recordNames=('wotPlusFreeXP', 'wotPlusFreeXPFactor100'), subtractRecords=(), valueExtractor=getWotPlusBonusValue, capsToBeChecked=None, label=_STR_PATH.wotPlus, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.FREE_XP)
TOTAL_FREE_XP = CurrencyRecord(recordNames=('freeXP',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.FREE_XP)
