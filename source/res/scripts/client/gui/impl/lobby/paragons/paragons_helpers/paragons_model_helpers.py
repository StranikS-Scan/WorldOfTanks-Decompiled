# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_helpers/paragons_model_helpers.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_status_model import StatusList
from gui.impl.gen.view_models.views.lobby.paragons.common.level_model import LevelModel
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.paragons_tooltip_vehicles_model import ParagonsTooltipVehiclesModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.gui_items.vehicle_helpers import removeNationFromTechName
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import Currency
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.paragons.paragons_bonuses_packers import getParagonsBonusPacker
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.server_events.bonuses import SimpleBonus
from gui.impl.lobby.paragons.paragons_helpers.paragons_helpers import getMaxChapterLevelPoints
from helpers import dependency
from paragons_common import getVehicleParagonsEntitlements
from skeletons.gui.game_control import IParagonsController, IParagonsRewardsShopController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Iterable, Dict, Tuple, List, Optional
    from skeletons.gui.shared.utils.requesters import IStatsRequester
_CURRENCIES = (Currency.CRYSTAL,
 Currency.GOLD,
 Currency.CREDITS,
 Currency.FREE_XP)
_SKIP_BONUSES_NAMES = ('customizations', 'dossier')
_BONUS_SWAP = {'entitlements': 'vehicleSelector'}
_MAX_LEN_MAIN_BONUSES = 3
_BONUS_SORT_ORDER = ['paragonsUnlocks',
 'vehicles',
 'tmanToken',
 'styleProgress']

def fillVehicleModel(model, vehicleItem):
    model.setIsPremium(vehicleItem.isPremium or vehicleItem.isElite)
    model.setName(vehicleItem.descriptor.type.shortUserString)
    model.setTechName(replaceHyphenToUnderscore(removeNationFromTechName(vehicleItem.name)))
    model.setTier(vehicleItem.level)
    model.setRoleKey(vehicleItem.roleLabel)
    model.setType(vehicleItem.type)
    model.setNation(vehicleItem.nationName)
    model.setVehicleCD(vehicleItem.compactDescr)


def fillPriceItemModel(stats, balanceArray):
    balanceArray.clear()
    for currency in _CURRENCIES:
        currencyModel = PriceItemModel()
        currencyModel.setName(currency)
        currencyModel.setValue(stats.actualFreeXP if currency == Currency.FREE_XP else stats.actualMoney.get(currency, 0))
        balanceArray.addViewModel(currencyModel)

    balanceArray.invalidate()


def getBranchProgressPointsMultiplier(progressPointsMultipliers):
    progressPointsMultipliers = set(progressPointsMultipliers)
    return progressPointsMultipliers.pop() if len(progressPointsMultipliers) == 1 else -1


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def fillChapterModels(arrayOfChapterModels, paragonsCtrl=None, tooltipData=None):
    if tooltipData is None:
        tooltipData = {}
    else:
        tooltipData.clear()
    arrayOfChapterModels.clear()
    sortedChapterIDs = sorted(list(paragonsCtrl.config.getChapterIDs()))
    for chapterID in sortedChapterIDs:
        chapterModel = ChapterModel()
        fillChapterModel(chapterModel, chapterID, tooltipData=tooltipData)
        arrayOfChapterModels.addViewModel(chapterModel)

    arrayOfChapterModels.invalidate()
    return tooltipData


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def fillChapterModel(chapterModel, chapterID, isNeedUpdateLevels=True, paragonsCtrl=None, tooltipData=None):
    chapterLevelIDs = paragonsCtrl.config.getChapterLevelIDs(chapterID)
    isComplete = paragonsCtrl.isChapterComplete(chapterID)
    points = paragonsCtrl.getProgressPoints(chapterID) if not isComplete else getMaxChapterLevelPoints(paragonsCtrl.config, chapterID, len(chapterLevelIDs))
    with chapterModel.transaction() as tx:
        tx.setId(chapterID)
        tx.chapterStatus.setStatus(getChapterStatus(chapterID))
        tx.setIsCompleted(isComplete)
        tx.setChapterLevel(min(paragonsCtrl.paragons.storage.getProgress(chapterID) + 1, len(chapterLevelIDs)))
        tx.setPoints(points)
        tx.setIsAllRewardsClaimed(paragonsCtrl.isChapterComplete(chapterID) and paragonsCtrl.isAllSelectablesClaimed(chapterID))
        if isNeedUpdateLevels:
            _fillChapterLevelsModel(tx, chapterID, paragonsCtrl, tooltipData=tooltipData)


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def getChapterStatus(chapterID, paragonsCtrl=None):
    if chapterID is None:
        return StatusList.DEFAULT
    elif chapterID in paragonsCtrl.config.getAnnouncementChapterIDs():
        return StatusList.ANNOUNCEMENT
    elif not paragonsCtrl.wasBranchResetEverAvailable:
        return StatusList.DISABLED
    elif paragonsCtrl.isChapterPaused(chapterID):
        return StatusList.PAUSED
    chosenChapter = paragonsCtrl.chapterID
    if paragonsCtrl.isChapterComplete(chapterID):
        return StatusList.FINISHED
    else:
        return StatusList.ACTIVE if chapterID == chosenChapter else StatusList.DEFAULT


def _fillChapterLevelsModel(chapterModel, chapterID, paragonsCtrl, tooltipData=None):
    levelModels = chapterModel.getLevels()
    levelModels.clear()
    if chapterID is None:
        levelModels.invalidate()
        return
    else:
        sortedLevelIDs = sorted(paragonsCtrl.config.getChapterLevelIDs(chapterID))
        for levelID in sortedLevelIDs:
            levelModel = chapterModel.getLevelsType()()
            with levelModel.transaction() as tx:
                tx.setNumber(levelID)
                maxChapterLevelPoints = getMaxChapterLevelPoints(paragonsCtrl.config, chapterID, levelID)
                tx.setMaxPoints(maxChapterLevelPoints)
                tx.setIsCompleted(paragonsCtrl.paragons.getProgressByChapterID(chapterID) >= levelID)
                _fillLevelRewardModels(tx, chapterID, levelID, paragonsCtrl, tooltipData)
            levelModels.addViewModel(levelModel)

        levelModels.invalidate()
        return


def _fillLevelRewardModels(levelModel, chapterID, levelID, paragonsCtrl, tooltipData=None):
    levelRewards = paragonsCtrl.config.rewards.get(chapterID)['levels'].get(levelID)['bonus']
    levelRewards = _swapIfReceived(chapterID, levelID, levelRewards, paragonsCtrl)
    rewards = _splitParagonsBonuses(levelRewards, paragonsCtrl, ctx=_makeContext(chapterID, levelID, paragonsCtrl))
    paragonsBonusPacker = getParagonsBonusPacker()
    packBonusModelAndTooltipData(rewards, levelModel.getRewards(), packer=paragonsBonusPacker, tooltipData=tooltipData, startIndex=max((int(key) for key in tooltipData)) + 1 if tooltipData else 0)


def _sortBonuses(bonus):
    bonusName = bonus.getName()
    return _BONUS_SORT_ORDER.index(bonusName) if bonusName in _BONUS_SORT_ORDER else len(_BONUS_SORT_ORDER) + 1


def _splitParagonsBonuses(rewards, paragonsCtrl, ctx=None):
    if not rewards:
        return []
    rewards = _preprocessParagonsRewards(rewards, paragonsCtrl, ctx)
    bonuses = []
    for key, value in rewards.iteritems():
        bonuses.extend(getNonQuestBonuses(key, value, ctx))

    bonuses.sort(key=_sortBonuses)
    return bonuses


def _splitParagonsRewards(rewards, paragonsCtrl, ctx=None):
    if not rewards:
        return ([], [])
    rewards = _preprocessParagonsRewards(rewards, paragonsCtrl, ctx)
    mainBonuses = []
    equalBonuses = []
    mainRewardNames = ('vehicles', 'paragonsUnlocks', 'entitlements', 'vehicleSelector', 'styleProgress', 'tmanToken', 'tokens', 'tman_token')
    for key, value in rewards.iteritems():
        if key in mainRewardNames and len(mainBonuses) < _MAX_LEN_MAIN_BONUSES:
            mainBonuses.extend(getNonQuestBonuses(key, value, ctx))
        equalBonuses.extend(getNonQuestBonuses(key, value, ctx))

    mainBonuses.sort(key=_sortBonuses)
    if len(mainBonuses) == _MAX_LEN_MAIN_BONUSES:
        mainBonuses[0], mainBonuses[1] = mainBonuses[1], mainBonuses[0]
    return (mainBonuses, equalBonuses)


def _preprocessParagonsRewards(rewards, paragonsCtrl, ctx=None):
    processedRewards = {}
    for key, value in rewards.iteritems():
        if key in _SKIP_BONUSES_NAMES:
            continue
        if key in _BONUS_SWAP:
            processedRewards[_BONUS_SWAP.get(key)] = value.copy()
            continue
        if key == 'paragonsUnlocks':
            paragonsUnlockID = next(iter(value.get('ids', set())))
            if ctx and paragonsCtrl:
                ctx.update({'isLocked': not paragonsCtrl.config.isParagonsUnlockEnabled(paragonsUnlockID)})
        processedRewards[key] = value

    return processedRewards


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def fillParagonsVehicleModels(arrayOfVehicles, vehicleCDs, itemsCache=None):
    vehicleBonuses = []
    vehicles = sorted([ itemsCache.items.getItemByCD(intCD) for intCD in vehicleCDs ], key=lambda veh: veh.level)
    for vehicle in vehicles:
        vehicleBonuses.extend(getNonQuestBonuses(name='vehicles', value={vehicle.intCD: {}}, ctx=None))

    packBonusModelAndTooltipData(vehicleBonuses, arrayOfVehicles, packer=getParagonsBonusPacker())
    arrayOfVehicles.invalidate()
    return


def _makeContext(chapter=1, level=1, paragonsCtrl=None):
    return {'chapterID': chapter,
     'chapterLevel': paragonsCtrl.paragons.getProgressByChapterID(chapter),
     'bonusLevel': level}


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def makeRewardModels(bonuses, mainRewards, otherRewards, chapterID=1, levelID=1, tooltipData=None, paragonsCtrl=None):
    mainBonuses, otherBonuses = _splitParagonsRewards(bonuses, paragonsCtrl, ctx=_makeContext(chapterID, levelID, paragonsCtrl))
    bonusPacker = getParagonsBonusPacker()
    packBonusModelAndTooltipData(mainBonuses, mainRewards, packer=bonusPacker, tooltipData=tooltipData, startIndex=max((int(key) for key in tooltipData)) + 1 if tooltipData else 0)
    packBonusModelAndTooltipData(otherBonuses, otherRewards, packer=bonusPacker, tooltipData=tooltipData, startIndex=max((int(key) for key in tooltipData)) + 1 if tooltipData else 0)


def getParagonsBonuses(rewards):
    bonuses = _splitParagonsBonuses(rewards, None, ctx=None)
    return bonuses


@dependency.replace_none_kwargs(selectableRewardsCtrl=IParagonsRewardsShopController)
def _swapIfReceived(chapterID, levelID, reward, paragonsCtrl, selectableRewardsCtrl=None):
    if not reward.get('entitlements'):
        return reward
    for code, _ in reward.get('entitlements').iteritems():
        if code in getVehicleParagonsEntitlements():
            bonusCD = paragonsCtrl.getSelectedRewardBonusCD(chapterID, levelID, code)
            if bonusCD:
                return {'vehicles': {bonusCD: {'crewLvl': 100}}}
            if levelID <= paragonsCtrl.paragons.getProgressByChapterID(chapterID):
                selectableRewardsCtrl.tryMarkSelectedReward(chapterID, levelID, code)
        return reward


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def packParagonsTooltipVehicleModel(model, vehicles, paragonsCtrl=None):
    vehiclesModel = model.getVehicles()
    for vehicle in vehicles:
        vehicleModel = ParagonsTooltipVehiclesModel()
        vehicleModel.setVehicleName(vehicle.userName)
        vehicleModel.setHasProgressionPoints(vehicle.isResetParagons)
        vehicleModel.setNeedRepair(vehicle.isBroken)
        vehicleModel.setIsInBattle(vehicle.isInBattle)
        vehicleModel.setIsInPlatoonFormation(vehicle.isInUnit)
        vehicleModel.setNeedResearch(not vehicle.isUnlocked)
        vehicleModel.setVehicleUnlockPoints(paragonsCtrl.getVehicleFirstUnlockPoints(vehicle, False))
        vehicleModel.setProgressionPoints(paragonsCtrl.getVehicleProgressPoints(vehicle.intCD))
        vehiclesModel.addViewModel(vehicleModel)
