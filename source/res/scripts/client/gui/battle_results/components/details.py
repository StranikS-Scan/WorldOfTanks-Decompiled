# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/details.py
import operator
from constants import IGR_TYPE, PREMIUM_TYPE
from gui import makeHtmlString
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.components import base
from gui.battle_results.components import style
from gui.battle_results.reusable.records import convertFactorToPercent
from gui.impl import backport
from gui.impl.backport.backport_system_locale import getIntegralFormat
from gui.impl.gen.resources import R
from gui.impl.lobby.premacc import premacc_helpers
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.icons import makeImageTag
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, dependency
from shared_utils import first
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class _GainResourceInBattleItem(base.StatsItem):
    __slots__ = ('__records', '__method', '__styler')

    def __init__(self, records, method, styler, field, *path):
        super(_GainResourceInBattleItem, self).__init__(field, *path)
        self.__records = records
        self.__method = method
        self.__styler = styler

    def _convert(self, value, reusable):
        personal = reusable.personal
        baseRecords, premiumRecords = first(operator.methodcaller(self.__method)(personal), default=(None, None))[:2]
        resource = 0
        if baseRecords is not None and not personal.avatar.hasPenalties():
            if reusable.hasAnyPremiumInPostBattle:
                records = premiumRecords
            else:
                records = baseRecords
            for append, name in self.__records:
                if append:
                    resource += records.getRecord(name)
                resource -= records.getRecord(name)

        return self.__styler(resource)


class GainCreditsInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCreditsInBattleItem, self).__init__(((True, 'credits'), (True, 'originalCreditsToDraw')), 'getMoneyRecords', getIntegralFormat, field, *path)


class GainCreditsValueInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCreditsValueInBattleItem, self).__init__(((True, 'credits'), (True, 'originalCreditsToDraw')), 'getMoneyRecords', (lambda x: x), field, *path)


class GainCrystalInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCrystalInBattleItem, self).__init__(((True, Currency.CRYSTAL),), 'getCrystalRecords', getIntegralFormat, field, *path)


class GainCrystalValueInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainCrystalValueInBattleItem, self).__init__(((True, Currency.CRYSTAL),), 'getCrystalRecords', (lambda x: x), field, *path)


class GainXPInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainXPInBattleItem, self).__init__(((True, 'xpToShow'),), 'getXPRecords', getIntegralFormat, field, *path)


class GainXPValueInBattleItem(_GainResourceInBattleItem):
    __slots__ = ()

    def __init__(self, field, *path):
        super(GainXPValueInBattleItem, self).__init__(((True, 'xpToShow'),), 'getXPRecords', (lambda x: x), field, *path)


class TotalBRReward(base.StatsItem):
    __slots__ = ('__record',)

    def __init__(self, record, field, *path):
        super(TotalBRReward, self).__init__(field, *path)
        self.__record = record

    def _convert(self, value, reusable):
        infoAvatar = value['avatar']
        return infoAvatar.get(self.__record)


class BRCredits(TotalBRReward):
    __slots__ = ()

    def __init__(self, field, *path):
        super(BRCredits, self).__init__('credits', field, *path)


class BRXp(TotalBRReward):
    __slots__ = ()

    def __init__(self, field, *path):
        super(BRXp, self).__init__('xp', field, *path)


class BRCrystal(TotalBRReward):
    __slots__ = ()

    def __init__(self, field, *path):
        super(BRCrystal, self).__init__('crystal', field, *path)


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
        canBeFaded = reusable.hasAnyPremiumInPostBattle and reusable.canResourceBeFaded
        isDiffShow = reusable.canUpgradeToPremiumPlus
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
            factor = int(records.getFactor('dailyXPFactor10'))
            if factor == 1 and showSquadLabels and squadHasBonus:
                value = i18n.makeString(backport.text(R.strings.battle_results.common.details.xpTitleSquad()), img=icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.prebattleInviteIcon_1())))
            else:
                value = backport.text(R.strings.battle_results.common.details.xpTitle())
            if factor > 1:
                value = ' '.join((value, icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.dyn('bonus_x{}'.format(factor))()), 46, 18)))
            self.addNextComponent(base.DirectStatsItem('', value))


class XPTitleTooltipBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        showSquadLabels, squadHasBonus = reusable.getPersonalSquadFlags()
        for records in reusable.personal.getBaseXPRecords():
            factor = int(records.getFactor('dailyXPFactor10'))
            value = None
            if factor == 1 and showSquadLabels and squadHasBonus:
                value = backport.text(R.strings.battle_results.common.tooltip.xpTitleSquad())
            self.addNextComponent(base.DirectStatsItem('', value))

        return


class BaseXPBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPremium = not reusable.hasAnyPremiumInPostBattle and reusable.canResourceBeFaded
        for records in reusable.personal.getBaseXPRecords():
            value = style.makeXpLabel(records.getRecord('xpToShow'), canBeFaded=isPremium)
            self.addNextComponent(base.DirectStatsItem('', value))


class PremiumXPBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        canBeFaded = reusable.hasAnyPremiumInPostBattle and reusable.canResourceBeFaded
        isDiffShow = reusable.canUpgradeToPremiumPlus
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
    __slots__ = ('premiumMask', 'hasAnyPremium', 'canResourceBeFaded', 'igrType', 'penaltyDetails')

    def __init__(self, meta=None, field='', *path):
        super(_EconomicsDetailsBlock, self).__init__(meta, field, *path)
        self.hasAnyPremium = False
        self.canResourceBeFaded = True
        self.penaltyDetails = None
        self.igrType = IGR_TYPE.NONE
        return

    def _addEmptyRow(self):
        self.addNextComponent(style.EmptyStatRow())

    def _addStatsRow(self, label, labelArgs=None, column1=None, column2=None, column3=None, column4=None, htmlKey=''):
        value = style.makeStatRow(label, labelArgs=labelArgs, column1=column1, column2=column2, column3=column3, column4=column4, htmlKey=htmlKey)
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
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __intermediateTotalRecords = ('credits', 'originalCreditsToDraw', 'originalCreditsToDrawSquad')

    def setRecord(self, result, reusable):
        baseCredits, premiumCredits, goldRecords, additionalRecords = result
        isTotalShown = False
        self.__addBaseCredits(baseCredits, premiumCredits)
        showSquadLabels, _ = reusable.getPersonalSquadFlags()
        if showSquadLabels:
            self.__addSquadBonus(baseCredits, premiumCredits)
        isTotalShown |= self.__addStatsItemIfExists('newYear', baseCredits, premiumCredits, True, None, 'newYearCreditsFactor')
        isTotalShown |= self.__addStatsItemIfExists('noPenalty', baseCredits, premiumCredits, False, None, 'achievementCredits')
        isTotalShown |= self.__addStatsItemIfExists('boosters', baseCredits, premiumCredits, False, None, 'boosterCredits', 'boosterCreditsFactor100')
        isTotalShown |= self.__addStatsItemIfExists('battlePayments', baseCredits, premiumCredits, False, None, 'orderCreditsFactor100')
        isTotalShown |= self.__addEventsMoney(baseCredits, premiumCredits, goldRecords)
        isTotalShown |= self.__addReferralSystemFactor(baseCredits, premiumCredits)
        self._addEmptyRow()
        self.__addViolationPenalty()
        isTotalShown |= self.__addStatsItem('friendlyFirePenalty', baseCredits, premiumCredits, 'originalCreditsPenalty', 'originalCreditsContributionOut', 'originalCreditsPenaltySquad', 'originalCreditsContributionOutSquad')
        isTotalShown |= self.__addStatsItem('friendlyFireCompensation', baseCredits, premiumCredits, 'originalCreditsContributionIn', 'originalCreditsContributionInSquad')
        self._addEmptyRow()
        isTotalShown |= self.__addAOGASFactor(baseCredits)
        if isTotalShown:
            self.__addBattleResults(baseCredits, premiumCredits, goldRecords)
            self._addEmptyRow()
        self.__addStatsItem('autoRepair', additionalRecords, additionalRecords, 'autoRepairCost')
        self.__addAutoCompletion('autoLoad', additionalRecords, 'autoLoadCredits', 'autoLoadGold')
        self.__addAutoCompletion('autoEquip', additionalRecords, 'autoEquipCredits', 'autoEquipGold')
        self._addEmptyRow()
        self.__addTotalResults(baseCredits, premiumCredits, goldRecords, additionalRecords)
        self._addEmptyRow()
        if self.__isProperBonusType(reusable) or self.__isGoldPiggyBankAvailable(reusable):
            self.__addPiggyBankInfo(premiumCredits, additionalRecords, reusable)
        return

    def __addStatsItem(self, label, baseRecords, premiumRecords, *names):
        baseValue = baseRecords.getRecord(*names)
        premiumValue = premiumRecords.getRecord(*names)
        baseLabel = style.makeCreditsLabel(baseValue, canBeFaded=not self.hasAnyPremium)
        premiumLabel = style.makeCreditsLabel(premiumValue, canBeFaded=self.hasAnyPremium)
        self._addStatsRow(label, column1=baseLabel, column3=premiumLabel)
        return baseValue != 0 or premiumValue != 0

    def __addStatsItemIfExists(self, label, baseRecords, premiumRecords, acceptAllIfExist, labelArgs=None, *names):
        baseValue = baseRecords.getRecord(*names)
        premiumValue = premiumRecords.getRecord(*names)
        result = False
        if acceptAllIfExist:
            isToAdd = baseRecords.getFactor(*names) > 1.0 or premiumRecords.getFactor(*names) > 1.0
        else:
            isToAdd = baseValue or premiumValue
        if isToAdd:
            result = True
            baseValue = style.makeCreditsLabel(baseValue, canBeFaded=not self.hasAnyPremium)
            premiumValue = style.makeCreditsLabel(premiumValue, canBeFaded=self.hasAnyPremium)
            self._addStatsRow(label, labelArgs, column1=baseValue, column3=premiumValue)
        return result

    def __addBaseCredits(self, baseRecords, premiumRecords):
        baseCredits = baseRecords.getRecord('originalCredits')
        baseCredits += baseRecords.getRecord('originalCreditsToDraw')
        baseCredits -= baseRecords.getRecord('achievementCredits')
        premiumCredits = premiumRecords.getRecord('originalCredits', 'appliedPremiumCreditsFactor100')
        premiumCredits += premiumRecords.getRecord('originalCreditsToDraw')
        premiumCredits -= premiumRecords.getRecord('achievementCredits')
        self._addStatsRow('base', column1=style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium), column3=style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium))

    def __addSquadBonus(self, baseRecords, premiumRecords):
        baseCredits = baseRecords.getRecord('originalPremSquadCredits', 'originalCreditsToDrawSquad')
        premiumCredits = premiumRecords.getRecord('originalPremSquadCredits', 'originalCreditsToDrawSquad')
        if not self.hasAnyPremium and baseCredits or self.hasAnyPremium and premiumCredits:
            self._addStatsRow('squadBonus', column1=style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium), column3=style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium))

    def __addPiggyBankInfo(self, premiumRecords, additionalRecords, reusable):
        baseCredits = 0
        baseGold = 0
        premiumGold = 0
        goldGain = reusable.personal.getGoldBankGain()
        if self.hasAnyPremium:
            premiumCredits = additionalRecords.getRecord('piggyBank')
            premiumGold = goldGain
        else:
            piggyBankMultiplier = self.__lobbyContext.getServerSettings().getPiggyBankConfig().get('multiplier')
            premiumCredits = premiumRecords.getRecord('credits') * piggyBankMultiplier
            baseGold = goldGain
        column2 = None
        column4 = None
        if self.__lobbyContext.getServerSettings().isRenewableSubGoldReserveEnabled():
            column2 = style.makeGoldLabel(baseGold, canBeFaded=True, isDiff=baseGold > 0)
            column4 = style.makeGoldLabel(premiumGold, canBeFaded=True, isDiff=premiumGold > 0)
        self._addStatsRow('piggyBankInfo', column1=style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium, isDiff=baseCredits > 0), column2=column2, column3=style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium, isDiff=premiumCredits > 0), column4=column4)
        return

    def __addReferralSystemFactor(self, baseCredits, premiumCredits):
        referralFactor = baseCredits.getFactor('referral20CreditsFactor100')
        labelArgs = {'bonusFactor': convertFactorToPercent(referralFactor)}
        return self.__addStatsItemIfExists('referralBonus', baseCredits, premiumCredits, False, labelArgs, 'referral20CreditsFactor100')

    def __addEventsMoney(self, baseCredits, premiumCredits, goldRecords):
        baseEventCredits = baseCredits.findRecord('eventCreditsList_') + baseCredits.findRecord('eventCreditsFactor100List_')
        premiumEventCredits = premiumCredits.findRecord('eventCreditsList_') + premiumCredits.findRecord('eventCreditsFactor100List_')
        baseEventGold = goldRecords.findRecord('eventGoldList_')
        result = False
        if baseEventCredits or premiumEventCredits or baseEventGold:
            result = True
            columns = {}
            if baseEventCredits:
                columns['column1'] = style.makeCreditsLabel(baseEventCredits, canBeFaded=not self.hasAnyPremium)
            if premiumEventCredits:
                columns['column3'] = style.makeCreditsLabel(premiumEventCredits, canBeFaded=self.hasAnyPremium)
            if baseEventGold:
                columns['column2'] = style.makeGoldLabel(baseEventGold, canBeFaded=not self.hasAnyPremium)
                columns['column4'] = style.makeGoldLabel(baseEventGold, canBeFaded=self.hasAnyPremium)
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
        baseCredits = baseRecords.getRecord(*self.__intermediateTotalRecords)
        premiumCredits = premiumRecords.getRecord(*self.__intermediateTotalRecords)
        baseCreditsLabel = style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium)
        premiumCreditsLabel = style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium)
        gold = goldRecords.getRecord('gold')
        if gold != 0:
            baseGoldLabel = style.makeGoldLabel(gold, canBeFaded=not self.hasAnyPremium)
            premiumGoldLabel = style.makeGoldLabel(gold, canBeFaded=self.hasAnyPremium)
        else:
            baseGoldLabel = None
            premiumGoldLabel = None
        self._addStatsRow('intermediateTotal', column1=baseCreditsLabel, column3=premiumCreditsLabel, column2=baseGoldLabel, column4=premiumGoldLabel)
        return

    def __addAutoCompletion(self, label, additionalRecords, creditsRecord, goldRecord):
        credit = additionalRecords.getRecord(creditsRecord)
        gold = additionalRecords.getRecord(goldRecord)
        columns = {'column1': style.makeCreditsLabel(credit, canBeFaded=not self.hasAnyPremium),
         'column3': style.makeCreditsLabel(credit, canBeFaded=self.hasAnyPremium)}
        if gold:
            columns.update({'column2': style.makeGoldLabel(gold, canBeFaded=not self.hasAnyPremium),
             'column4': style.makeGoldLabel(gold, canBeFaded=self.hasAnyPremium)})
        self._addStatsRow(label, **columns)

    def __addTotalResults(self, baseCredits, premiumCredits, goldRecords, additionalRecords):
        baseCanBeFaded = not self.hasAnyPremium and self.canResourceBeFaded
        premiumCanBeFaded = self.hasAnyPremium and self.canResourceBeFaded
        autoCredits = additionalRecords.getRecord('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits')
        autoGold = additionalRecords.getRecord('autoLoadGold', 'autoEquipGold')
        columns = {'column1': style.makeCreditsLabel(baseCredits.getRecord(*self.__intermediateTotalRecords) + autoCredits, canBeFaded=baseCanBeFaded),
         'column3': style.makeCreditsLabel(premiumCredits.getRecord(*self.__intermediateTotalRecords) + autoCredits, canBeFaded=premiumCanBeFaded),
         'column2': style.makeGoldLabel(goldRecords.getRecord('gold') + autoGold, canBeFaded=not self.hasAnyPremium),
         'column4': style.makeGoldLabel(goldRecords.getRecord('gold') + autoGold, canBeFaded=self.hasAnyPremium)}
        self._addStatsRow('total', htmlKey='lightText', **columns)

    def __isProperBonusType(self, reusable):
        arenaTypes = self.__lobbyContext.getServerSettings().getPiggyBankConfig().get('arena', tuple())
        return reusable.common.arenaBonusType in arenaTypes

    def __isGoldPiggyBankAvailable(self, reusable):
        arenaTypes = self.__lobbyContext.getServerSettings().getArenaTypesWithGoldReserve()
        return reusable.common.arenaBonusType in arenaTypes


class XPDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        baseXP, premiumXP, baseFreeXP, premiumFreeXP = result
        self.__addBaseXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addComplexXPsItemIfExists('noPenalty', baseXP, premiumXP, baseFreeXP, premiumFreeXP, 'achievementXP', 'achievementFreeXP')
        self.__addNewYearXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        penaltyKey = 'friendlyFirePenalty'
        if reusable.common.arenaVisitor.gui.isRankedBattle():
            penaltyKey = 'friendlyFireRankedXpPenalty'
        self.__addXPsItem(penaltyKey, baseXP, premiumXP, 'originalXPPenalty')
        if reusable.common.arenaVisitor.gui.isInEpicRange():
            self.__addXPsItem('playerRankXP', baseXP, premiumXP, 'playerRankXPFactor100')
        self.__addIGRFactor(baseXP)
        self.__addDailyXPFactor(baseXP)
        self.__addAdditionalXPBonus(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addBoosterXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addXPsItemIfExists('tacticalTraining', baseXP, premiumXP, 'orderXPFactor100')
        self.__addFreeXPsItemIfExists('militaryManeuvers', baseFreeXP, premiumFreeXP, 'orderFreeXPFactor100')
        self.__addEventXPs(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self.__addReferralSystemFactor(baseXP, premiumXP)
        self.__addComplexXPsItemIfExists('premiumVehicleXP', baseXP, premiumXP, baseFreeXP, premiumFreeXP, 'premiumVehicleXPFactor100', 'premiumVehicleXPFactor100')
        showSquadLabels, _ = reusable.getPersonalSquadFlags()
        if showSquadLabels:
            self.__addSquadXPDetails(baseXP, premiumXP)
        self._addAOGASFactor(baseXP)
        if self.getNextComponentIndex() < 7:
            self._addEmptyRow()
        self.__addXPsViolationPenalty()
        self.__addTotalResults(baseXP, premiumXP, baseFreeXP, premiumFreeXP)
        self._addEmptyRow()

    def __addXPsItem(self, label, baseXP, premiumXP, xpRecord, labelArgs=None):
        columns = {'column1': style.makeXpLabel(baseXP.getRecord(xpRecord), canBeFaded=not self.hasAnyPremium),
         'column3': style.makeXpLabel(premiumXP.getRecord(xpRecord), canBeFaded=self.hasAnyPremium)}
        self._addStatsRow(label, labelArgs=labelArgs, **columns)

    def __addFreeXPsItem(self, label, baseFreeXP, premiumFreeXP, freeXPRecord):
        columns = {'column2': style.makeFreeXpLabel(baseFreeXP.getRecord(freeXPRecord), canBeFaded=not self.hasAnyPremium),
         'column4': style.makeFreeXpLabel(premiumFreeXP.getRecord(freeXPRecord), canBeFaded=self.hasAnyPremium)}
        self._addStatsRow(label, **columns)

    def __addComplexXPsItem(self, label, baseXP, premiumXP, baseFreeXP, premiumFreeXP, xpRecord, freeXPRecord, htmlKey=''):
        baseCanBeFaded = not self.hasAnyPremium
        premiumCanBeFaded = self.hasAnyPremium
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
        premiumXPValue = premiumXP.getRecord('originalXP', 'appliedPremiumXPFactor100')
        premiumXPValue -= premiumXP.getRecord('achievementXP')
        baseFreeXPValue = baseFreeXP.getRecord('originalFreeXP')
        baseFreeXPValue -= baseFreeXP.getRecord('achievementFreeXP')
        premiumFreeXPValue = premiumFreeXP.getRecord('originalFreeXP', 'appliedPremiumXPFactor100')
        premiumFreeXPValue -= premiumFreeXP.getRecord('achievementFreeXP')
        baseCanBeFaded = not self.hasAnyPremium
        premiumCanBeFaded = self.hasAnyPremium
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
            baseCanBeFaded = not self.hasAnyPremium
            premiumCanBeFaded = self.hasAnyPremium
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
        hasFactors = (rec.getFactor('newYearXpFactor') > 1.0 for rec in (baseXP,
         premiumXP,
         baseFreeXP,
         premiumFreeXP))
        hasFactors = any(hasFactors)
        if baseXPValue or premiumXPValue or baseFreeXPValue or premiumFreeXPValue or hasFactors:
            baseCanBeFaded = not self.hasAnyPremium
            premiumCanBeFaded = self.hasAnyPremium
            columns = {'column1': style.makeXpLabel(baseXPValue, canBeFaded=baseCanBeFaded),
             'column3': style.makeXpLabel(premiumXPValue, canBeFaded=premiumCanBeFaded),
             'column2': style.makeFreeXpLabel(baseFreeXPValue, canBeFaded=baseCanBeFaded),
             'column4': style.makeFreeXpLabel(premiumFreeXPValue, canBeFaded=premiumCanBeFaded)}
            self._addStatsRow('vehicleBranch', **columns)

    def __addEventXPs(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseXPValue = baseXP.findRecord('eventXPList_') + baseXP.findRecord('eventXPFactor1000List_')
        premiumXPValue = premiumXP.findRecord('eventXPList_') + premiumXP.findRecord('eventXPFactor1000List_')
        baseFreeXPValue = baseFreeXP.findRecord('eventFreeXPList_') + baseFreeXP.findRecord('eventFreeXPFactor100List_')
        premiumFreeXPValue = premiumFreeXP.findRecord('eventFreeXPList_') + premiumFreeXP.findRecord('eventFreeXPFactor100List_')
        if baseXPValue or premiumXPValue or baseFreeXPValue or premiumFreeXPValue:
            baseCanBeFaded = not self.hasAnyPremium
            premiumCanBeFaded = self.hasAnyPremium
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
            columns = self.__getFormattedColumnsWithFreeXP([factor] * 4)
            self._addStatsRow('firstWin', **columns)

    def __addAdditionalXPBonus(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):

        def getAdditionalXPFactor(item):
            factor = item.getFactor('additionalXPFactor10')
            return factor if factor > 1 else 0

        factors = tuple((getAdditionalXPFactor(xp) for xp in (baseXP,
         baseFreeXP,
         premiumXP,
         premiumFreeXP)))
        if any(factors):
            columns = self.__getFormattedColumnsWithFreeXP(factors)
            self._addStatsRow('additionalBonus', **columns)

    def __addSquadXPDetails(self, baseXP, premiumXP):
        squadXP = baseXP.getRecord('squadXPFactor100')
        premiumSquadXP = premiumXP.getRecord('squadXPFactor100')
        baseLabel = style.makeXpLabel(squadXP, canBeFaded=not self.hasAnyPremium)
        premiumLabel = style.makeXpLabel(premiumSquadXP, canBeFaded=not self.hasAnyPremium)
        if squadXP < 0 or premiumSquadXP < 0:
            label = 'squadXPPenalty'
            if self.hasAnyPremium:
                baseLabel = None
            else:
                premiumLabel = None
        else:
            label = 'squadXP'
        columns = {'column1': baseLabel,
         'column3': premiumLabel}
        self._addStatsRow(label, **columns)
        return

    def __addReferralSystemFactor(self, baseXP, premiumXP):
        referralFactor = baseXP.getFactor('referral20XPFactor100')
        if referralFactor > 0 and baseXP.getRecord('referral20XPFactor100'):
            labelArgs = {'bonusFactor': convertFactorToPercent(referralFactor)}
            self.__addXPsItem('referralBonus', baseXP, premiumXP, 'referral20XPFactor100', labelArgs=labelArgs)

    def __addTotalResults(self, baseXP, premiumXP, baseFreeXP, premiumFreeXP):
        baseCanBeFaded = not self.hasAnyPremium and self.canResourceBeFaded
        premiumCanBeFaded = self.hasAnyPremium and self.canResourceBeFaded
        columns = {'column1': style.makeXpLabel(baseXP.getRecord('xp'), canBeFaded=baseCanBeFaded),
         'column3': style.makeXpLabel(premiumXP.getRecord('xp'), canBeFaded=premiumCanBeFaded),
         'column2': style.makeFreeXpLabel(baseFreeXP.getRecord('freeXP'), canBeFaded=baseCanBeFaded),
         'column4': style.makeFreeXpLabel(premiumFreeXP.getRecord('freeXP'), canBeFaded=premiumCanBeFaded)}
        self._addStatsRow('total', htmlKey='lightText', **columns)

    @staticmethod
    def __getFormattedColumnsWithFreeXP(factors):
        return {'column{}'.format(n):style.makeMultiXPFactorValue(factor, useFreeXPStyle=not bool(n % 2)) for n, factor in enumerate(factors, 1)}


class CrystalDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        label = backport.text(R.strings.battle_results.details.calculations.crystal.total())
        earned = self.__addRecordField('originalCrystal', result, label)
        label = backport.text(R.strings.battle_results.details.calculations.crystal.events())
        earned += self.__addRecordField('events', result, label)
        label = backport.text(R.strings.battle_results.details.calculations.autoBoosters())
        expenses = self.__addRecordField('autoEquipCrystals', result, label)
        if earned or expenses:
            self.__addTotalResults(earned + expenses)

    def __addRecordField(self, key, result, label, force=False):
        value = result.getRecord(key)
        if force or value:
            self._addRecord(label, value)
        return value

    def __addTotalResults(self, value):
        self.addNextComponent(style.EmptyStatRow())
        i18nText = backport.text(R.strings.battle_results.details.calculations.total())
        totalStr = makeHtmlString('html_templates:lobby/battle_results', 'lightText', {'value': i18nText})
        self._addRecord(totalStr, value)

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
        hasAnyPremium = reusable.hasAnyPremiumInPostBattle
        canResourceBeFaded = reusable.canResourceBeFaded
        for records in operator.methodcaller(self.__iteratorName)(personal):
            block = self.__blockClass(base.ListMeta(registered=True))
            block.hasAnyPremium = hasAnyPremium
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
        for record in personal.getCrystalDetailsRecords():
            block = CrystalDetailsBlock(base.ListMeta(registered=True))
            block.setRecord(record, reusable)
            self.addNextComponent(block)


class PremiumBonusDetailsBlock(base.StatsBlock):
    __slots__ = ('description', 'bonusLeft', 'xpValue', 'statusBonusLabel', 'statusBonusTooltip', 'bonusIcon', '__isPersonalTeamWin', '__arenaUniqueID', '__arenaBonusType', '__xpFactor', '__vehicleCD')
    __itemsCache = dependency.descriptor(IItemsCache)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, meta=None, field='', *path):
        super(PremiumBonusDetailsBlock, self).__init__(meta, field, *path)
        self.__arenaUniqueID = 0
        self.__isPersonalTeamWin = False
        self.__arenaBonusType = None
        self.__xpFactor = 1
        self.__vehicleCD = None
        self.bonusIcon = ''
        self.description = ''
        self.bonusLeft = ''
        self.xpValue = ''
        self.statusBonusLabel = ''
        self.statusBonusTooltip = ''
        return

    def getVO(self):
        self.__updateStatus()
        return super(PremiumBonusDetailsBlock, self).getVO()

    def setRecord(self, result, reusable):
        self.__arenaUniqueID = reusable.arenaUniqueID
        self.__isPersonalTeamWin = reusable.isPersonalTeamWin()
        self.__arenaBonusType = reusable.common.arenaBonusType
        self.__xpFactor = self.__getAdditionalXPFactor10FromResult(result, reusable)
        _, vehicle = first(reusable.personal.getVehicleItemsIterator())
        self.__vehicleCD = vehicle.intCD

    def __getAdditionalXPFactor10FromResult(self, result, reusable):
        vehicleId = reusable.vehicles.getVehicleID(reusable.getPlayerInfo().dbID)
        vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
        additionalXPFactor10 = result.get(vehicleInfo.intCD, {}).get('additionalXPFactor10', 1)
        return int(additionalXPFactor10 / 10) if additionalXPFactor10 else 1

    def __getIsApplied(self):
        return self.__battleResults.isAddXPBonusApplied(self.__arenaUniqueID)

    def __updateStatus(self):
        self.__setBonusLeft()
        if self.__arenaUniqueID == 0:
            return
        self.__setBaseState()
        if self.__getIsApplied():
            self.__setAppliedState()
        elif not self.__isPersonalTeamWin:
            self.__setLostBattleState()
        elif not self.__battleResults.isAddXPBonusEnabled(self.__arenaUniqueID):
            self.__setExcludedState()
        elif self.__isBlockedByVehicle():
            self.__setBlockedByVehicle()
        elif self.__isBlockedByXPToTman():
            self.__setBlockedByXPToTman()
        elif self.__isBlockedByCrew():
            self.__setBlockedByCrew()
        else:
            self.__setShowButtonState()

    def __isBlockedByVehicle(self):
        item = self.__itemsCache.items.getItemByCD(self.__vehicleCD)
        return not item.isInInventory or not item.activeInNationGroup

    def __setBlockedByVehicle(self):
        self.xpValue = ''
        self.statusBonusLabel = text_styles.neutral(backport.text(R.strings.battle_results.common.premiumBonus.tankStateChanged()))
        self.statusBonusTooltip = TOOLTIPS.BATTLERESULTS_PREMIUMBONUS_TANKSTATECHANGED

    def __isBlockedByXPToTman(self):
        return not self.__battleResults.isXPToTManSameForArena(self.__arenaUniqueID)

    def __setBlockedByXPToTman(self):
        self.xpValue = ''
        if self.__battleResults.getVehicleForArena(self.__arenaUniqueID).isXPToTman:
            textKey = R.strings.battle_results.common.premiumBonus.isXPToTmenEnabled()
        else:
            textKey = R.strings.battle_results.common.premiumBonus.isXPToTmenDisabled()
        self.statusBonusLabel = text_styles.neutral(backport.text(textKey))
        self.statusBonusTooltip = makeTooltip(body=TOOLTIPS.BATTLERESULTS_PREMIUMBONUS_XPTOTMENCHANGED_BODY)

    def __isBlockedByCrew(self):
        return not self.__battleResults.isCrewSameForArena(self.__arenaUniqueID)

    def __setBlockedByCrew(self):
        self.xpValue = ''
        self.statusBonusLabel = text_styles.neutral(backport.text(R.strings.battle_results.common.premiumBonus.tankmenStateChanged()))
        self.statusBonusTooltip = TOOLTIPS.BATTLERESULTS_PREMIUMBONUS_TANKMENSTATECHANGED

    def __setBaseState(self):
        self.bonusIcon = self.__getAddXPBonusIcon(self.__xpFactor)
        self.description = text_styles.highlightText(backport.text(R.strings.battle_results.common.premiumBonus.description()))

    def __setBonusLeft(self):
        if self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS):
            applyAdditionalXPCount = self.__itemsCache.items.stats.applyAdditionalXPCount
        else:
            applyAdditionalXPCount = '-'
        self.bonusLeft = self.__getBonusLeftStr(applyAdditionalXPCount)

    def __setAppliedState(self):
        self.xpValue = ''
        self.statusBonusLabel = '{}{}'.format(makeImageTag(source=backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1())), text_styles.bonusAppliedText(backport.text(R.strings.battle_results.common.premiumBonus.appliedBonus())))

    def __setExcludedState(self):
        self.xpValue = ''
        self.statusBonusLabel = '{}{}'.format(makeImageTag(source=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), vSpace=-3), text_styles.neutral(backport.text(R.strings.battle_results.common.premiumBonus.expiredBattleResult())))

    def __setLostBattleState(self):
        self.xpValue = ''
        self.bonusIcon = self.__getAddXPBonusIcon(premacc_helpers.BattleResultsBonusConstants.LOST_BATTLE_BACKGROUND_MULTIPLIER)
        self.statusBonusLabel = '{}{}'.format(makeImageTag(source=backport.image(R.images.gui.maps.icons.library.attentionIconFilled()), vSpace=-3), text_styles.neutral(backport.text(R.strings.battle_results.common.premiumBonus.rule())))

    def __setShowButtonState(self):
        self.statusBonusLabel = ''
        self.statusBonusTooltip = ''
        bonusValue = self.__battleResults.getAdditionalXPValue(self.__arenaUniqueID)
        self.xpValue = style.makeXpLabel(bonusValue, isDiff=True, useBigIcon=True)

    def __getAddXPBonusIcon(self, multiplier):
        multiplier = premacc_helpers.validateAdditionalBonusMultiplier(multiplier)
        return backport.image(R.images.gui.maps.icons.premacc.battleResult.dyn('bonus_x{}'.format(multiplier))())

    def __getBonusLeftStr(self, applyAdditionalXPCount):
        return text_styles.main(backport.text(R.strings.battle_results.common.premiumBonus.bonusLeft(), count=text_styles.stats(applyAdditionalXPCount)))
