# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/details.py
import operator
import BigWorld
from constants import IGR_TYPE
from gui import makeHtmlString
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_results.components import base
from gui.battle_results.components import style
from gui.shared.formatters import icons
from gui.shared.money import Currency
from helpers import i18n
from shared_utils import findFirst

class _GainResourceInBattleItem(base.StatsItem):
    __slots__ = ('__records', '__method')

    def __init__(self, records, method, field, *path):
        super(_GainResourceInBattleItem, self).__init__(field, *path)
        self.__records = records
        self.__method = method

    def _convert(self, value, reusable):
        personal = reusable.personal
        baseRecords, premiumRecords = findFirst(None, operator.methodcaller(self.__method)(personal), (None, None))[:2]
        resource = 0
        if baseRecords is not None and not personal.avatar.hasPenalties():
            if reusable.isPostBattlePremium:
                records = premiumRecords
            else:
                records = baseRecords
            for append, name in self.__records:
                if append:
                    resource += records.getRecord(name)
                resource -= records.getRecord(name)

        return BigWorld.wg_getIntegralFormat(resource)


class GainCreditsInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCreditsInBattleItem, self).__init__(((True, 'credits'), (True, 'originalCreditsToDraw')), 'getMoneyRecords', field, *path)


class GainCrystalInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCrystalInBattleItem, self).__init__(((True, Currency.CRYSTAL),), 'getCrystalRecords', field, *path)


class GainXPInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainXPInBattleItem, self).__init__(((True, 'xpToShow'),), 'getXPRecords', field, *path)


class BaseCreditsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        canBeFaded = not reusable.isPostBattlePremium and reusable.canResourceBeFaded
        for records in reusable.personal.getBaseCreditsRecords():
            value = style.makeCreditsLabel(records.getRecord('credits', 'originalCreditsToDraw'), canBeFaded=canBeFaded)
            self.addNextComponent(base.DirectStatsItem('', value))


class PremiumCreditsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        canBeFaded = reusable.isPostBattlePremium and reusable.canResourceBeFaded
        isDiffShow = reusable.canUpgradeToPremium
        for records in reusable.personal.getMoneyRecords():
            baseCredits, premiumCredits = records[:2]
            value = premiumCredits.getRecord('credits', 'originalCreditsToDraw')
            if isDiffShow and value > 0:
                value -= baseCredits.getRecord('credits', 'originalCreditsToDraw')
            value = style.makeCreditsLabel(value, canBeFaded=canBeFaded, isDiff=isDiffShow)
            self.addNextComponent(base.DirectStatsItem('', value))


class XPTitleBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        showSquadLabels, squadHasBonus = reusable.getPersonalSquadFlags()
        for records in reusable.personal.getBaseXPRecords():
            factor = records.getFactor('dailyXPFactor10')
            if factor == 1 and showSquadLabels and squadHasBonus:
                result = i18n.makeString(BATTLE_RESULTS.COMMON_DETAILS_XPTITLESQUAD, img=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_PREBATTLEINVITEICON_1))
            else:
                result = i18n.makeString(BATTLE_RESULTS.COMMON_DETAILS_XPTITLE)
            if factor > 1:
                result = ' '.join((result, i18n.makeString(BATTLE_RESULTS.COMMON_DETAILS_XPTITLEFIRSTVICTORY, factor)))
            self.addNextComponent(base.DirectStatsItem('', result))


class BaseXPBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPremuim = not reusable.isPostBattlePremium and reusable.canResourceBeFaded
        for records in reusable.personal.getBaseXPRecords():
            value = style.makeXpLabel(records.getRecord('xpToShow'), canBeFaded=isPremuim)
            self.addNextComponent(base.DirectStatsItem('', value))


class PremiumXPBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        canBeFaded = reusable.isPostBattlePremium and reusable.canResourceBeFaded
        isDiffShow = reusable.canUpgradeToPremium
        for records in reusable.personal.getXPRecords():
            baseXP, premiumXP = records[:2]
            xp = premiumXP.getRecord('xpToShow')
            if isDiffShow:
                value = xp - baseXP.getRecord('xpToShow')
            else:
                value = xp
            value = style.makeXpLabel(value, canBeFaded=canBeFaded, isDiff=isDiffShow)
            self.addNextComponent(base.DirectStatsItem('', value))


class _EconomicsDetailsBlock(base.StatsBlock):
    __slots__ = ('isPremium', 'canResourceBeFaded', 'igrType', 'penaltyDetails')

    def __init__(self, meta=None, field='', *path):
        super(_EconomicsDetailsBlock, self).__init__(meta, field, *path)
        self.isPremium = False
        self.canResourceBeFaded = True
        self.penaltyDetails = None
        self.igrType = IGR_TYPE.NONE
        return

    def _addEmptyRow(self):
        self.addNextComponent(style.EmptyStatRow())

    def _addStatsRow(self, label, column1=None, column2=None, column3=None, column4=None, htmlKey=''):
        value = style.makeStatRow(label, column1=column1, column2=column2, column3=column3, column4=column4, htmlKey=htmlKey)
        self.addNextComponent(base.DirectStatsItem('', value))

    def _addAOGASFactor(self, baseRecords, allColumns=True):
        factor = baseRecords.getFactor('aogasFactor10')
        if factor < 1:
            value = style.makeAOGASFactorValue(factor)
            if allColumns:
                self._addStatsRow('aogasFactor', column1=value, column2=value, column3=value, column4=value)
            else:
                self._addStatsRow('aogasFactor', column1=value, column3=value)
            return True
        else:
            return False


class MoneyDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        baseCredits, premiumCredits, goldRecords, autoRecords = result
        isTotalShown = False
        self.__addBaseCredits(baseCredits, premiumCredits)
        isTotalShown |= self.__addStatsItemIfExists('newYear', baseCredits, premiumCredits, 'newYearCredits', 'newYearCreditsFactor')
        isTotalShown |= self.__addStatsItemIfExists('noPenalty', baseCredits, premiumCredits, 'achievementCredits')
        isTotalShown |= self.__addStatsItemIfExists('boosters', baseCredits, premiumCredits, 'boosterCredits', 'boosterCreditsFactor100')
        isTotalShown |= self.__addStatsItemIfExists('battlePayments', baseCredits, premiumCredits, 'orderCreditsFactor100')
        isTotalShown |= self.__addEventsMoney(baseCredits, premiumCredits, goldRecords)
        self._addEmptyRow()
        self.__addViolationPenalty()
        isTotalShown |= self.__addStatsItem('friendlyFirePenalty', baseCredits, premiumCredits, 'originalCreditsPenalty', 'originalCreditsContributionOut')
        isTotalShown |= self.__addStatsItem('friendlyFireCompensation', baseCredits, premiumCredits, 'originalCreditsContributionIn')
        self._addEmptyRow()
        isTotalShown |= self.__addAOGASFactor(baseCredits)
        if isTotalShown:
            self.__addBattleResults(baseCredits, premiumCredits, goldRecords)
            self._addEmptyRow()
        self.__addStatsItem('autoRepair', autoRecords, autoRecords, 'autoRepairCost')
        self.__addAutoCompletion('autoLoad', autoRecords, 'autoLoadCredits', 'autoLoadGold')
        self.__addAutoCompletion('autoEquip', autoRecords, 'autoEquipCredits', 'autoEquipGold')
        self._addEmptyRow()
        self.__addTotalResults(baseCredits, premiumCredits, goldRecords, autoRecords)

    def __addStatsItem(self, label, baseRecords, premiumRecords, *names):
        baseValue = baseRecords.getRecord(*names)
        premiumValue = premiumRecords.getRecord(*names)
        baseLabel = style.makeCreditsLabel(baseValue, canBeFaded=not self.isPremium)
        premiumLabel = style.makeCreditsLabel(premiumValue, canBeFaded=self.isPremium)
        self._addStatsRow(label, column1=baseLabel, column3=premiumLabel)
        return baseValue != 0 or premiumValue != 0

    def __addNewYearCreditsIfExists(self, baseRecords, premiumRecords):
        baseValue = baseRecords.getRecord('newYearCredits', 'newYearCreditsFactor')
        premiumValue = premiumRecords.getRecord('newYearCredits', 'newYearCreditsFactor')
        result = False
        if baseValue or premiumValue:
            result = True
            baseValue = style.makeCreditsLabel(baseValue, canBeFaded=not self.isPremium)
            premiumValue = style.makeCreditsLabel(premiumValue, canBeFaded=self.isPremium)
            self._addStatsRow('newYear', column1=baseValue, column3=premiumValue)
        return result

    def __addStatsItemIfExists(self, label, baseRecords, premiumRecords, *names):
        baseValue = baseRecords.getRecord(*names)
        premiumValue = premiumRecords.getRecord(*names)
        result = False
        if baseValue or premiumValue:
            result = True
            baseValue = style.makeCreditsLabel(baseValue, canBeFaded=not self.isPremium)
            premiumValue = style.makeCreditsLabel(premiumValue, canBeFaded=self.isPremium)
            self._addStatsRow(label, column1=baseValue, column3=premiumValue)
        return result

    def __addBaseCredits(self, baseRecords, premiumRecords):
        baseCredits = baseRecords.getRecord('originalCredits')
        baseCredits += baseRecords.getRecord('originalCreditsToDraw')
        baseCredits -= baseRecords.getRecord('achievementCredits')
        premiumCredits = premiumRecords.getRecord('originalCredits', 'appliedPremiumCreditsFactor10')
        premiumCredits += premiumRecords.getRecord('originalCreditsToDraw')
        premiumCredits -= premiumRecords.getRecord('achievementCredits')
        self._addStatsRow('base', column1=style.makeCreditsLabel(baseCredits, canBeFaded=not self.isPremium), column3=style.makeCreditsLabel(premiumCredits, canBeFaded=self.isPremium))

    def __addEventsMoney(self, baseCredits, premiumCredits, goldRecords):
        baseEventCredits = baseCredits.findRecord('eventCreditsList_') + baseCredits.findRecord('eventCreditsFactor100List_')
        premiumEventCredits = premiumCredits.findRecord('eventCreditsList_') + premiumCredits.findRecord('eventCreditsFactor100List_')
        baseEventGold = goldRecords.findRecord('eventGoldList_')
        result = False
        if baseEventCredits or premiumEventCredits or baseEventGold:
            result = True
            columns = {}
            if baseEventCredits:
                columns['column1'] = style.makeCreditsLabel(baseEventCredits, canBeFaded=not self.isPremium)
            if premiumEventCredits:
                columns['column3'] = style.makeCreditsLabel(premiumEventCredits, canBeFaded=self.isPremium)
            if baseEventGold:
                columns['column2'] = style.makeGoldLabel(baseEventGold, canBeFaded=not self.isPremium)
                columns['column4'] = style.makeGoldLabel(baseEventGold, canBeFaded=self.isPremium)
            self._addStatsRow('event', **columns)
        return result

    def __addViolationPenalty(self):
        if self.penaltyDetails is not None:
            name, penalty = self.penaltyDetails
            penalty = style.makePercentLabel(penalty)
            value = style.makeStatRow('fairPlayViolation/{}'.format(name), column1=penalty, column3=penalty)
            self.addNextComponent(base.DirectStatsItem('', value))
        return

    def __addAOGASFactor(self, baseRecords):
        result = self._addAOGASFactor(baseRecords, allColumns=False)
        if result:
            self._addEmptyRow()
        return result

    def __addBattleResults(self, baseRecords, premiumRecords, goldRecords):
        baseCredits = baseRecords.getRecord('credits', 'originalCreditsToDraw')
        premiumCredits = premiumRecords.getRecord('credits', 'originalCreditsToDraw')
        baseCreditsLabel = style.makeCreditsLabel(baseCredits, canBeFaded=not self.isPremium)
        premiumCreditsLabel = style.makeCreditsLabel(premiumCredits, canBeFaded=self.isPremium)
        gold = goldRecords.getRecord('gold')
        if gold != 0:
            baseGoldLabel = style.makeGoldLabel(gold, canBeFaded=not self.isPremium)
            premiumGoldLabel = style.makeGoldLabel(gold, canBeFaded=self.isPremium)
        else:
            baseGoldLabel = None
            premiumGoldLabel = None
        self._addStatsRow('intermediateTotal', column1=baseCreditsLabel, column3=premiumCreditsLabel, column2=baseGoldLabel, column4=premiumGoldLabel)
        return

    def __addAutoCompletion(self, label, autoRecords, creditsRecord, goldRecord):
        credit = autoRecords.getRecord(creditsRecord)
        gold = autoRecords.getRecord(goldRecord)
        columns = {'column1': style.makeCreditsLabel(credit, canBeFaded=not self.isPremium),
         'column3': style.makeCreditsLabel(credit, canBeFaded=self.isPremium)}
        if gold:
            columns.update({'column2': style.makeGoldLabel(gold, canBeFaded=not self.isPremium),
             'column4': style.makeGoldLabel(gold, canBeFaded=self.isPremium)})
        self._addStatsRow(label, **columns)

    def __addTotalResults(self, baseCredits, premiumCredits, goldRecords, autoRecords):
        baseCanBeFaded = not self.isPremium and self.canResourceBeFaded
        premiumCanBeFaded = self.isPremium and self.canResourceBeFaded
        autoCredits = autoRecords.getRecord('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits')
        autoGold = autoRecords.getRecord('autoLoadGold', 'autoEquipGold')
        columns = {'column1': style.makeCreditsLabel(baseCredits.getRecord('credits', 'originalCreditsToDraw') + autoCredits, canBeFaded=baseCanBeFaded),
         'column3': style.makeCreditsLabel(premiumCredits.getRecord('credits', 'originalCreditsToDraw') + autoCredits, canBeFaded=premiumCanBeFaded),
         'column2': style.makeGoldLabel(goldRecords.getRecord('gold') + autoGold, canBeFaded=not self.isPremium),
         'column4': style.makeGoldLabel(goldRecords.getRecord('gold') + autoGold, canBeFaded=self.isPremium)}
        self._addStatsRow('total', htmlKey='lightText', **columns)


class XPDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        baseXP, premiumXP, baseFreeXP, premiumFreeXP = result
        self.__addBaseXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addComplexXPsItemIfExists('noPenalty', baseXP, premiumXP, baseFreeXP, premiumFreeXP, 'achievementXP', 'achievementFreeXP')
        self.__addNewYearXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addXPsItem('friendlyFirePenalty', baseXP, premiumXP, 'originalXPPenalty')
        if reusable.common.arenaVisitor.gui.isInEpicRange():
            self.__addXPsItem('playerRankXP', baseXP, premiumXP, 'playerRankXPFactor100')
        self.__addIGRFactor(baseXP)
        self.__addDailyXPFactor(baseXP)
        self.__addBoosterXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addXPsItemIfExists('tacticalTraining', baseXP, premiumXP, 'orderXPFactor100')
        self.__addFreeXPsItemIfExists('militaryManeuvers', baseFreeXP, premiumFreeXP, 'orderFreeXPFactor100')
        self.__addEventXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addReferralSystemFactor(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addComplexXPsItemIfExists('premiumVehicleXP', baseXP, premiumXP, baseFreeXP, premiumFreeXP, 'premiumVehicleXPFactor100', 'premiumVehicleXPFactor100')
        if reusable.getPersonalSquadFlags()[0]:
            self.__getSquadXPDetails(baseXP, premiumXP)
        self._addAOGASFactor(baseXP)
        rows = self.getNextComponentIndex()
        if rows < 3 or rows < 7:
            self._addEmptyRow()
        self.__addXPsViolationPenalty()
        self.__addTotalResults(baseXP, premiumXP, baseFreeXP, premiumFreeXP)

    def __addXPsItem(self, label, baseXP, premiumXP, xpRecord):
        columns = {'column1': style.makeXpLabel(baseXP.getRecord(xpRecord), canBeFaded=not self.isPremium),
         'column3': style.makeXpLabel(premiumXP.getRecord(xpRecord), canBeFaded=self.isPremium)}
        self._addStatsRow(label, **columns)

    def __addFreeXPsItem(self, label, baseFreeXP, premiumFreeXP, freeXPRecord):
        columns = {'column2': style.makeFreeXpLabel(baseFreeXP.getRecord(freeXPRecord), canBeFaded=not self.isPremium),
         'column4': style.makeFreeXpLabel(premiumFreeXP.getRecord(freeXPRecord), canBeFaded=self.isPremium)}
        self._addStatsRow(label, **columns)

    def __addComplexXPsItem(self, label, baseXP, premiumXP, baseFreeXP, premiumFreeXP, xpRecord, freeXPRecord, htmlKey=''):
        baseCanBeFaded = not self.isPremium
        premiumCanBeFaded = self.isPremium
        columns = {'column1': style.makeXpLabel(baseXP.getRecord(xpRecord), canBeFaded=baseCanBeFaded),
         'column3': style.makeXpLabel(premiumXP.getRecord(xpRecord), canBeFaded=premiumCanBeFaded),
         'column2': style.makeFreeXpLabel(baseFreeXP.getRecord(freeXPRecord), canBeFaded=baseCanBeFaded),
         'column4': style.makeFreeXpLabel(premiumFreeXP.getRecord(freeXPRecord), canBeFaded=premiumCanBeFaded)}
        self._addStatsRow(label, htmlKey=htmlKey, **columns)

    def __addXPsItemIfExists(self, label, baseXP, premiumXP, xpRecord):
        if baseXP.getRecord(xpRecord) or premiumXP.getRecord(xpRecord):
            self.__addXPsItem(label, baseXP, premiumXP, xpRecord)

    def __addFreeXPsItemIfExists(self, label, baseFreeXP, premiumFreeXP, freeXPRecord):
        if baseFreeXP.getRecord(freeXPRecord) or premiumFreeXP.getRecord(freeXPRecord):
            self.__addFreeXPsItem(label, baseFreeXP, premiumFreeXP, freeXPRecord)

    def __addComplexXPsItemIfExists(self, label, baseXP, premiumXP, baseFreeXP, premiumFreeXP, xpRecord, freeXPRecord):
        value = baseXP.getRecord(xpRecord)
        value += premiumXP.getRecord(xpRecord)
        value += baseFreeXP.getRecord(freeXPRecord)
        value += premiumFreeXP.getRecord(freeXPRecord)
        if value:
            self.__addComplexXPsItem(label, baseXP, premiumXP, baseFreeXP, premiumFreeXP, xpRecord, freeXPRecord)

    def __addBaseXPs(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        if baseXP.getRecord('isHighScope'):
            label, htmlKey = ('', 'xpRecord')
        else:
            label, htmlKey = ('base', '')
        baseXPValue = baseXP.getRecord('originalXP')
        baseXPValue -= baseXP.getRecord('achievementXP')
        premiumXPValue = premiumXP.getRecord('originalXP', 'appliedPremiumXPFactor10')
        premiumXPValue -= premiumXP.getRecord('achievementXP')
        baseFreeXPValue = baseFreeXP.getRecord('originalFreeXP')
        baseFreeXPValue -= baseFreeXP.getRecord('achievementFreeXP')
        premiumFreeXPValue = premiumFreeXP.getRecord('originalFreeXP', 'appliedPremiumXPFactor10')
        premiumFreeXPValue -= premiumFreeXP.getRecord('achievementFreeXP')
        baseCanBeFaded = not self.isPremium
        premiumCanBeFaded = self.isPremium
        columns = {'column1': style.makeXpLabel(baseXPValue, canBeFaded=baseCanBeFaded),
         'column3': style.makeXpLabel(premiumXPValue, canBeFaded=premiumCanBeFaded),
         'column2': style.makeFreeXpLabel(baseFreeXPValue, canBeFaded=baseCanBeFaded),
         'column4': style.makeFreeXpLabel(premiumFreeXPValue, canBeFaded=premiumCanBeFaded)}
        self._addStatsRow(label, htmlKey=htmlKey, **columns)

    def __addBoosterXPs(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseXPValue = baseXP.getRecord('boosterXP', 'boosterXPFactor100')
        premiumXPValue = premiumXP.getRecord('boosterXP', 'boosterXPFactor100')
        baseFreeXPValue = baseFreeXP.getRecord('boosterFreeXP', 'boosterFreeXPFactor100')
        premiumFreeXPValue = premiumFreeXP.getRecord('boosterFreeXP', 'boosterFreeXPFactor100')
        if baseXPValue or premiumXPValue or baseFreeXPValue or premiumFreeXPValue:
            baseCanBeFaded = not self.isPremium
            premiumCanBeFaded = self.isPremium
            columns = {'column1': style.makeXpLabel(baseXPValue, canBeFaded=baseCanBeFaded),
             'column3': style.makeXpLabel(premiumXPValue, canBeFaded=premiumCanBeFaded),
             'column2': style.makeFreeXpLabel(baseFreeXPValue, canBeFaded=baseCanBeFaded),
             'column4': style.makeFreeXpLabel(premiumFreeXPValue, canBeFaded=premiumCanBeFaded)}
            self._addStatsRow('boosters', **columns)

    def __addNewYearXPs(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseXPValue = baseXP.getRecord('newYearXp') + baseXP.findRecord('newYearXpFactor')
        premiumXPValue = premiumXP.getRecord('newYearXp') + premiumXP.findRecord('newYearXpFactor')
        baseFreeXPValue = baseFreeXP.getRecord('newYearFreeXp') + baseFreeXP.findRecord('newYearFreeXpFactor')
        premiumFreeXPValue = premiumFreeXP.getRecord('newYearFreeXp') + premiumFreeXP.findRecord('newYearFreeXpFactor')
        if baseXPValue or premiumXPValue or baseFreeXPValue or premiumFreeXPValue:
            baseCanBeFaded = not self.isPremium
            premiumCanBeFaded = self.isPremium
            columns = {'column1': style.makeXpLabel(baseXPValue, canBeFaded=baseCanBeFaded),
             'column3': style.makeXpLabel(premiumXPValue, canBeFaded=premiumCanBeFaded),
             'column2': style.makeFreeXpLabel(baseFreeXPValue, canBeFaded=baseCanBeFaded),
             'column4': style.makeFreeXpLabel(premiumFreeXPValue, canBeFaded=premiumCanBeFaded)}
            self._addStatsRow('newYear', **columns)

    def __addEventXPs(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseXPValue = baseXP.findRecord('eventXPList_') + baseXP.findRecord('eventXPFactor100List_')
        premiumXPValue = premiumXP.findRecord('eventXPList_') + premiumXP.findRecord('eventXPFactor100List_')
        baseFreeXPValue = baseFreeXP.findRecord('eventFreeXPList_') + baseFreeXP.findRecord('eventFreeXPFactor100List_')
        premiumFreeXPValue = premiumFreeXP.findRecord('eventFreeXPList_') + premiumFreeXP.findRecord('eventFreeXPFactor100List_')
        if baseXPValue or premiumXPValue or baseFreeXPValue or premiumFreeXPValue:
            baseCanBeFaded = not self.isPremium
            premiumCanBeFaded = self.isPremium
            columns = {'column1': style.makeXpLabel(baseXPValue, canBeFaded=baseCanBeFaded),
             'column3': style.makeXpLabel(premiumXPValue, canBeFaded=premiumCanBeFaded),
             'column2': style.makeFreeXpLabel(baseFreeXPValue, canBeFaded=baseCanBeFaded),
             'column4': style.makeFreeXpLabel(premiumFreeXPValue, canBeFaded=premiumCanBeFaded)}
            self._addStatsRow('event', **columns)

    def __addXPsViolationPenalty(self):
        if self.penaltyDetails is not None:
            name, penalty = self.penaltyDetails
            penalty = style.makePercentLabel(penalty)
            self._addStatsRow('fairPlayViolation/{}'.format(name), column1=penalty, column2=penalty, column3=penalty, column4=penalty)
        return

    def __addIGRFactor(self, baseXP):
        factor = baseXP.getFactor('igrXPFactor10')
        if factor > 1:
            icon = style.makeIGRIcon(self.igrType)
            value = style.makeIGRBonusValue(factor)
            self.addNextComponent(style.StatRow(style.makeIGRBonusLabel(''), style.makeIGRBonusLabel(icon), style.WIDE_STAT_ROW, column1=value, column2=value, column3=value, column4=value))

    def __addDailyXPFactor(self, baseXP):
        factor = baseXP.getFactor('dailyXPFactor10')
        if factor > 1:
            value = style.makeDailyXPFactorValue(factor)
            self._addStatsRow('firstWin', column1=value, column2=value, column3=value, column4=value)

    def __getSquadXPDetails(self, baseXP, premiumXP):
        squadXP = baseXP.getRecord('squadXPFactor100')
        premiumSquadXP = premiumXP.getRecord('squadXPFactor100')
        baseLabel = style.makeXpLabel(squadXP, canBeFaded=not self.isPremium)
        premiumLabel = style.makeXpLabel(premiumSquadXP, canBeFaded=not self.isPremium)
        if squadXP < 0 or premiumSquadXP < 0:
            label = 'squadXPPenalty'
            if self.isPremium:
                baseLabel = None
            else:
                premiumLabel = None
        else:
            label = 'squadXP'
        columns = {'column1': baseLabel,
         'column3': premiumLabel}
        self._addStatsRow(label, **columns)
        return

    def __addReferralSystemFactor(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        if baseXP.getFactor('refSystemXPFactor10') > 1:
            self.__addComplexXPsItem('referralBonus', baseXP, premiumXP, baseFreeXP, premiumFreeXP, 'refSystemXPFactor10', 'refSystemXPFactor10')

    def __addTotalResults(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseCanBeFaded = not self.isPremium and self.canResourceBeFaded
        premiumCanBeFaded = self.isPremium and self.canResourceBeFaded
        columns = {'column1': style.makeXpLabel(baseXP.getRecord('xp'), canBeFaded=baseCanBeFaded),
         'column3': style.makeXpLabel(premiumXP.getRecord('xp'), canBeFaded=premiumCanBeFaded),
         'column2': style.makeFreeXpLabel(baseFreeXP.getRecord('freeXP'), canBeFaded=baseCanBeFaded),
         'column4': style.makeFreeXpLabel(premiumFreeXP.getRecord('freeXP'), canBeFaded=premiumCanBeFaded)}
        self._addStatsRow('total', htmlKey='lightText', **columns)


class CrystalDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        crystalTotal = 0
        crystalAchive = 0
        for details in result:
            achievementName, value = details
            if achievementName == 'originalCrystal':
                if value > 0:
                    crystalTotal += value
                    self._addRecord(i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_CRYSTAL_TOTAL), value)
            crystalAchive += value

        if crystalAchive > 0:
            self._addRecord(i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_CRYSTAL_ACHIEVEMENT), crystalAchive)
        crystalTotal += crystalAchive
        if crystalTotal > 0:
            self.addNextComponent(style.EmptyStatRow())
            i18nText = i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_TOTAL)
            totalStr = makeHtmlString('html_templates:lobby/battle_results', 'lightText', {'value': i18nText})
            self._addRecord(totalStr, crystalTotal)

    def _addRecord(self, res, value):
        self.addNextComponent(style.StatRow(res, res, style.SMALL_STAT_LINE, column1=style.makeCrystalLabel(value)))


class _TotalEconomicsDetailsBlock(base.StatsBlock):
    __slots__ = ('__iteratorName', '__blockClass')

    def __init__(self, iterator, block, meta=None, field='', *path):
        super(_TotalEconomicsDetailsBlock, self).__init__(meta, field, *path)
        self.__iteratorName = iterator
        self.__blockClass = block

    def setRecord(self, result, reusable):
        igrType = reusable.getPlayerInfo().igrType
        personal = reusable.personal
        penaltyDetails = personal.avatar.getPenaltyDetails()
        isPremuim = reusable.isPostBattlePremium
        canResourceBeFaded = reusable.canResourceBeFaded
        for records in operator.methodcaller(self.__iteratorName)(personal):
            block = self.__blockClass(base.ListMeta(registered=True))
            block.isPremium = isPremuim
            block.canResourceBeFaded = canResourceBeFaded
            block.igrType = igrType
            block.penaltyDetails = penaltyDetails
            block.setRecord(records, reusable)
            self.addNextComponent(block)


class TotalMoneyDetailsBlock(_TotalEconomicsDetailsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(TotalMoneyDetailsBlock, self).__init__('getMoneyRecords', MoneyDetailsBlock, meta, field, *path)


class TotalXPDetailsBlock(_TotalEconomicsDetailsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(TotalXPDetailsBlock, self).__init__('getXPRecords', XPDetailsBlock, meta, field, *path)


class TotalCrystalDetailsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        personal = reusable.personal
        block = CrystalDetailsBlock(base.ListMeta(registered=True))
        block.setRecord(personal.getCrystalDetails(), reusable)
        self.addNextComponent(block)
