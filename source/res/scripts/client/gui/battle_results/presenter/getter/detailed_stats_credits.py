# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/detailed_stats_credits.py
from collections import namedtuple
from enum import Enum
import typing
from gui.battle_results.presenter.getter.detailed_stats import CurrencyField, EventField, StatsCurrencyBlock
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_record_model import DetailsRecordModel
from gui.impl.gen.resources import R
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.battle_results.reusable.records import ReplayRecords

class _CreditIndexes(Enum):
    EARNED = 0
    TOTAL = 1
    PIGGY_BANK = 2
    ALTERNATIVE = 3


class _CreditEarningsBlockIndexes(Enum):
    BONUSES = 0
    FINES = 1
    TOTAL_EARNED = 2


class _CreditExpensesBlockIndexes(Enum):
    EXPENSES = 0
    TOTAL_EXPENSES = 1


_CREDIT_STRINGS = R.strings.postbattle_screen.detailsStats.credits
_CREDIT_TOOLTIP_STRING = R.strings.postbattle_screen.tooltip.financeDetails
DetailedStatsCreditFields = namedtuple('creditFields', ('earned', 'expenses', 'earnings', 'total', 'piggyBank', 'alternativeTotal'))
DetailedStatsCreditExpenses = namedtuple('creditFields', ('autoRepair', 'autoLoad', 'autoEquip', 'autoBoosters'))
DetailedStatsCreditEarnings = namedtuple('creditEarnings', ('bonuses', 'totalBonuses', 'fines'))
DetailedStatsCreditBonuses = namedtuple('creditBonuses', ('achievementCredits', 'eventCredits', 'contributionCredits', 'premiumCredits', 'squadCredits', 'orderCredits', 'referralCredits', 'boosterCredits'))
DetailedStatsCreditFines = namedtuple('creditFines', ('aogasCreditsFactor', 'deserterCreditsPenalty', 'suicideCreditsPenalty', 'afkCreditsPenalty', 'friendlyFireCreditsPenalty', 'friendlyFireSPGCreditsPenalty'))

class CreditEarningsField(CurrencyField):
    __slots__ = ()

    def __init__(self, stringID, blockIdx, recordItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CreditEarningsField, self).__init__(stringID, blockIdx, recordItems, CurrencyModel.CREDITS, tags, isShown, tooltipString)

    def getFieldValues(self, record):
        return self._getRecord(self._getValue(record))

    def _getValue(self, record):
        return record.getRecord(*self._recordItems)


class CreditsEarnedField(CreditEarningsField):
    __slots__ = ('_recordSubtractItems',)

    def __init__(self, stringID, blockIdx, recordItems, recordSubtractItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CreditsEarnedField, self).__init__(stringID, blockIdx, recordItems, tags, isShown, tooltipString)
        self._recordSubtractItems = recordSubtractItems

    def _getValue(self, record):
        return record.getRecord(*self._recordItems) - record.getRecord(*self._recordSubtractItems)


class CreditsTotalField(CurrencyField):
    __slots__ = ('_additionalRecordItems', '_recordItems')

    def __init__(self, stringID, blockIdx, recordItems, additionalRecordItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(CreditsTotalField, self).__init__(stringID, blockIdx, recordItems, CurrencyModel.CREDITS, tags, isShown, tooltipString)
        self._additionalRecordItems = additionalRecordItems
        self._recordItems = recordItems

    def getFieldValues(self, record, additionalRecord):
        return self._getRecord(self._getValue(record, additionalRecord))

    def _getValue(self, record, additionalRecord):
        return record.getRecord(*self._recordItems) + additionalRecord.getRecord(*self._additionalRecordItems)


def getCreditFields():
    return DetailedStatsCreditFields(earned=_getEarnedCredits(), expenses=_getCreditExpenses(), earnings=_getCreditEarnings(), total=_getTotalCredits(), piggyBank=_getPiggyBankCredits(), alternativeTotal=_getAlternativeTotalCredits())


def _getEarnedCredits():
    return CreditsEarnedField(blockIdx=_CreditIndexes.EARNED, stringID=_CREDIT_STRINGS.earned(), tooltipString=_CREDIT_STRINGS.earned.descr(), tags=(DetailsRecordModel.EARNED,), recordItems=('originalCredits', 'originalCreditsToDraw'), recordSubtractItems=('achievementCredits',), isShown=True)


def _getCreditExpenses():
    return StatsCurrencyBlock(detailed=_getDetailedCreditExpenses(), total=_getTotalCreditExpenses())


def _getDetailedCreditExpenses():
    return DetailedStatsCreditExpenses(autoRepair=CreditEarningsField(blockIdx=_CreditExpensesBlockIndexes.EXPENSES, stringID=_CREDIT_STRINGS.expenses.autoRepair(), tooltipString=_CREDIT_STRINGS.expenses.autoRepair.descr(), recordItems=('autoRepairCost',), isShown=True), autoLoad=CreditEarningsField(blockIdx=_CreditExpensesBlockIndexes.EXPENSES, stringID=_CREDIT_STRINGS.expenses.autoLoad(), tooltipString=_CREDIT_STRINGS.expenses.autoLoad.descr(), recordItems=('autoLoadCredits',), isShown=True), autoEquip=CreditEarningsField(blockIdx=_CreditExpensesBlockIndexes.EXPENSES, stringID=_CREDIT_STRINGS.expenses.autoEquip(), tooltipString=_CREDIT_STRINGS.expenses.autoEquip.descr(), recordItems=('autoEquipCredits',), isShown=True), autoBoosters=CreditEarningsField(blockIdx=_CreditExpensesBlockIndexes.EXPENSES, stringID=_CREDIT_STRINGS.expenses.autoBoosters(), tooltipString=_CREDIT_STRINGS.expenses.autoBoosters.descr(), recordItems=('autoBoostersCredits',), isShown=True))


def _getTotalCreditExpenses():
    return CreditEarningsField(blockIdx=_CreditExpensesBlockIndexes.TOTAL_EXPENSES, stringID=_CREDIT_STRINGS.expenses.total(), tooltipString=_CREDIT_STRINGS.expenses.total.descr(), tags=(DetailsRecordModel.SUBGROUP_TOTAL,), recordItems=('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits', 'autoBoostersCredits'), isShown=True)


def _getDetailedCreditEarnings():
    return DetailedStatsCreditEarnings(bonuses=_getCreditBonuses(), fines=_getCreditFines(), totalBonuses=_getCreditsBonusesTotal())


def _getCreditEarnings():
    return StatsCurrencyBlock(detailed=_getDetailedCreditEarnings(), total=_getTotalCreditEarnings())


def _getCreditBonuses():
    return DetailedStatsCreditBonuses(achievementCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.noPenalty(), tooltipString=_CREDIT_STRINGS.bonuses.noPenalty.descr(), recordItems=('achievementCredits',)), eventCredits=EventField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.event(), tooltipString=_CREDIT_STRINGS.bonuses.event.descr(), recordItems=('eventCreditsList_', 'eventCreditsFactor100List_'), valueType=CurrencyModel.CREDITS), contributionCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.friendlyFireCompensation(), tooltipString=_CREDIT_STRINGS.bonuses.friendlyFireCompensation.descr(), recordItems=('originalCreditsContributionIn', 'originalCreditsContributionInSquad')), premiumCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.premiumAccount(), tooltipString=_CREDIT_STRINGS.bonuses.premiumAccount.descr(), recordItems=('appliedPremiumCreditsFactor100',)), squadCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.squad(), tooltipString=_CREDIT_STRINGS.bonuses.squad.descr(), recordItems=('originalPremSquadCredits', 'originalCreditsToDrawSquad')), orderCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.battlePayments(), tooltipString=_CREDIT_STRINGS.bonuses.battlePayments.descr(), recordItems=('orderCreditsFactor100',)), referralCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.referralBonus(), tooltipString=_CREDIT_STRINGS.bonuses.referralBonus.descr(), recordItems=('referral20CreditsFactor100',)), boosterCredits=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.BONUSES, stringID=_CREDIT_STRINGS.bonuses.boosters(), tooltipString=_CREDIT_STRINGS.bonuses.boosters.descr(), recordItems=('boosterCredits', 'boosterCreditsFactor100')))


def _getCreditFines():
    return DetailedStatsCreditFines(aogasCreditsFactor=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.aogasFactor(), tooltipString=_CREDIT_STRINGS.fines.aogasFactor.descr(), recordItems=('aogasFactor10',)), deserterCreditsPenalty=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.deserter(), tooltipString=_CREDIT_STRINGS.fines.deserter.descr(), recordItems=('fairplayFactor10',)), suicideCreditsPenalty=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.suicide(), tooltipString=_CREDIT_STRINGS.fines.suicide.descr(), recordItems=('fairplayFactor10',)), afkCreditsPenalty=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.afk(), tooltipString=_CREDIT_STRINGS.fines.afk.descr(), recordItems=('fairplayFactor10',)), friendlyFireCreditsPenalty=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.friendlyFirePenalty(), tooltipString=_CREDIT_STRINGS.fines.friendlyFirePenalty.descr(), recordItems=('originalCreditsPenalty', 'originalCreditsContributionOut', 'originalCreditsPenaltySquad', 'originalCreditsContributionOutSquad')), friendlyFireSPGCreditsPenalty=CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.FINES, stringID=_CREDIT_STRINGS.fines.friendlyFireSPGPenalty(), tooltipString=_CREDIT_STRINGS.fines.friendlyFireSPGPenalty.descr(), recordItems=('originalCreditsPenalty', 'originalCreditsContributionOut', 'originalCreditsPenaltySquad', 'originalCreditsContributionOutSquad')))


def _getTotalCreditEarnings():
    return CreditEarningsField(blockIdx=_CreditEarningsBlockIndexes.TOTAL_EARNED, stringID=_CREDIT_STRINGS.totalEarnings(), tooltipString=_CREDIT_STRINGS.totalEarnings.descr(), tags=(DetailsRecordModel.SUBGROUP_TOTAL,), recordItems=('credits', 'originalCreditsToDraw', 'originalCreditsToDrawSquad'), isShown=True)


def _getCreditsBonusesTotal():
    return CreditsEarnedField(blockIdx=_CreditEarningsBlockIndexes.TOTAL_EARNED, stringID=_CREDIT_TOOLTIP_STRING.bonuses(), recordItems=('credits', 'achievementCredits'), recordSubtractItems=('originalCredits', 'originalCreditsToDraw'), isShown=True)


def _getTotalCredits():
    return CreditsTotalField(blockIdx=_CreditIndexes.TOTAL, stringID=_CREDIT_STRINGS.total(), tooltipString=_CREDIT_STRINGS.total.descr(), tags=(DetailsRecordModel.TOTAL,), recordItems=('credits', 'originalCreditsToDraw', 'originalCreditsToDrawSquad'), additionalRecordItems=('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits', 'autoBoostersCredits'), isShown=True)


def _getPiggyBankCredits():
    return CreditEarningsField(blockIdx=_CreditIndexes.PIGGY_BANK, stringID=_CREDIT_STRINGS.piggyBankInfo(), tooltipString=_CREDIT_STRINGS.piggyBankInfo.descr(), recordItems=('piggyBank',))


def _getAlternativeTotalCredits():
    return CreditsTotalField(blockIdx=_CreditIndexes.ALTERNATIVE, stringID=_CREDIT_TOOLTIP_STRING.alternativeTotal.credits(), tags=(DetailsRecordModel.ALTERNATIVE_TOTAL,), recordItems=('credits', 'originalCreditsToDraw', 'originalCreditsToDrawSquad'), additionalRecordItems=('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits', 'autoBoostersCredits'))
