# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_helpers/paragons_model_helpers.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel, StatusList
from gui.impl.gen.view_models.views.lobby.paragons.common.level_model import LevelModel
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
from paragons_common import getAllParagonsEntitlements, PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX, SELECTED_REWARD_TOKEN_PREFIX_TO_BONUS_TYPE
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Iterable, Dict, Tuple, List, Optional
    from skeletons.gui.shared.utils.requesters import IStatsRequester
_CURRENCIES = (Currency.CRYSTAL,
 Currency.GOLD,
 Currency.CREDITS,
 Currency.FREE_XP)
_MAIN_REWARD_NAMES = ('vehicles', 'paragonsUnlocks', 'entitlements', 'vehicleSelector')
_SKIP_BONUSES_NAMES = ('customizations', 'dossier')
_BONUS_SWAP = {'entitlements': 'vehicleSelector'}

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
    with chapterModel.transaction() as tx:
        tx.setId(chapterID)
        tx.setStatus(getChapterStatus(chapterID))
        tx.setIsCompleted(paragonsCtrl.isChapterComplete(chapterID))
        tx.setChapterLevel(min(paragonsCtrl.paragons.storage.getProgress(chapterID) + 1, len(chapterLevelIDs)))
        tx.setPoints(paragonsCtrl.progress if chapterID == paragonsCtrl.chapterID else 0)
        tx.setIsAllRewardsClaimed(paragonsCtrl.isChapterComplete(chapterID) and paragonsCtrl.isAllSelectablesClaimed())
        if isNeedUpdateLevels:
            _fillChapterLevelsModel(tx, chapterID, paragonsCtrl, tooltipData=tooltipData)


@dependency.replace_none_kwargs(paragonsCtrl=IParagonsController)
def getChapterStatus(chapterID, paragonsCtrl=None):
    if chapterID is None:
        return StatusList.DEFAULT
    elif chapterID in paragonsCtrl.config.getAnnouncementChapterIDs():
        return StatusList.ANNOUNCEMENT
    elif paragonsCtrl.isPaused:
        return StatusList.DISABLED
    chosenChapter = paragonsCtrl.chapterID
    if paragonsCtrl.isChapterComplete(chapterID):
        return StatusList.FINISHED
    elif chapterID == chosenChapter:
        return StatusList.ACTIVE
    else:
        return StatusList.DISABLED if chapterID != chosenChapter and chosenChapter is not None else StatusList.DEFAULT


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
    mainBonuses, equalBonuses = _splitParagonsBonuses(levelRewards, paragonsCtrl, ctx=_makeContext(chapterID, levelID, paragonsCtrl))
    paragonsBonusPacker = getParagonsBonusPacker()
    packBonusModelAndTooltipData(mainBonuses, levelModel.getMainRewards(), packer=paragonsBonusPacker, tooltipData=tooltipData, startIndex=max((int(key) for key in tooltipData)) + 1 if tooltipData else 0)
    packBonusModelAndTooltipData(equalBonuses, levelModel.getEqualRewards(), packer=paragonsBonusPacker, tooltipData=tooltipData, startIndex=max((int(key) for key in tooltipData)) + 1 if tooltipData else 0)


def _sortBonuses(bonuses, position, maxLength, instance):
    if len(bonuses) <= position:
        return
    for index, item in enumerate(bonuses):
        if len(bonuses) <= maxLength and item.getName() == instance:
            bonuses[position], bonuses[index] = bonuses[index], bonuses[position]


def _splitParagonsBonuses(rewards, paragonsCtrl, ctx=None):
    if not rewards:
        return ([], [])
    rewards = _preprocessParagonsRewards(rewards, paragonsCtrl, ctx)
    mainBonuses = []
    equalBonuses = []
    for key, value in rewards.iteritems():
        if key in _MAIN_REWARD_NAMES:
            mainBonuses.extend(getNonQuestBonuses(key, value, ctx))
        equalBonuses.extend(getNonQuestBonuses(key, value, ctx))

    _sortBonuses(equalBonuses, 0, 3, 'tmanToken')
    return (mainBonuses, equalBonuses)


def _splitParagonsRewards(rewards, paragonsCtrl, ctx=None):
    if not rewards:
        return ([], [])
    rewards = _preprocessParagonsRewards(rewards, paragonsCtrl, ctx)
    mainBonuses = []
    equalBonuses = []
    mainRewardNames = ('vehicles', 'paragonsUnlocks', 'entitlements', 'vehicleSelector', 'styleProgress', 'tmanToken', 'tokens', 'tman_token')
    for key, value in rewards.iteritems():
        if key in mainRewardNames and len(mainBonuses) < 3:
            mainBonuses.extend(getNonQuestBonuses(key, value, ctx))
        equalBonuses.extend(getNonQuestBonuses(key, value, ctx))

    _sortBonuses(mainBonuses, 0, 3, 'tmanToken')
    _sortBonuses(mainBonuses, 1, 3, 'vehicles')
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
    bonuses, otherBonuses = _splitParagonsBonuses(rewards, None, ctx=None)
    return bonuses + otherBonuses


def _swapIfReceived(chapterID, levelID, reward, paragonsCtrl):
    if not reward.get('entitlements'):
        return reward
    for code, _ in reward.get('entitlements').iteritems():
        if code in getAllParagonsEntitlements():
            received = paragonsCtrl.getSelectedRewardTokenID(chapterID, levelID, code)
            if received:
                bonusType, bonusCD = ('', 0)
                if received.startswith(PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX):
                    bonusCD = received.split(':')[-1]
                    bonusType = SELECTED_REWARD_TOKEN_PREFIX_TO_BONUS_TYPE[PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX]
                return {bonusType: {int(bonusCD): {'crewLvl': 100}}}
        return reward
