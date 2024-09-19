# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/getter.py
import typing
from fairplay_violation_types import FAIRPLAY_VIOLATIONS_NAMES
from gui.battle_results.presenter.getter.detailed_stats_credits import getCreditFields
from gui.battle_results.presenter.getter.detailed_stats_crystals import getCrystalFields
from gui.battle_results.presenter.getter.detailed_stats_xp import getXPFields
from gui.battle_results.presenter.getter.team_stats import getTeamStats
from gui.battle_results.presenter.getter.premium_benefits import getPremiumBenefits
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.presenter.getter.detailed_stats_credits import CreditEarningsField, CreditsTotalField, CreditsEarnedField
    from gui.battle_results.presenter.getter.detailed_stats_crystals import CrystalsField, CrystalsTotalField
    from gui.battle_results.presenter.getter.detailed_stats_xp import XPEarnedField

def createFieldsGetter():
    return PostbattleFieldsGetter(creditFields=getCreditFields(), crystalFields=getCrystalFields(), xpFields=getXPFields(), teamStatsFields=getTeamStats(), premiumBenefitFields=getPremiumBenefits())


class _CreditsGetter(object):
    __slots__ = ('__detailedStatsCredits',)

    def __init__(self, creditsFields):
        self.__detailedStatsCredits = creditsFields

    def getEarnedCredits(self):
        return self.__detailedStatsCredits.earned

    def getCreditEarnings(self, reusable):
        creditEarningsFields = self.__detailedStatsCredits.earnings.detailed.bonuses + _processFinesFields(reusable, *self.__detailedStatsCredits.earnings.detailed.fines) + (self.__detailedStatsCredits.earnings.total,)
        for field in creditEarningsFields:
            yield field

    def getTotalCreditEarnings(self):
        return self.__detailedStatsCredits.earnings.total

    def getTotalBonusesCredits(self):
        return self.__detailedStatsCredits.earnings.detailed.totalBonuses

    def getCreditExpenses(self):
        creditExpensesFields = self.__detailedStatsCredits.expenses.detailed + (self.__detailedStatsCredits.expenses.total,)
        for field in creditExpensesFields:
            yield field

    def getTotalCreditExpenses(self):
        return self.__detailedStatsCredits.expenses.total

    def getTotalCredits(self):
        return self.__detailedStatsCredits.total

    def getPiggyBankCredits(self):
        return self.__detailedStatsCredits.piggyBank

    def getAlternativeTotalCredits(self):
        return self.__detailedStatsCredits.alternativeTotal


class _CrystalsGetter(object):
    __slots__ = ('__detailedStatsCrystals',)

    def __init__(self, crystalFields):
        self.__detailedStatsCrystals = crystalFields

    def getEarnedCrystals(self):
        return self.__detailedStatsCrystals.earned

    def getCrystalsEarnings(self):
        crystalEarningsFields = self.__detailedStatsCrystals.earnings.detailed + (self.__detailedStatsCrystals.earnings.total,)
        for field in crystalEarningsFields:
            yield field

    def getTotalCrystalsEarnings(self):
        return self.__detailedStatsCrystals.earnings.total

    def getCrystalsExpenses(self):
        crystalExpensesFields = self.__detailedStatsCrystals.expenses.detailed + (self.__detailedStatsCrystals.expenses.total,)
        for field in crystalExpensesFields:
            yield field

    def getTotalCrystalsExpenses(self):
        return self.__detailedStatsCrystals.expenses.total

    def getTotalCrystals(self):
        return self.__detailedStatsCrystals.total


class _XPGetter(object):
    __slots__ = ('__detailedStatsXP',)

    def __init__(self, xpFields):
        self.__detailedStatsXP = xpFields

    def getXP(self, reusable, isRecord):
        earned = self.getEarnedXP(isRecord)
        xpFields = (earned,) + self.__detailedStatsXP.earnings.bonuses + _processFinesFields(reusable, *self.__detailedStatsXP.earnings.fines) + (self.__detailedStatsXP.total,)
        for field in xpFields:
            yield field

    def getEarnedXP(self, isRecord):
        return self.__detailedStatsXP.earned.earnedRecord if isRecord else self.__detailedStatsXP.earned.earned

    def getBonusesXP(self):
        return self.__detailedStatsXP.earnings.bonuses

    def getBonusesTotalXP(self):
        return self.__detailedStatsXP.bonusesTotal

    def getTotalXP(self):
        return self.__detailedStatsXP.total

    def getAlternativeTotalXP(self):
        return self.__detailedStatsXP.alternativeTotal


class PostbattleFieldsGetter(object):
    __slots__ = ('__detailedStatsCredits', '__detailedStatsCrystals', '__detailedStatsXP', '__teamStats', '__premiumBenefits')

    def __init__(self, creditFields, crystalFields, xpFields, teamStatsFields, premiumBenefitFields):
        self.__detailedStatsCredits = _CreditsGetter(creditFields)
        self.__detailedStatsCrystals = _CrystalsGetter(crystalFields)
        self.__detailedStatsXP = _XPGetter(xpFields)
        self.__teamStats = teamStatsFields
        self.__premiumBenefits = premiumBenefitFields

    @property
    def crystals(self):
        return self.__detailedStatsCrystals

    @property
    def credits(self):
        return self.__detailedStatsCredits

    @property
    def xp(self):
        return self.__detailedStatsXP

    def clear(self):
        self.__detailedStatsCredits = None
        self.__detailedStatsCrystals = None
        self.__detailedStatsXP = None
        self.__teamStats = None
        self.__premiumBenefits = None
        return

    def getTeamStats(self, isSPG, isPersonal, isRoleExp):
        roleExpFields = (self.__teamStats.expSegments.total,
         self.__teamStats.expSegments.attack,
         self.__teamStats.expSegments.assist,
         self.__teamStats.expSegments.role)
        spgFields = (self.__teamStats.other.stunNum,
         self.__teamStats.other.stunDuration,
         self.__teamStats.other.damageAssistedStun,
         self.__teamStats.other.damageAssistedStunSelf)
        personalFields = (self.__teamStats.other.damageAssistedSelf, self.__teamStats.other.damageAssistedStunSelf)
        nonPersonalFields = (self.__teamStats.other.damageAssisted, self.__teamStats.other.damageAssistedStun)

        def filterFunc(field):
            return (field not in spgFields or isSPG) and (field not in personalFields or isPersonal) and (field not in nonPersonalFields or not isPersonal) and (field not in roleExpFields or isRoleExp)

        teamStats = self.__teamStats.expSegments + self.__teamStats.shots + self.__teamStats.damageDealt + self.__teamStats.hitsReceived + self.__teamStats.other + self.__teamStats.time
        for field in filter(filterFunc, teamStats):
            yield field

    def getPremiumBenefits(self):
        for field in self.__premiumBenefits:
            yield field


def _processFinesFields(reusable, aogasField, deserterField, suicideField, afkField, friendlyFire, friendlyFireSPG):
    _, vehicle = first(reusable.personal.getVehicleItemsIterator())
    isSPG = vehicle.type == VEHICLE_CLASS_NAME.SPG
    friendlyFireField = friendlyFireSPG if isSPG else friendlyFire
    penaltyNamesToFieldNames = {FAIRPLAY_VIOLATIONS_NAMES[0]: deserterField,
     FAIRPLAY_VIOLATIONS_NAMES[1]: suicideField,
     FAIRPLAY_VIOLATIONS_NAMES[2]: afkField,
     FAIRPLAY_VIOLATIONS_NAMES[3]: deserterField,
     FAIRPLAY_VIOLATIONS_NAMES[4]: afkField}
    penalty = reusable.personal.avatar.getPenaltyDetails()
    penaltyField = penaltyNamesToFieldNames[penalty[0]] if penalty else None
    return filter(None, (aogasField, penaltyField, friendlyFireField))
