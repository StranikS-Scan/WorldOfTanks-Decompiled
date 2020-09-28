# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/detailed_stats_xp.py
from collections import namedtuple
from enum import Enum
import typing
from frameworks.wulf import Array
from gui.battle_results.presenter.getter.detailed_stats import CurrencyField, DetailedStatsField
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.postbattle.details_record_model import DetailsRecordModel
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.records import ReplayRecords

class _XPBlockIndexes(Enum):
    EARNED = 0
    BONUSES = 1
    FINES = 2
    TOTAL = 3
    ALTERNATIVE = 4


_XP_STRINGS = R.strings.postbattle_screen.detailsStats.xp
_XP_TOOLTIP_STRING = R.strings.postbattle_screen.tooltip.financeDetails
DetailedStatsXPFields = namedtuple('xpFields', ('earned', 'earnings', 'bonusesTotal', 'total', 'alternativeTotal'))
DetailedStatsEarnedXP = namedtuple('earnedXP', ('earned', 'earnedRecord'))
DetailedStatsXPEarnings = namedtuple('xpEarnings', ('bonuses', 'fines'))
DetailedStatsXPBonuses = namedtuple('xpBonuses', ('achievementXP', 'premiumXP', 'igrXP', 'squadXP', 'dailyXP', 'additionalXP', 'referralXP', 'premiumVehicleXP', 'orderXP', 'boosterXP', 'orderFreeXP', 'rankXP', 'eventsXP'))
DetailedStatsXPFines = namedtuple('xpFines', ('aogasXPFactor', 'deserterXPPenalty', 'suicideXPPenalty', 'afkXPPenalty', 'friendlyFireXPPenalty', 'friendlyFireSPGXPPenalty'))

class XPSingleValueField(CurrencyField):
    __slots__ = ()

    def getFieldValues(self, xpRecord, freeXPRecord):
        record = xpRecord if self._valueType == CurrencyModel.XP else freeXPRecord
        return self._getRecord(self._getValue(record))

    def _getValue(self, record):
        return record.getRecord(*self._recordItems)


class XPField(DetailedStatsField):
    __slots__ = ('_xpRecordItems', '_freeXPRecordItems')

    def __init__(self, stringID, blockIdx, xpRecordItems, freeXPRecordItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(XPField, self).__init__(stringID, blockIdx, tags, isShown, tooltipString)
        self._xpRecordItems = xpRecordItems
        self._freeXPRecordItems = freeXPRecordItems

    def _getRecord(self, values):
        if all((not value for value in values)) and not self._isShown:
            return None
        else:
            record = Array()
            record.reserve(2)
            for value, valueType in zip(values, (CurrencyModel.XP, CurrencyModel.FREE_XP)):
                valueModel = CurrencyModel()
                valueModel.setAmount(value)
                valueModel.setType(valueType)
                record.addViewModel(valueModel)

            return record


class XPEventField(XPField):
    __slots__ = ()

    def getFieldValues(self, xpRecord, freeXPRecord):
        return self._getRecord(self._getValue(xpRecord, freeXPRecord))

    def _getValue(self, xpRecord, freeXPRecord):
        xpValue = sum([ xpRecord.findRecord(recordItem) for recordItem in self._xpRecordItems ])
        freeXPValue = sum([ freeXPRecord.findRecord(recordItem) for recordItem in self._freeXPRecordItems ])
        return (xpValue, freeXPValue)


class XPEarningsField(XPField):
    __slots__ = ()

    def getFieldValues(self, xpRecord, freeXPRecord):
        return self._getRecord(self._getValue(xpRecord, freeXPRecord))

    def _getValue(self, xpRecord, freeXPRecord):
        xpValue = xpRecord.getRecord(*self._xpRecordItems)
        freeXPValue = freeXPRecord.getRecord(*self._freeXPRecordItems)
        return (xpValue, freeXPValue)


class XPEarnedField(XPEarningsField):
    __slots__ = ('_xpSubtractItems', '_freeXPSubtractItems')

    def __init__(self, stringID, blockIdx, xpRecordItems, freeXPRecordItems, xpSubtractItems, freeXPSubtractItems, tags=None, isShown=False, tooltipString=R.invalid()):
        super(XPEarnedField, self).__init__(stringID, blockIdx, xpRecordItems, freeXPRecordItems, tags, isShown, tooltipString)
        self._xpSubtractItems = xpSubtractItems
        self._freeXPSubtractItems = freeXPSubtractItems

    def _getValue(self, xpRecord, freeXPRecord):
        xpValue = xpRecord.getRecord(*self._xpRecordItems) - xpRecord.getRecord(*self._xpSubtractItems)
        freeXPValue = freeXPRecord.getRecord(*self._freeXPRecordItems) - freeXPRecord.getRecord(*self._freeXPSubtractItems)
        return (xpValue, freeXPValue)


def getXPFields():
    return DetailedStatsXPFields(earned=_getEarnedXP(), earnings=_getXPEarnings(), bonusesTotal=_getXPBonusesTotal(), total=_getXPTotal(), alternativeTotal=_getAlternativeTotalXP())


def _getEarnedXP():
    return DetailedStatsEarnedXP(earned=XPEarnedField(blockIdx=_XPBlockIndexes.EARNED, stringID=_XP_STRINGS.earned(), tooltipString=_XP_STRINGS.earned.descr(), tags=(DetailsRecordModel.EARNED,), xpRecordItems=('originalXP',), freeXPRecordItems=('originalFreeXP',), xpSubtractItems=('achievementXP',), freeXPSubtractItems=('achievementFreeXP',), isShown=True), earnedRecord=XPEarnedField(blockIdx=_XPBlockIndexes.EARNED, stringID=_XP_STRINGS.earned(), tooltipString=_XP_STRINGS.earned.descr(), tags=(DetailsRecordModel.EARNED_RECORD, DetailsRecordModel.EARNED), xpRecordItems=('originalXP',), freeXPRecordItems=('originalFreeXP',), xpSubtractItems=('achievementXP',), freeXPSubtractItems=('achievementFreeXP',), isShown=True))


def _getXPTotal():
    return XPEarningsField(blockIdx=_XPBlockIndexes.TOTAL, stringID=_XP_STRINGS.total(), tooltipString=_XP_STRINGS.total.descr(), tags=(DetailsRecordModel.TOTAL,), xpRecordItems=('xp',), freeXPRecordItems=('freeXP',), isShown=True)


def _getXPBonusesTotal():
    return XPEarnedField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_TOOLTIP_STRING.bonuses(), tags=(DetailsRecordModel.EARNED_RECORD,), xpRecordItems=('xp', 'achievementXP'), freeXPRecordItems=('freeXP', 'achievementFreeXP'), xpSubtractItems=('originalXP',), freeXPSubtractItems=('originalFreeXP',), isShown=True)


def _getXPEarnings():
    return DetailedStatsXPEarnings(bonuses=_getXPBonuses(), fines=_getXPFines())


def _getXPBonuses():
    return DetailedStatsXPBonuses(achievementXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.noPenalty(), tooltipString=_XP_STRINGS.bonuses.noPenalty.descr(), xpRecordItems=('achievementXP',), freeXPRecordItems=('achievementFreeXP',)), premiumXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.premiumAcc(), tooltipString=_XP_STRINGS.bonuses.premiumAcc.descr(), xpRecordItems=('appliedPremiumXPFactor100',), freeXPRecordItems=('appliedPremiumXPFactor100',)), igrXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.igrBonus(), tooltipString=_XP_STRINGS.bonuses.igrBonus.descr(), xpRecordItems=('igrXPFactor10',), freeXPRecordItems=('igrXPFactor10',)), squadXP=XPSingleValueField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.squadBonus(), tooltipString=_XP_STRINGS.bonuses.squadBonus.descr(), recordItems=('squadXPFactor100',), valueType=CurrencyModel.XP), dailyXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.firstBattleBonus(), tooltipString=_XP_STRINGS.bonuses.firstBattleBonus.descr(), xpRecordItems=('dailyXPFactor10',), freeXPRecordItems=('dailyXPFactor10',)), additionalXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.xpBonus(), tooltipString=_XP_STRINGS.bonuses.xpBonus.descr(), xpRecordItems=('additionalXPFactor10',), freeXPRecordItems=('additionalXPFactor10',)), referralXP=XPSingleValueField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.referralBonus(), tooltipString=_XP_STRINGS.bonuses.referralBonus.descr(), recordItems=('referral20XPFactor100',), valueType=CurrencyModel.XP), premiumVehicleXP=XPSingleValueField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.premVehicle(), tooltipString=_XP_STRINGS.bonuses.premVehicle.descr(), recordItems=('premiumVehicleXPFactor100',), valueType=CurrencyModel.XP), orderXP=XPSingleValueField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.tacticalTraining(), tooltipString=_XP_STRINGS.bonuses.tacticalTraining.descr(), recordItems=('orderXPFactor100',), valueType=CurrencyModel.XP), boosterXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.boosters(), tooltipString=_XP_STRINGS.bonuses.boosters.descr(), xpRecordItems=('boosterXP', 'boosterXPFactor100'), freeXPRecordItems=('boosterFreeXP', 'boosterFreeXPFactor100')), orderFreeXP=XPSingleValueField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.militaryManeuvers(), tooltipString=_XP_STRINGS.bonuses.militaryManeuvers.descr(), recordItems=('orderFreeXPFactor100',), valueType=CurrencyModel.FREE_XP), rankXP=XPEarningsField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.playerRankXP(), xpRecordItems=('playerRankXPFactor100',), freeXPRecordItems=('playerRankXPFactor100',)), eventsXP=XPEventField(blockIdx=_XPBlockIndexes.BONUSES, stringID=_XP_STRINGS.bonuses.events(), tooltipString=_XP_STRINGS.bonuses.events.descr(), xpRecordItems=('eventXPList_', 'eventXPFactor100List_'), freeXPRecordItems=('eventFreeXPList_', 'eventFreeXPFactor100List_')))


def _getXPFines():
    return DetailedStatsXPFines(aogasXPFactor=XPEarningsField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.aogasFactor(), tooltipString=_XP_STRINGS.fines.aogasFactor.descr(), xpRecordItems=('aogasFactor10',), freeXPRecordItems=('aogasFactor10',)), deserterXPPenalty=XPEarningsField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.deserter(), tooltipString=_XP_STRINGS.fines.deserter.descr(), xpRecordItems=('fairplayFactor10',), freeXPRecordItems=('fairplayFactor10',)), suicideXPPenalty=XPEarningsField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.suicide(), tooltipString=_XP_STRINGS.fines.suicide.descr(), xpRecordItems=('fairplayFactor10',), freeXPRecordItems=('fairplayFactor10',)), afkXPPenalty=XPEarningsField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.afk(), tooltipString=_XP_STRINGS.fines.afk.descr(), xpRecordItems=('fairplayFactor10',), freeXPRecordItems=('fairplayFactor10',)), friendlyFireXPPenalty=XPSingleValueField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.friendlyFirePenalty(), tooltipString=_XP_STRINGS.fines.friendlyFirePenalty.descr(), recordItems=('originalXPPenalty', 'originalXPContributionOut', 'originalXPPenaltySquad', 'originalXPContributionOutSquad'), valueType=CurrencyModel.XP), friendlyFireSPGXPPenalty=XPSingleValueField(blockIdx=_XPBlockIndexes.FINES, stringID=_XP_STRINGS.fines.friendlyFireSPGPenalty(), tooltipString=_XP_STRINGS.fines.friendlyFireSPGPenalty.descr(), recordItems=('originalXPPenalty', 'originalXPContributionOut', 'originalXPPenaltySquad', 'originalXPContributionOutSquad'), valueType=CurrencyModel.XP))


def _getAlternativeTotalXP():
    return XPEarningsField(blockIdx=_XPBlockIndexes.ALTERNATIVE, stringID=_XP_TOOLTIP_STRING.alternativeTotal.xp(), tags=(DetailsRecordModel.ALTERNATIVE_TOTAL,), xpRecordItems=('xp',), freeXPRecordItems=('freeXP',), isShown=True)
