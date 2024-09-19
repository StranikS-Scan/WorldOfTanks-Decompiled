# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/personal.py
import typing
import ArenaType
from gui.battle_control.battle_constants import WinStatus
from gui.battle_results.br_constants import ARENAS_WITH_PREMIUM_BONUSES
from gui.battle_results.presenter.achievements import setPersonalAchievements
from gui.battle_results.presenter.common import getTotalXPToShow, getTotalCreditsToShow, getXpRecords, getCreditsRecords, setPremiumBonuses
from gui.battle_results.presenter.detailed_efficiency import setDetailedEfficiency
from gui.battle_results.br_helper import getShortVehicleInfo, isPremiumExpBonusAvailable, getBattleType
from gui.battle_results.br_constants import PlayerTeamResult
from gui.impl.auxiliary.rewards_helper import getCurrentStepState
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.common_stats_model import CommonStatsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.rewards_model import RewardsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.progressive_reward_model import ProgressiveRewardModel
    from gui.impl.gen.view_models.views.lobby.postbattle.general_info_model import GeneralInfoModel
_TEAM_RESULT_TO_WIN_STATUS = {PlayerTeamResult.WIN: WinStatus.WIN,
 PlayerTeamResult.DRAW: WinStatus.DRAW,
 PlayerTeamResult.DEFEAT: WinStatus.LOSE}

def setPersonalData(model, cachedSettings, reusable, result):
    _setGeneralInfoData(model.generalInfo, reusable, result)
    _setEconomicData(model.rewards, reusable)
    _setProgressiveReward(model.rewards.progressiveReward, reusable)
    _setPremiumData(model.rewards, reusable, cachedSettings)
    setPremiumBonuses(model.rewards, reusable)
    setPersonalAchievements(model.rewards, reusable, result)
    setDetailedEfficiency(model.detailedEfficiency, reusable, result)
    model.rewards.setIsPremiumBought(reusable.personal.isPremiumPlus)


def updatePremiumData(model, reusable, cachedSettings):
    hasPremium = reusable.hasAnyPremiumInPostBattle
    xpRecord = getXpRecords(reusable).main.xp
    model.setExperience(getTotalXPToShow(reusable, xpRecord, hasPremium))
    _setPremiumData(model, reusable, cachedSettings)


def updatePremiumState(model, reusable, cachedSettings):
    isActivePremiumPlus = reusable.personal.isPremiumPlus
    model.setIsPremiumBought(isActivePremiumPlus)
    if isActivePremiumPlus:
        _setPremiumData(model, reusable, cachedSettings)


def updateCurrentTime(model, reusable):
    model.generalInfo.setServerTime(time_utils.getServerUTCTime())
    if reusable.personal.isPremiumPlus and reusable.personal.getAppliedAdditionalCount() == 0:
        model.rewards.expBonus.setNextBonusTime(_getNextBonusTime())


def _setEconomicData(model, reusable):
    hasPremium = reusable.hasAnyPremiumInPostBattle
    xpRecord = getXpRecords(reusable).main.xp
    creditsRecords = getCreditsRecords(reusable).main
    model.setExperience(getTotalXPToShow(reusable, xpRecord, hasPremium))
    model.setCredits(getTotalCreditsToShow(reusable, creditsRecords, hasPremium))


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _setPremiumData(model, reusable, cachedSettings, itemsCache=None, lobbyContext=None):
    config = lobbyContext.getServerSettings().getAdditionalBonusConfig()
    isEnabled = config['enabled']
    if not isEnabled or reusable.common.arenaBonusType not in ARENAS_WITH_PREMIUM_BONUSES:
        return
    else:
        additionalBonusMaxCount = config['applyCount']
        if cachedSettings is None or cachedSettings.get('additionalBonusMultiplier') is None:
            additionalBonusMultiplier = config['bonusFactor']
        else:
            additionalBonusMultiplier = cachedSettings.get('additionalBonusMultiplier')
        restriction = _getBonusRestriction(reusable)
        leftCount = itemsCache.items.stats.applyAdditionalXPCount
        bonusLeft = leftCount > 0
        model.expBonus.setBonusMultiplier(additionalBonusMultiplier)
        model.expBonus.setRestriction(restriction)
        model.expBonus.setUsedBonusCount(additionalBonusMaxCount - leftCount)
        model.expBonus.setMaxBonusCount(additionalBonusMaxCount)
        model.expBonus.setIsEnabled(isEnabled)
        if not bonusLeft:
            model.expBonus.setNextBonusTime(_getNextBonusTime())
        return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _setGeneralInfoData(model, reusable, result, itemsCache=None):
    winStatus = _TEAM_RESULT_TO_WIN_STATUS[reusable.getPersonalTeamResult()]
    model.setWinStatus(winStatus)
    battleType = getBattleType(reusable)
    model.setBattleType(battleType)
    arenaType = ArenaType.g_cache[reusable.common.arenaTypeID]
    model.setArenaName(arenaType.geometryName)
    vehicleInfo = getShortVehicleInfo(reusable)
    vehicle = itemsCache.items.getItemByCD(vehicleInfo.intCD)
    noNationName = getNationLessName(vehicle.name)
    model.setVehicleIconName(replaceHyphenToUnderscore(noNationName))
    model.setVehicleLevel(vehicle.level)
    model.setVehicleType(vehicle.type)
    model.setLocalizedVehicleName(vehicle.shortUserName)
    model.setBattleFinishReason(reusable.common.finishReason)
    common = result['common']
    finishTime = common.get('arenaCreateTime', 0) + common.get('duration', 0)
    model.setBattleFinishTime(finishTime)
    model.setServerTime(time_utils.getServerUTCTime())


def _setProgressiveReward(submodel, reusable):
    data = reusable.progress.processProgressiveRewardData()
    if data is not None:
        submodel.setIsEnabled(True)
        submodel.setMaxSteps(data.maxSteps)
        submodel.setCurrentStep(data.currentStep)
        submodel.setCurrentStepState(getCurrentStepState(data.probability, data.hasCompleted))
    else:
        submodel.setIsEnabled(False)
    return


def _getNextBonusTime():
    return time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()


def _getBonusRestriction(reusable):
    _, vehicle = first(reusable.personal.getVehicleItemsIterator())
    vehicleCD = vehicle.intCD
    return isPremiumExpBonusAvailable(reusable.arenaUniqueID, reusable.isPersonalTeamWin(), vehicleCD)
