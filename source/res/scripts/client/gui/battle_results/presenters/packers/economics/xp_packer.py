# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/economics/xp_packer.py
import logging
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.battle_results.presenters.packers.economics.base_currency_packer import BaseCurrencyPacker, CurrencyGroup
from gui.battle_results.presenters.packers.economics import xp_records, free_xp_records, common_records
from gui.battle_results.pbs_helpers.economics import getXpRecords, getFreeXpRecords
from gui.battle_results.settings import CurrenciesConstants
_logger = logging.getLogger(__name__)

class XpPacker(BaseCurrencyPacker):
    __slots__ = ()
    _EARNED = CurrencyGroup(label=None, records=[(xp_records.ORIGINAL_XP, free_xp_records.ORIGINAL_FREE_XP),
     (xp_records.ACHIEVEMENT_XP, free_xp_records.ACHIEVEMENT_FREE_XP),
     (xp_records.FRIENDLY_FIRE_PENALTY_XP, None),
     (xp_records.IGR_BONUS_XP, free_xp_records.IGR_BONUS_FREE_XP),
     (xp_records.DAILY_BONUS_XP, free_xp_records.DAILY_BONUS_FREE_XP),
     (xp_records.ADDITIONAL_BONUS_XP, free_xp_records.ADDITIONAL_BONUS_FREE_XP),
     (xp_records.BOOSTERS_XP, free_xp_records.BOOSTERS_FREE_XP),
     (xp_records.TACTICAL_TRAINING_XP, None),
     (None, free_xp_records.MILITARY_MANEUVERS_FREE_XP),
     (xp_records.EVENT_XP, free_xp_records.EVENT_FREE_XP),
     (xp_records.REFERRAL_BONUS_XP, None),
     (xp_records.PREMIUM_VEHICLE_XP, free_xp_records.PREMIUM_VEHICLE_FREE_XP),
     (xp_records.SQUAD_BONUS_XP, None),
     (xp_records.SQUAD_PENALTY_XP, None),
     (common_records.AOGAS_FACTOR, common_records.AOGAS_FACTOR),
     (xp_records.WOT_PLUS_BONUS_XP, free_xp_records.WOT_PLUS_BONUS_FREE_XP),
     (common_records.DESERTER_VIOLATION, common_records.DESERTER_VIOLATION),
     (common_records.SUICIDE_VIOLATION, common_records.SUICIDE_VIOLATION),
     (common_records.AFK_VIOLATION, common_records.AFK_VIOLATION)])
    _EXPENSES = None
    _TOTAL = CurrencyGroup(label=None, records=[(xp_records.TOTAL_XP, free_xp_records.TOTAL_FREE_XP)])
    _EXTRACTORS = {(True, True): ((getXpRecords, getFreeXpRecords), lambda configs: configs),
     (True, False): ((getXpRecords,), lambda configs: zip([ pair[0] for pair in configs ])),
     (False, True): ((getFreeXpRecords,), lambda configs: zip([ pair[1] for pair in configs ]))}

    @classmethod
    def _getExtractors(cls, currencyType, battleResults):
        if currencyType == CurrenciesConstants.FREE_XP:
            return cls._EXTRACTORS[False, True]
        elif currencyType == CurrenciesConstants.XP_COST:
            commonInfo = battleResults.reusable.common
            state = (True, commonInfo.checkBonusCaps(_CAPS.FREE_XP))
            return cls._EXTRACTORS.get(state, cls._EXTRACTORS[True, False])
        else:
            _logger.error('Invalid currency constant for the tooltip')
            return (None, None)
