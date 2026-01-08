# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/financial_report_packers.py
from itertools import izip_longest
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.battle_results.pbs_helpers.economics import getDirectXpRecords, FinancialRecordValues, getDirectFreeXpRecords, getDirectMoneyRecords
from gui.battle_results.presenters.packers.economics import xp_records, common_records, free_xp_records, credits_records, gold_records
from gui.battle_results.presenters.packers.economics.crystals_records import ORIGINAL_CRYSTALS, EVENT_CRYSTALS, AUTO_EQUIP_CRYSTALS, TOTAL_CRYSTALS
from gui.battle_results.presenters.packers.economics.currency_packers import DetailedCurrencyPacker, CurrencyRecord
from gui.battle_results.presenters.packers.economics.value_extractors import getBaseAccountValue, getPremiumAccountValue
from gui.battle_results.reusable.records import RecordsIterator
from gui.battle_results.settings import CurrenciesConstants
from gui.impl.gen import R
from shared_utils import first
from soft_exception import SoftException

class FrontlineDetailedCurrencyPacker(DetailedCurrencyPacker):

    @classmethod
    def packModel(cls, model, currencyType, battleResults, vehIdx=-1):
        recordsExtractors, recordsConfigsExtractor = cls._getExtractors(battleResults)
        if recordsExtractors is None or recordsConfigsExtractor is None:
            raise SoftException('Invalid currency data')
        records = [ extractor(battleResults.reusable) for extractor in recordsExtractors ]
        if vehIdx >= 0 and isinstance(first(records), FinancialRecordValues):
            baseAccountValue, premiumAccountValue, additionalValue, extraValue, baseAccountValueWithWotPlus, premiumAccountValueWithWotPlus = list(izip_longest(*[ item or [] for item in records[0] ]))[vehIdx + 1]
            specRecords = [FinancialRecordValues(baseAccountValue=RecordsIterator([baseAccountValue]) if baseAccountValue else None, premiumAccountValue=RecordsIterator([premiumAccountValue]) if premiumAccountValue else None, additionalValue=RecordsIterator([additionalValue]) if additionalValue else None, extraValue=RecordsIterator([extraValue]) if extraValue else None, baseAccountValueWithWotPlus=RecordsIterator([baseAccountValueWithWotPlus]) if baseAccountValueWithWotPlus else None, premiumAccountValueWithWotPlus=RecordsIterator([premiumAccountValueWithWotPlus]) if premiumAccountValueWithWotPlus else None)]
        elif vehIdx >= 0 and isinstance(first(records), RecordsIterator):
            recordItem = zip(records[0])[vehIdx + 1]
            specRecords = [RecordsIterator(recordItem) if recordItem else None]
        else:
            specRecords = records
        cls._packGroup(model.getEarned(), specRecords, battleResults, recordsConfigsExtractor, cls._EARNED)
        cls._packGroup(model.getExpenses(), specRecords, battleResults, recordsConfigsExtractor, cls._EXPENSES)
        cls._packGroup(model.getTotal(), specRecords, battleResults, recordsConfigsExtractor, cls._TOTAL)
        return


RANK_BONUS_XP = CurrencyRecord(recordNames=('playerRankXPFactor100',), subtractRecords=(), baseAccountValueExtractor=getBaseAccountValue, premiumAccountValueExtractor=getPremiumAccountValue, detailsValuesExtractors=(), capsToBeChecked={ARENA_BONUS_TYPE_CAPS.PLAYER_RANK_MECHANICS}, paramName='playerRankXP', label=R.strings.battle_results.details.calculations.playerRankXP, modifiers=(), showZeroValue=False, currencyType=CurrenciesConstants.XP_COST)

class FrontlineXpDetailsPacker(FrontlineDetailedCurrencyPacker):
    _EARNED = (xp_records.ORIGINAL_XP,
     xp_records.ACHIEVEMENT_XP,
     xp_records.FRIENDLY_FIRE_PENALTY_XP,
     xp_records.IGR_BONUS_XP,
     xp_records.FIRST_WIN_XP,
     xp_records.ADDITIONAL_BONUS_XP,
     xp_records.BOOSTERS_XP,
     xp_records.TACTICAL_TRAINING_XP,
     xp_records.EVENT_XP,
     xp_records.REFERRAL_BONUS_XP,
     xp_records.PREMIUM_VEHICLE_XP,
     xp_records.SQUAD_BONUS_XP,
     xp_records.SQUAD_PENALTY_XP,
     common_records.AOGAS_FACTOR,
     xp_records.WOT_PLUS_BONUS_XP,
     common_records.DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION,
     RANK_BONUS_XP)
    _EXPENSES = None
    _TOTAL = (xp_records.TOTAL_XP,)

    @classmethod
    def _getExtractors(cls, battleResults):
        return ((getDirectXpRecords,), zip)


class FrontlineCrystalsDetailsPacker(FrontlineDetailedCurrencyPacker):
    _EARNED = (ORIGINAL_CRYSTALS, EVENT_CRYSTALS)
    _EXPENSES = (AUTO_EQUIP_CRYSTALS,)
    _TOTAL = (TOTAL_CRYSTALS,)

    @classmethod
    def _getExtractors(cls, battleResults):
        return ((lambda _: battleResults.reusable.personal.getCrystalDetailsRecords(),), zip)


class FrontlineFreeXpDetailsPacker(FrontlineDetailedCurrencyPacker):
    _EARNED = (free_xp_records.ORIGINAL_FREE_XP,
     free_xp_records.ACHIEVEMENT_FREE_XP,
     free_xp_records.IGR_BONUS_FREE_XP,
     free_xp_records.FIRST_WIN_FREE_XP,
     free_xp_records.ADDITIONAL_BONUS_FREE_XP,
     free_xp_records.BOOSTERS_FREE_XP,
     free_xp_records.MILITARY_MANEUVERS_FREE_XP,
     free_xp_records.EVENT_FREE_XP,
     free_xp_records.PREMIUM_VEHICLE_FREE_XP,
     common_records.AOGAS_FACTOR,
     free_xp_records.WOT_PLUS_BONUS_FREE_XP,
     common_records.DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION)
    _EXPENSES = None
    _TOTAL = (free_xp_records.TOTAL_FREE_XP,)

    @classmethod
    def _getExtractors(cls, battleResults):
        return ((getDirectFreeXpRecords,), zip)


class FrontlineCreditsStatisticsPacker(FrontlineDetailedCurrencyPacker):
    _EARNED = (credits_records.BASE_EARNED_CREDITS,
     credits_records.SQUAD_BONUS_CREDITS,
     credits_records.ACHIEVEMENT_CREDITS,
     credits_records.BOOSTERS_CREDITS,
     credits_records.PET_SYSTEM_BONUS_CREDITS,
     credits_records.BATTLE_PAYMENTS_CREDITS,
     credits_records.EVENT_PAYMENTS_CREDITS,
     credits_records.REFERRAL_BONUS_CREDITS,
     credits_records.WOT_PLUS_BONUS_CREDITS,
     common_records.DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION,
     credits_records.FRIENDLY_FIRE_PENALTY_CREDITS,
     credits_records.FRIENDLY_FIRE_COMPENSATION_CREDITS,
     common_records.AOGAS_FACTOR,
     credits_records.PIGGY_BANK_CREDITS)
    _EXPENSES = (credits_records.AUTO_REPAIR_CREDITS, credits_records.AUTO_LOAD_CREDITS, credits_records.AUTO_EQUIP_CREDITS)
    _TOTAL = (credits_records.INTERMEDIATE_TOTAL_CREDITS, credits_records.TOTAL_CREDITS)

    @classmethod
    def _getExtractors(cls, battleResults):
        return ((getDirectMoneyRecords,), zip)


class FrontlineGoldStatisticsPacker(FrontlineDetailedCurrencyPacker):
    _EARNED = (gold_records.GOLD_PIGGY_BANK, gold_records.GOLD_EVENT_PAYMENTS)
    _EXPENSES = None
    _TOTAL = (gold_records.TOTAL_GOLD, gold_records.INTERMEDIATE_TOTAL_GOLD)

    @classmethod
    def _getExtractors(cls, battleResults):
        return ((getDirectMoneyRecords,), zip)
