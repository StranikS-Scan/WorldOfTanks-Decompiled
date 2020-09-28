# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/personal.py
import typing
import ArenaType
from constants import LOOTBOX_TOKEN_PREFIX
from gui.battle_control.battle_constants import WinStatus
from gui.battle_results.br_constants import ARENAS_WITH_PREMIUM_BONUSES
from gui.battle_results.presenter.achievements import setPersonalAchievements
from gui.battle_results.presenter.common import getTotalXPToShow, getTotalCreditsToShow, getXpRecords, getCreditsRecords, getCrystalsRecords
from gui.battle_results.presenter.detailed_efficiency import setDetailedEfficiency
from gui.battle_results.br_helper import getShortVehicleInfo, isPremiumExpBonusAvailable, getBattleType
from gui.battle_results.br_constants import PlayerTeamResult
from gui.impl.gen.view_models.views.lobby.postbattle.widget_model import WidgetModel
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.wt_event.wt_event_helpers import getTicketName, getLootBoxTypeByID, isSpecialBossVehicle, isBossCollectionElement, BOSS_ELEMENT_NAME, HUNTER_ELEMENT_NAME
from helpers import dependency, time_utils
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import first, findFirst
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.common_stats_model import CommonStatsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.rewards_model import RewardsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.general_info_model import GeneralInfoModel
    from gui.impl.wrappers.user_list_model import UserListModel
    from gui.server_events.bonuses import SimpleBonus, BattleTokensBonus
_TEAM_RESULT_TO_WIN_STATUS = {PlayerTeamResult.WIN: WinStatus.WIN,
 PlayerTeamResult.DRAW: WinStatus.DRAW,
 PlayerTeamResult.DEFEAT: WinStatus.LOSE}
_WT_WIDGETS_PRIORITY = {HUNTER_ELEMENT_NAME: 3,
 BOSS_ELEMENT_NAME: 3,
 'ticket': 2,
 'wt_hunter': 1,
 'wt_boss': 1}

def setPersonalData(model, cachedSettings, reusable, result):
    _setGeneralInfoData(model.generalInfo, reusable, result)
    _setEconomicData(model.rewards, reusable)
    setPersonalAchievements(model.rewards, reusable, result)
    setDetailedEfficiency(model.detailedEfficiency, reusable, result)


def updatePremiumData(model, reusable, cachedSettings):
    hasPremium = reusable.economics.hasAnyPremium
    xpRecord = getXpRecords(reusable).main.xp
    model.setExperience(getTotalXPToShow(reusable, xpRecord, hasPremium))
    _setPremiumData(model, reusable, cachedSettings)


def updatePremiumState(model, reusable, cachedSettings):
    isActivePremiumPlus = reusable.economics.isActivePremiumPlus()
    model.setIsPremiumBought(isActivePremiumPlus)
    if isActivePremiumPlus:
        _setPremiumData(model, reusable, cachedSettings)


def updateCurrentTime(model, reusable):
    model.generalInfo.setServerTime(time_utils.getServerUTCTime())
    if reusable.economics.isActivePremiumPlus() and reusable.economics.getAppliedAdditionalCount() == 0:
        model.rewards.expBonus.setNextBonusTime(_getNextBonusTime())


def setWidgetsData(model, reusable, result):
    rewards = []
    questsProgress = reusable.progress.getPlayerQuestProgress()
    for quest, _, _, _, isCompleted in questsProgress:
        if not isCompleted:
            continue
        for bonus in quest.getBonuses():
            rewards.append(bonus)

    rewards = mergeBonuses(rewards)
    rewards = splitBonuses(rewards)
    widgetsData = []
    for reward in rewards:
        widgetsData.extend(_makeWidgetData(reward))

    for widget in sorted(widgetsData, cmp=_widgetComparator, reverse=True):
        model.addViewModel(widget)


def _widgetComparator(left, right):
    leftPriority = _WT_WIDGETS_PRIORITY.get(left.getType(), 0)
    rightPriority = _WT_WIDGETS_PRIORITY.get(right.getType(), 0)
    return leftPriority - rightPriority


def _makeWidgetData(bonus):
    result = []
    bonusName = bonus.getName()
    if bonusName not in ('battleToken', 'wtTicket', 'groups'):
        return result
    else:
        if bonusName in ('battleToken', 'wtTicket'):
            tokens = bonus.getTokens()
            ticketName = getTicketName()
            hasLootBoxes = _hasLootBoxes()
            for token in tokens.itervalues():
                widgetType = 'unknown'
                isDisabled = False
                if token.id.startswith(ticketName):
                    widgetType = 'ticket'
                elif token.id.startswith(LOOTBOX_TOKEN_PREFIX):
                    widgetType = getLootBoxTypeByID(token.id)
                    isDisabled = not hasLootBoxes
                if widgetType in ('unknown', 'wt_special'):
                    continue
                model = WidgetModel()
                model.setQuantity(token.count)
                model.setType(widgetType)
                model.setIsDisabled(isDisabled)
                result.append(model)

        elif bonusName == 'groups':
            isBoss = isBossCollectionElement(bonus)
            if isBoss is None:
                return result
            model = WidgetModel()
            model.setType(BOSS_ELEMENT_NAME if isBoss else HUNTER_ELEMENT_NAME)
            result.append(model)
        return result


def _setEconomicData(model, reusable):
    hasPremium = reusable.economics.hasAnyPremium
    xpRecord = getXpRecords(reusable).main.xp
    creditsRecords = getCreditsRecords(reusable).main
    crystalsRecords = getCrystalsRecords(reusable)
    model.setExperience(getTotalXPToShow(reusable, xpRecord, hasPremium))
    model.setCredits(getTotalCreditsToShow(reusable, creditsRecords, hasPremium))
    model.setCrystals(crystalsRecords.main.getRecord('crystal') if crystalsRecords is not None else 0)
    return


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
    model.setIsSpecial(isSpecialBossVehicle(vehicle))
    model.setBattleFinishReason(reusable.common.finishReason)
    common = result['common']
    finishTime = common.get('arenaCreateTime', 0) + common.get('duration', 0)
    model.setBattleFinishTime(finishTime)
    model.setServerTime(time_utils.getServerUTCTime())


def _getNextBonusTime():
    return time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()


def _getBonusRestriction(reusable):
    _, vehicle = first(reusable.personal.getVehicleItemsIterator())
    vehicleCD = vehicle.intCD
    return isPremiumExpBonusAvailable(reusable.arenaUniqueID, reusable.isPersonalTeamWin(), vehicleCD)


def _hasLootBoxes():
    itemsCache = dependency.instance(IItemsCache)
    box = findFirst(lambda box: box.getInventoryCount() > 0, itemsCache.items.tokens.getLootBoxes().itervalues(), None)
    return box is not None
