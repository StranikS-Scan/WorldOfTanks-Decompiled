# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/tooltips/currency_tooltips.py
import typing
from gui.battle_results.presenter.common import getXpRecords, getCrystalsRecords, getCreditsRecords, getRecordItems, createRecord
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen import R
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.presenter.getter.getter import PostbattleFieldsGetter
    from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.financial_tooltip_model import FinancialTooltipModel
_TOOLTIP_STRINGS = R.strings.postbattle_screen.tooltip.financeDetails

def setFinancialData(model, getter, reusable, currencyType):
    valueExtractor = _PARAMETER_VALUE_EXTRACTOR.get(currencyType)
    if valueExtractor is None:
        raise SoftException('Incorrect currency Type={}'.format(currencyType))
    fields, strIDs, records = valueExtractor(getter, reusable)
    fields = [ _getActualField(field, label) for field, label in zip(fields, strIDs) ]
    records = [ createRecord(fields, record) for fields, record in zip(fields, records) ]
    model.setRecords(getRecordItems(filter(None, records)))
    model.setCurrencyType(currencyType)
    model.setAccountType(reusable.personal.getPremiumType())
    return


def _getCreditsData(getter, reusable):
    creditRecords = getCreditsRecords(reusable)
    fields = (getter.credits.getEarnedCredits(),
     getter.credits.getTotalCreditExpenses(),
     getter.credits.getTotalBonusesCredits(),
     getter.credits.getTotalCredits(),
     getter.credits.getPiggyBankCredits(),
     getter.credits.getAlternativeTotalCredits())
    strIDs = (_TOOLTIP_STRINGS.earned(),
     _TOOLTIP_STRINGS.expenses(),
     _TOOLTIP_STRINGS.bonuses(),
     _TOOLTIP_STRINGS.total.credits(),
     _TOOLTIP_STRINGS.piggyBank(),
     _TOOLTIP_STRINGS.alternativeTotal.credits())
    creditRecords = ((creditRecords.main,),
     (creditRecords.additional,),
     (creditRecords.main,),
     (creditRecords.main, creditRecords.additional),
     (creditRecords.additional,),
     (creditRecords.alternative, creditRecords.additional))
    return (fields, strIDs, creditRecords)


def _getCrystalsData(getter, reusable):
    crystalsRecords = getCrystalsRecords(reusable)
    if crystalsRecords is None:
        return
    else:
        fields = (getter.crystals.getEarnedCrystals(),
         getter.crystals.getTotalCrystalsExpenses(),
         getter.crystals.getTotalCrystalsEarnings(),
         getter.crystals.getTotalCrystals())
        strIDs = (_TOOLTIP_STRINGS.earned(),
         _TOOLTIP_STRINGS.expenses(),
         _TOOLTIP_STRINGS.bonuses(),
         _TOOLTIP_STRINGS.total.crystals())
        crystalRecords = ((crystalsRecords.main,),
         (crystalsRecords.additional,),
         (crystalsRecords.main,),
         (crystalsRecords.main, crystalsRecords.additional))
        return (fields, strIDs, crystalRecords)


def _getXPData(getter, reusable):
    xpRecords = getXpRecords(reusable)
    fields = (getter.xp.getEarnedXP(xpRecords.main.xp.getRecord('isHighScope')),
     getter.xp.getBonusesTotalXP(),
     getter.xp.getTotalXP(),
     getter.xp.getAlternativeTotalXP())
    strIDs = (_TOOLTIP_STRINGS.earned(),
     _TOOLTIP_STRINGS.bonuses(),
     _TOOLTIP_STRINGS.total.xp(),
     _TOOLTIP_STRINGS.alternativeTotal.xp())
    xpRecords = (xpRecords.main,
     xpRecords.main,
     xpRecords.main,
     xpRecords.alternative)
    return (fields, strIDs, xpRecords)


def _getActualField(field, strID):
    return field if field.stringID == strID else field.copy(stringID=strID)


_PARAMETER_VALUE_EXTRACTOR = {CurrencyModel.CREDITS: _getCreditsData,
 CurrencyModel.CRYSTALS: _getCrystalsData,
 CurrencyModel.XP: _getXPData}
