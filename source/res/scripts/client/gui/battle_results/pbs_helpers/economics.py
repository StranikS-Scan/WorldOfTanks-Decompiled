# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/pbs_helpers/economics.py
from collections import namedtuple
import typing
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
FinancialRecords = namedtuple('FinancialRecords', ('main', 'alternative', 'additional', 'extra', 'mainWithWotPlus', 'alternativeWithWotPlus'))

def getTotalCrystalsToShow(reusable):
    record = first(reusable.personal.getCrystalRecords())
    if record:
        _, crystals = record[:2]
        return crystals.getRecord('crystal')


def getTotalXPToShow(reusable):
    return first(getXpRecords(reusable)).getRecord('xpToShow')


def getTotalFreeXPToShow(reusable):
    return first(getFreeXpRecords(reusable)).getRecord('freeXP')


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
    if hasPremium:
        return getCreditsToShow(reusable)[0]
    records = getCreditsRecords(reusable).main
    return records.getRecord('credits', 'originalCreditsToDraw')


def getCreditsRecords(reusable):
    personalResults = reusable.personal
    base, premium, gold, additional, baseWithWotPlus, premiumWithWotPlus = first(personalResults.getMoneyRecords())
    if personalResults.hasAnyPremium:
        creditRecords, alternativeRecords = premium, base
        creditRecordsWithWotPlus, alternativeRecordsWithWotPlus = premiumWithWotPlus, baseWithWotPlus
    else:
        creditRecords, alternativeRecords = base, premium
        creditRecordsWithWotPlus, alternativeRecordsWithWotPlus = baseWithWotPlus, premiumWithWotPlus
    return FinancialRecords(main=creditRecords, additional=additional, alternative=alternativeRecords, extra=gold, mainWithWotPlus=creditRecordsWithWotPlus, alternativeWithWotPlus=alternativeRecordsWithWotPlus)


def getXpRecords(reusable):
    personalResults = reusable.personal
    baseXP, premiumXP, _, _, baseXPWithWotPlus, premiumXPWithWotPlus, _, _ = first(personalResults.getXPRecords())
    if personalResults.hasAnyPremium:
        xp, alternativeXp = premiumXP, baseXP
        xpWithWotPlus, alternativeXpWithWotPlus = premiumXPWithWotPlus, baseXPWithWotPlus
    else:
        xp, alternativeXp = baseXP, premiumXP
        xpWithWotPlus, alternativeXpWithWotPlus = baseXPWithWotPlus, premiumXPWithWotPlus
    return FinancialRecords(main=xp, alternative=alternativeXp, mainWithWotPlus=xpWithWotPlus, alternativeWithWotPlus=alternativeXpWithWotPlus, additional=None, extra=None)


def getFreeXpRecords(reusable):
    personalResults = reusable.personal
    _, _, baseFreeXP, premiumFreeXP, _, _, baseFreeXPWithWotPlus, premiumFreeXPWithWotPlus = first(personalResults.getXPRecords())
    if personalResults.hasAnyPremium:
        freeXp, alternativeFreeXp = premiumFreeXP, baseFreeXP
        freeXpWithWotPlus, alternativeWithWotPlus = premiumFreeXPWithWotPlus, baseFreeXPWithWotPlus
    else:
        freeXp, alternativeFreeXp = baseFreeXP, premiumFreeXP
        freeXpWithWotPlus, alternativeWithWotPlus = baseFreeXPWithWotPlus, premiumFreeXPWithWotPlus
    return FinancialRecords(main=freeXp, alternative=alternativeFreeXp, mainWithWotPlus=freeXpWithWotPlus, alternativeWithWotPlus=alternativeWithWotPlus, additional=None, extra=None)


def hasAogasFine(reusable):
    factor = 'aogasFactor10'
    return getCreditsRecords(reusable).main.getFactor(factor) < 1 or getXpRecords(reusable).main.getFactor(factor) < 1
