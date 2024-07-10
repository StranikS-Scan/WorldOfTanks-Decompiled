# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/xp_records.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
from gui.battle_results.presenters.packers.economics.base_currency_packer import CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getSquadXp, getSquadXpPenalty, getMainValue, getMainEarnedValue, getIncreasingMainFactor, getEventValue, getWotPlusBonusValue
from gui.battle_results.settings import CurrenciesConstants
_STR_PATH = R.strings.battle_results.details.calculations
ORIGINAL_XP = CurrencyRecord(recordNames=('originalXP', 'appliedPremiumXPFactor100'), subtractRecords=('achievementXP',), valueExtractor=getMainEarnedValue, capsToBeChecked=None, label=_STR_PATH.base, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
ACHIEVEMENT_XP = CurrencyRecord(recordNames=('achievementXP',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.noPenalty, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
FRIENDLY_FIRE_PENALTY_XP = CurrencyRecord(recordNames=('originalXPPenalty',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.friendlyFirePenalty, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
IGR_BONUS_XP = CurrencyRecord(recordNames=('igrXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked=None, label=_STR_PATH.igrBonus.simpleLabel, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
DAILY_BONUS_XP = CurrencyRecord(recordNames=('dailyXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked={_CAPS.DAILY_MULTIPLIED_XP}, label=_STR_PATH.firstWin, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.MULTY_XP)
ADDITIONAL_BONUS_XP = CurrencyRecord(recordNames=('additionalXPFactor10',), subtractRecords=(), valueExtractor=getIncreasingMainFactor, capsToBeChecked={_CAPS.ADDITIONAL_XP_POSTBATTLE}, label=_STR_PATH.additionalBonus, modifiers=(ValueModifiers.MUL,), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
BOOSTERS_XP = CurrencyRecord(recordNames=('boosterXP', 'boosterXPFactor100'), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.boosters, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
TACTICAL_TRAINING_XP = CurrencyRecord(recordNames=('orderXPFactor100',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.tacticalTraining, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
EVENT_XP = CurrencyRecord(recordNames=('eventXPList_', 'eventXPFactor100List_'), subtractRecords=(), valueExtractor=getEventValue, capsToBeChecked=None, label=_STR_PATH.event, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
REFERRAL_BONUS_XP = CurrencyRecord(recordNames=('referral20XPFactor100',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.referralBonus.simpleLabel, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
PREMIUM_VEHICLE_XP = CurrencyRecord(recordNames=('premiumVehicleXPFactor100',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked={_CAPS.PREM_VEHICLE}, label=_STR_PATH.premiumVehicleXP, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
SQUAD_BONUS_XP = CurrencyRecord(recordNames=('squadXPFactor100',), subtractRecords=(), valueExtractor=getSquadXp, capsToBeChecked={_CAPS.SQUAD_XP}, label=_STR_PATH.squadXP, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
SQUAD_PENALTY_XP = CurrencyRecord(recordNames=('squadXPFactor100',), subtractRecords=(), valueExtractor=getSquadXpPenalty, capsToBeChecked={_CAPS.SQUAD_XP}, label=_STR_PATH.squadXPPenalty, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
WOT_PLUS_BONUS_XP = CurrencyRecord(recordNames=('wotPlusXP', 'wotPlusXPFactor100'), subtractRecords=(), valueExtractor=getWotPlusBonusValue, capsToBeChecked=None, label=_STR_PATH.wotPlus, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)
TOTAL_XP = CurrencyRecord(recordNames=('xp',), subtractRecords=(), valueExtractor=getMainValue, capsToBeChecked=None, label=_STR_PATH.title.total, modifiers=(), showZeroValue=True, currencyType=CurrenciesConstants.XP_COST)
