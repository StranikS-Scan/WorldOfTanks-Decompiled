# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/detail_stats.py
from enum import Enum
import typing
import common
from gui.battle_results.br_constants import ARENAS_WITH_PREMIUM_BONUSES
from gui.battle_results.presenter.common import setPremiumBonuses
from gui.impl.gen.view_models.views.lobby.postbattle.details_stats_model import DetailsStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_group_model import DetailsGroupModel
if typing.TYPE_CHECKING:
    from gui.battle_results.presenter.getter.getter import PostbattleFieldsGetter
    from gui.battle_results.reusable import _ReusableInfo
    from gui.impl.lobby.postbattle.wrappers.user_detailed_stats_model import UserDetailedStatsModel

class MainViewBlockIndexes(Enum):
    CREDITS = 0
    CRYSTALS = 1
    EXPERIENCE = 2
    PREMIUM_EARNINGS = 3


class CurrencyGroupBlockIndexes(Enum):
    CURRENCY_DETAILS = 1


def updateDetailedStatsXP(model, reusable, getter):
    model.setXP(_createXPModel(reusable, getter))
    model.invalidate()


def setDetailStatsData(model, getter, reusable, result):
    model.setCredits(_createCreditsModel(reusable, getter))
    crystalsModel = _createCrystalsModel(reusable, getter)
    if crystalsModel:
        model.setCrystals(crystalsModel)
    model.setXP(_createXPModel(reusable, getter))
    if reusable.common.arenaBonusType in ARENAS_WITH_PREMIUM_BONUSES:
        setPremiumBonuses(model, reusable)
    model.invalidate()


def _createCreditsModel(reusable, getter):
    creditsRecords = common.getCreditsRecords(reusable)
    replayRecords = ((creditsRecords.additional,), (creditsRecords.main,))
    creditFields = (getter.credits.getCreditExpenses(), getter.credits.getCreditEarnings(reusable))
    modelTypes = (DetailsStatsModel.EXPENSES_SUBGROUP_TYPE, DetailsStatsModel.EARNINGS_SUBGROUP_TYPE)
    models = _addCurrencySubgroups(creditFields, replayRecords, modelTypes, CurrencyGroupBlockIndexes.CURRENCY_DETAILS)
    records = [common.createRecord(getter.credits.getEarnedCredits(), (creditsRecords.main,))]
    records += models
    records.append(common.createRecord(getter.credits.getTotalCredits(), (creditsRecords.main, creditsRecords.additional)))
    records.append(common.createRecord(getter.credits.getPiggyBankCredits(), (creditsRecords.additional,)))
    recordItems = common.getRecordItems(filter(None, records))
    creditsModel = common.createGroupModel(MainViewBlockIndexes.CREDITS, DetailsStatsModel.CREDITS_GROUP_TYPE)
    creditsModel.setRecords(recordItems)
    return creditsModel


def _createCrystalsModel(reusable, getter):
    crystalsRecords = common.getCrystalsRecords(reusable)
    if crystalsRecords is None:
        return
    else:
        replayRecords = ((crystalsRecords.additional,), (crystalsRecords.main,))
        modelTypes = (DetailsStatsModel.EXPENSES_SUBGROUP_TYPE, DetailsStatsModel.EARNINGS_SUBGROUP_TYPE)
        crystalFields = (getter.crystals.getCrystalsExpenses(), getter.crystals.getCrystalsEarnings())
        records = [common.createRecord(getter.crystals.getEarnedCrystals(), (crystalsRecords.main,))]
        records += _addCurrencySubgroups(crystalFields, replayRecords, modelTypes, CurrencyGroupBlockIndexes.CURRENCY_DETAILS)
        records.append(common.createRecord(getter.crystals.getTotalCrystals(), (crystalsRecords.main, crystalsRecords.additional)))
        recordItems = common.getRecordItems(filter(None, records))
        if recordItems is None:
            return
        crystalsModel = common.createGroupModel(MainViewBlockIndexes.CRYSTALS, DetailsStatsModel.CRYSTALS_GROUP_TYPE)
        crystalsModel.setRecords(recordItems)
        return crystalsModel


def _addCurrencySubgroups(currencyFields, replayRecords, modelTypes, blockIdx):
    models = []
    for fields, replays, modelType in zip(currencyFields, replayRecords, modelTypes):
        subgroupRecords = filter(None, [ common.createRecord(field, replays) for field in fields ])
        if not subgroupRecords:
            continue
        recordItems = common.getRecordItems(subgroupRecords)
        model = common.createGroupModel(blockIdx, modelType)
        model.setRecords(recordItems)
        models.append(model)

    return models


def _createXPModel(reusable, getter):
    xpRecords, freeXpRecords = common.getXpRecords(reusable).main
    xpFields = getter.xp.getXP(reusable, xpRecords.getRecord('isHighScope'))
    records = filter(None, [ common.createRecord(field, (xpRecords, freeXpRecords)) for field in xpFields ])
    recordItems = common.getRecordItems(records)
    xpGroup = common.createGroupModel(MainViewBlockIndexes.EXPERIENCE, DetailsStatsModel.XP_GROUP_TYPE)
    xpGroup.setRecords(recordItems)
    return xpGroup
