# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/comp7_light_financial_report_packers.py
from __future__ import absolute_import
from gui.battle_results.presenters.packers.economics.currency_packers import CurrencyRecord
from gui.battle_results.settings import CurrenciesConstants
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
from gui.impl.gen.view_models.views.lobby.battle_results.currency_value_model import ValueModifiers
from fairplay_violation_types import FairplayViolations
from gui.impl.gen import R
from gui.battle_results.presenters.packers.economics.financial_report_packers import CreditsStatisticsPacker, XpDetailsPacker, FreeXpDetailsPacker
from gui.battle_results.presenters.packers.economics import free_xp_records, xp_records, common_records, credits_records

def getComp7LightDeserterViolation(_, __, battleResults):
    avatarInfo = battleResults.reusable.personal.avatar
    if avatarInfo.hasPenalties():
        name, percent = avatarInfo.getPenaltyDetails()
        if name == FairplayViolations.COMP7_LIGHT_DESERTER:
            return percent
        return 0


COMP7_LIGHT_DESERTER_VIOLATION = CurrencyRecord(recordNames=(), subtractRecords=(), baseAccountValueExtractor=getComp7LightDeserterViolation, premiumAccountValueExtractor=getComp7LightDeserterViolation, detailsValuesExtractors=(), capsToBeChecked=None, paramName=CurrencyRecordsItemModel.DESERTER_VIOLATION, label=R.strings.battle_results.details.calculations.fairPlayViolation.deserter, modifiers=(ValueModifiers.PROCENT,), showZeroValue=False, currencyType=CurrenciesConstants.COMMON_CURRENCY)

class Comp7LightCreditsStatisticsPacker(CreditsStatisticsPacker):
    _EARNED = (credits_records.BASE_EARNED_CREDITS,
     credits_records.SQUAD_BONUS_CREDITS,
     credits_records.ACHIEVEMENT_CREDITS,
     credits_records.BOOSTERS_CREDITS,
     credits_records.PET_SYSTEM_BONUS_CREDITS,
     credits_records.BATTLE_PAYMENTS_CREDITS,
     credits_records.EVENT_PAYMENTS_CREDITS,
     credits_records.REFERRAL_BONUS_CREDITS,
     credits_records.WOT_PLUS_BONUS_CREDITS,
     credits_records.WOT_PLUS_PRO_BOOST_BONUS_CREDITS,
     COMP7_LIGHT_DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION,
     credits_records.FRIENDLY_FIRE_PENALTY_CREDITS,
     credits_records.FRIENDLY_FIRE_COMPENSATION_CREDITS,
     common_records.AOGAS_FACTOR,
     credits_records.PIGGY_BANK_CREDITS)


class Comp7LightXpDetailsPacker(XpDetailsPacker):
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
     xp_records.WOT_PLUS_PRO_BOOST_BONUS_XP,
     COMP7_LIGHT_DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION)


class Comp7LightFreeXpDetailsPacker(FreeXpDetailsPacker):
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
     free_xp_records.WOT_PLUS_PRO_BOOST_BONUS_FREE_XP,
     COMP7_LIGHT_DESERTER_VIOLATION,
     common_records.SUICIDE_VIOLATION,
     common_records.AFK_VIOLATION)
