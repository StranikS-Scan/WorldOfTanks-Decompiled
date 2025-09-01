# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/pbs_helpers/economics.py
from collections import namedtuple
import typing
from helpers import dependency
from shared_utils import first
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.battle_results.pbs_helpers.additional_bonuses import isGoldPiggyBankAvailaible
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.stats_ctrl import BattleResults
FinancialRecordValues = namedtuple('FinancialRecordValues', ('baseAccountValue', 'premiumAccountValue', 'additionalValue', 'extraValue', 'baseAccountValueWithWotPlus', 'premiumAccountValueWithWotPlus'))

def getTotalCrystalsToShow(reusable):
    record = first(reusable.personal.getCrystalRecords())
    if record:
        _, crystals = record[:2]
        return crystals.getRecord('crystal')


def getTotalXPToShow(reusable):
    hasPremium = reusable.personal.hasAnyPremium
    xpRecords = getDirectXpRecords(reusable)
    return xpRecords.premiumAccountValue.getRecord('xpToShow') if hasPremium else xpRecords.baseAccountValue.getRecord('xpToShow')


def getTotalFreeXPToShow(reusable):
    hasPremium = reusable.personal.hasAnyPremium
    freeXpRecords = getDirectFreeXpRecords(reusable)
    return freeXpRecords.premiumAccountValue.getRecord('freeXP') if hasPremium else freeXpRecords.baseAccountValue.getRecord('freeXP')


def getCreditsToShow(reusable, isDiffShow=False):
    values = []
    for creditRecords in reusable.personal.getMoneyRecords():
        baseCredits, premiumCredits = creditRecords[:2]
        value = premiumCredits.getRecord('credits', 'originalCreditsToDraw')
        if isDiffShow and value > 0:
            value -= baseCredits.getRecord('credits', 'originalCreditsToDraw')
        values.append(value)

    return values


def getTotalCreditsToShow(reusable):
    hasPremium = reusable.personal.hasAnyPremium
    moneyRecords = getDirectMoneyRecords(reusable)
    return moneyRecords.premiumAccountValue.getRecord('credits', 'originalCreditsToDraw') if hasPremium else moneyRecords.baseAccountValue.getRecord('credits', 'originalCreditsToDraw')


def getDirectMoneyRecords(reusable):
    personalResults = reusable.personal
    base, premium, gold, additional, baseWithWotPlus, premiumWithWotPlus = first(personalResults.getMoneyRecords())
    return FinancialRecordValues(baseAccountValue=base, premiumAccountValue=premium, additionalValue=additional, extraValue=gold, baseAccountValueWithWotPlus=baseWithWotPlus, premiumAccountValueWithWotPlus=premiumWithWotPlus)


def getDirectXpRecords(reusable):
    personalResults = reusable.personal
    baseXP, premiumXP, _, _, baseXPWithWotPlus, premiumXPWithWotPlus, _, _ = first(personalResults.getXPRecords())
    return FinancialRecordValues(baseAccountValue=baseXP, premiumAccountValue=premiumXP, additionalValue=None, extraValue=None, baseAccountValueWithWotPlus=baseXPWithWotPlus, premiumAccountValueWithWotPlus=premiumXPWithWotPlus)


def getDirectFreeXpRecords(reusable):
    personalResults = reusable.personal
    _, _, baseFreeXP, premiumFreeXP, _, _, baseFreeXPWithWotPlus, premiumFreeXPWithWotPlus = first(personalResults.getXPRecords())
    return FinancialRecordValues(baseAccountValue=baseFreeXP, premiumAccountValue=premiumFreeXP, additionalValue=None, extraValue=None, baseAccountValueWithWotPlus=baseFreeXPWithWotPlus, premiumAccountValueWithWotPlus=premiumFreeXPWithWotPlus)


def hasAogasFine(battleResults):
    factor = 'aogasFactor10'
    xpRecords = getDirectXpRecords(battleResults.reusable)
    moneyRecords = getDirectMoneyRecords(battleResults.reusable)
    return ('hasAogasFine', moneyRecords.premiumAccountValue.getFactor(factor) < 1 or xpRecords.premiumAccountValue.getFactor(factor) < 1) if battleResults.reusable.personal.hasAnyPremium else ('hasAogasFine', moneyRecords.baseAccountValue.getFactor(factor) < 1 or xpRecords.baseAccountValue.getFactor(factor) < 1)


def hasHighScope(battleResults):
    personalResults = battleResults.reusable.personal
    baseXP, _, _, _, _, _, _, _ = first(personalResults.getXPRecords())
    return ('isHighScope', baseXP.getRecord('isHighScope')) if baseXP else ('isHighScope', False)


def hasXpReferralFactor(battleResults):
    personalResults = battleResults.reusable.personal
    baseXP, _, _, _, _, _, _, _ = first(personalResults.getXPRecords())
    if baseXP:
        referralFactor = baseXP.getFactor('referral20XPFactor100')
        if referralFactor > 0 and baseXP.getRecord('referral20XPFactor100'):
            return ('referralFactor', referralFactor)


def hasCreditsReferralFactor(battleResults):
    personalResults = battleResults.reusable.personal
    baseCredits, _, _, _, _, _ = first(personalResults.getMoneyRecords())
    referralFactor = 0
    if baseCredits:
        referralFactor = baseCredits.getFactor('referral20CreditsFactor100')
    return ('referralFactor', max(referralFactor, 0))


def isPiggyBankCreditsAvailable(battleResults):
    isAvailable = battleResults.reusable.common.checkBonusCaps(_CAPS.PIGGY_BANK_CREDITS)
    return ('isAvailable', isAvailable)


def isPiggyBankGoldAvailable(battleResults):
    isAvailable = isGoldPiggyBankAvailaible(battleResults.reusable)
    return ('isAvailable', isAvailable)


def isCreditsAvailable(battleResults):
    isAvailable = battleResults.reusable.common.checkBonusCaps(_CAPS.CREDITS)
    return ('isAvailable', isAvailable)


def isXpAvailable(battleResults):
    isAvailable = battleResults.reusable.common.checkBonusCaps(_CAPS.XP)
    return ('isAvailable', isAvailable)


def isFreeXpAvailable(battleResults):
    isAvailable = battleResults.reusable.common.checkBonusCaps(_CAPS.FREE_XP)
    return ('isAvailable', isAvailable)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isWotPlusBonusEnabled(_, lobbyContext=None):
    isWotPlusBattleBonusesEnabled = lobbyContext.getServerSettings().isWotPlusBattleBonusesEnabled()
    return ('isEnabled', isWotPlusBattleBonusesEnabled)
