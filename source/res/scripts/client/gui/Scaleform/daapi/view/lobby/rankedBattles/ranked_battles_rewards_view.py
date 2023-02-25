# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_rewards_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_STYLED_VEHICLES_POOL, RANKED_AWARDS_COUNTER, RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED, RANKED_AWARDS_BUBBLE_YEAR_REACHED
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsLeaguesMeta import RankedBattlesRewardsLeaguesMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsMeta import RankedBattlesRewardsMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsRanksMeta import RankedBattlesRewardsRanksMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsYearMeta import RankedBattlesRewardsYearMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS as _RBC
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import FINAL_QUEST_PATTERN, STANDARD_POINTS_COUNT, YEAR_AWARDS_ORDER
from gui.ranked_battles.ranked_builders import rewards_vos
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter
from gui.ranked_battles.ranked_helpers import getDataFromFinalTokenQuestID
from gui.ranked_battles.ranked_helpers.sound_manager import AmbientType
from gui.shared.event_dispatcher import showStylePreview, showRankedSelectableReward
from gui.shared.formatters import text_styles
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import AcyclicNotifier
from helpers import dependency, time_utils
from items import parseIntCompactDescr
from items.vehicles import VehicleDescriptor, getVehicleType
from shared_utils import findFirst, first
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.ranked_battles.ranked_builders import main_page_vos
_logger = logging.getLogger(__name__)
_REWARDS_COMPONENTS = (RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI, RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI, RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI)

class RankedBattlesRewardsView(RankedBattlesRewardsMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedBattlesRewardsView, self).__init__()
        self._selectedViewID = None
        return

    def reset(self):
        pass

    def onTabChanged(self, viewId):
        self._selectedViewID = viewId
        self._updateSounds()
        component = self.getComponent(viewId)
        if component is not None:
            component.reset()
        return

    def setActiveTab(self, linkage=None):
        raise NotImplementedError

    def _populate(self):
        super(RankedBattlesRewardsView, self)._populate()
        self.__rankedController.onUpdated += self._update
        self.setActiveTab()
        self.as_setCountersS([{'componentId': _RBC.RANKED_BATTLES_REWARDS_YEAR_ID,
          'count': main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_AWARDS_COUNTER))}])

    def _dispose(self):
        self.__rankedController.onUpdated -= self._update
        super(RankedBattlesRewardsView, self)._dispose()

    def _update(self):
        self.setActiveTab(self._selectedViewID)

    def _updateSounds(self):
        raise NotImplementedError()

    def _updateYearRewardCounters(self):
        isNeedUpdate = False
        if AccountSettings.getCounters(RANKED_AWARDS_COUNTER) > 0:
            AccountSettings.setCounters(RANKED_AWARDS_COUNTER, 0)
            isNeedUpdate = True
        if not AccountSettings.getSettings(RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED):
            AccountSettings.setSettings(RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED, True)
            isNeedUpdate = True
        if not AccountSettings.getSettings(RANKED_AWARDS_BUBBLE_YEAR_REACHED):
            AccountSettings.setSettings(RANKED_AWARDS_BUBBLE_YEAR_REACHED, True)
            isNeedUpdate = True
        if isNeedUpdate:
            self._updateCounters()

    def _updateCounters(self):
        self.as_setCountersS([{'componentId': _RBC.RANKED_BATTLES_REWARDS_YEAR_ID,
          'count': main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_AWARDS_COUNTER))}])


class RankedRewardsSeasonOffView(RankedBattlesRewardsView):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def reset(self):
        self._updateSounds()

    def setActiveTab(self, linkage=None):
        self._updateYearRewardCounters()
        tabs = rewards_vos.getSeasonOffTabs(self.__rankedController.isYearRewardEnabled(), self.__rankedController.isLeagueRewardEnabled())
        self.as_setTabsDataS(tabs)

    def _update(self):
        pass

    def _updateSounds(self):
        soundManager = self.__rankedController.getSoundManager()
        soundManager.setAmbient(AmbientType.HANGAR)
        soundManager.setProgressSound()


class RankedRewardsSeasonOnView(RankedBattlesRewardsView):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def reset(self):
        self.setActiveTab()
        for linkage in _REWARDS_COMPONENTS:
            component = self.getComponent(linkage)
            if component is not None:
                component.reset()

        return

    def setActiveTab(self, linkage=None):
        isYearRewardEnabled = self.__rankedController.isYearRewardEnabled()
        if linkage == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI and not isYearRewardEnabled:
            linkage = None
        if linkage not in _REWARDS_COMPONENTS:
            if self.__rankedController.isAccountMastered() and self.__rankedController.isLeagueRewardEnabled():
                linkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI
            else:
                linkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI
        tabs = rewards_vos.getSeasonOnTabs(linkage, isYearRewardEnabled, self.__rankedController.isLeagueRewardEnabled())
        self.as_setTabsDataS(tabs)
        return

    def _updateSounds(self):
        isMastered = self.__rankedController.isAccountMastered()
        soundManager = self.__rankedController.getSoundManager()
        if self._selectedViewID == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI:
            soundManager.setAmbient(AmbientType.HANGAR)
            soundManager.setProgressSound()
        elif isMastered:
            soundManager.setAmbient()
            soundManager.setProgressSound()
        else:
            soundManager.setAmbient()
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID())

    def onTabChanged(self, viewId):
        if viewId == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI:
            self._updateYearRewardCounters()
        super(RankedRewardsSeasonOnView, self).onTabChanged(viewId)


class RankedBattlesRewardsRanksView(RankedBattlesRewardsRanksMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedBattlesRewardsRanksView, self).__init__()
        self.__selectedDivisionIdx = self.__rankedController.getCurrentDivision().getID()
        self.__bonusFormatter = getRankedAwardsFormatter()

    def onRequestData(self, divisionIdx, iconSizeID, rewardsCount):
        if self.__selectedDivisionIdx != int(divisionIdx):
            self.__selectedDivisionIdx = int(divisionIdx)
            self.__updateSounds()
        selectedDivision = self.__getSelectedDivision()
        self.as_setRewardsS(self.__getRewardsData(selectedDivision, iconSizeID, int(rewardsCount)), selectedDivision.isQualification())

    def reset(self):
        currentDivisionIdx = self.__rankedController.getCurrentDivision().getID()
        if self.__selectedDivisionIdx != currentDivisionIdx:
            self.__selectedDivisionIdx = currentDivisionIdx
            self.__onUpdate(True)
        self.__updateSounds()

    def _populate(self):
        super(RankedBattlesRewardsRanksView, self)._populate()
        self.__rankedController.onUpdated += self.__onUpdate
        self.as_setDivisionsDataS(self.__getDivisionsData(), False)

    def _dispose(self):
        self.__bonusFormatter = None
        self.__rankedController.onUpdated -= self.__onUpdate
        super(RankedBattlesRewardsRanksView, self)._dispose()
        return

    def __getRankRewards(self, rank, iconSize):
        quest = rank.getQuest()
        return self.__bonusFormatter.getFormattedBonuses(quest.getBonuses(), iconSize) if quest else []

    def __getDivisionsData(self):
        data = []
        for division in self.__rankedController.getDivisions():
            data.append(rewards_vos.getDivisionVO(division))

        return data

    def __getSelectedDivision(self):
        return self.__rankedController.getDivisions()[self.__selectedDivisionIdx]

    def __getRewardsData(self, division, iconSize, rewardsCount):
        rewards = []
        self.__bonusFormatter.setMaxRewardsCount(rewardsCount)
        currentRankID, _ = self.__rankedController.getMaxRank()
        if division.isQualification():
            iconSize = _RBC.RANKED_REWARDS_REWARD_SIZE_BIG
        for rankID in division.getRanksIDs():
            rank = self.__rankedController.getRank(rankID)
            rewards.append(rewards_vos.getRankRewardsVO(rank, self.__getRankRewards(rank, iconSize), currentRankID))

        return rewards

    def __onUpdate(self, immediately=False):
        self.as_setDivisionsDataS(self.__getDivisionsData(), immediately)

    def __updateSounds(self):
        soundManager = self.__rankedController.getSoundManager()
        selectedDivision = self.__getSelectedDivision()
        if selectedDivision.isUnlocked():
            soundManager.setProgressSound(selectedDivision.getUserID())
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID(), isLoud=False)


_DEFAULT_STYLED_VEHICLES = ('uk:GB91_Super_Conqueror', 'china:Ch41_WZ_111_5A', 'ussr:R148_Object_430_U', 'japan:J20_Type_2605')

class RankedBattlesRewardsLeaguesView(RankedBattlesRewardsLeaguesMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RankedBattlesRewardsLeaguesView, self).__init__()
        self.__styleDescriptions = {}

    def onStyleClick(self, styleID):
        self.__showStylePreview(int(styleID))

    def reset(self):
        pass

    @classmethod
    def _backToLeaguesCallback(cls):
        cls.__rankedController.showRankedBattlePage(ctx={'selectedItemID': _RBC.RANKED_BATTLES_REWARDS_ID,
         'rewardsSelectedTab': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI})

    def _populate(self):
        super(RankedBattlesRewardsLeaguesView, self)._populate()
        data = self.__getLeaguesData()
        descr = backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.description())
        self.as_setRewardsS({'leagues': data,
         'description': descr})

    def __getLeaguesData(self):
        leaguesRewardsData = self.__rankedController.getLeagueRewards()
        result = []
        formatter = getRankedAwardsFormatter()

        def findAndPreformatBonus(awardsList, bonusName):
            bonus = findFirst(lambda x: x.getName() == bonusName, awardsList)
            if bonus is not None:
                bonus = first(formatter.getPreformattedBonuses([bonus]))
            return bonus

        for data in leaguesRewardsData:
            leagueID = data['league']
            awards = data['awards']
            badgeBonus = findAndPreformatBonus(awards, 'dossier')
            styleBonus = findAndPreformatBonus(awards, 'customizations')
            if leagueID and styleBonus and badgeBonus:
                isCurrent = self.__rankedController.getWebSeasonProvider().seasonInfo.league == leagueID
                styleCD = styleBonus.specialArgs[0]
                style = self.__itemsCache.items.getItemByCD(styleCD)
                _, _, styleID = parseIntCompactDescr(styleCD)
                self.__styleDescriptions[styleID] = backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.description.dyn('league%s' % leagueID)())
                badgeID = badgeBonus.specialArgs[0]
                result.append(rewards_vos.getLeagueRewardVO(leagueID, styleBonus, styleID, style.userName, badgeID, isCurrent))
            _logger.error('Invalid awards or leagueID in quests')

        return result

    def __showStylePreview(self, styleID):
        styledVehicleCD = None
        minLvl, _ = self.__rankedController.getSuitableVehicleLevels()
        if g_currentVehicle.isPresent() and g_currentVehicle.item.level >= minLvl:
            styledVehicleCD = g_currentVehicle.item.intCD
        else:
            accDossier = self.__itemsCache.items.getAccountDossier()
            vehicles = accDossier.getRankedStats().getVehicles()
            if not vehicles:
                vehicles = accDossier.getRandomStats().getVehicles()
            if vehicles:
                sortedVehicles = sorted(vehicles.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
                for vehicleCD, _ in sortedVehicles:
                    vehicleType = getVehicleType(vehicleCD)
                    if vehicleType.level >= minLvl:
                        styledVehicleCD = vehicleCD
                        break

            if not styledVehicleCD:
                vehiclesPool = AccountSettings.getSettings(RANKED_STYLED_VEHICLES_POOL)
                if not vehiclesPool:
                    vehiclesPool = list(_DEFAULT_STYLED_VEHICLES)
                vehicleName = vehiclesPool.pop(0)
                styledVehicleCD = VehicleDescriptor(typeName=vehicleName).type.compactDescr
                vehiclesPool.append(vehicleName)
                AccountSettings.setSettings(RANKED_STYLED_VEHICLES_POOL, vehiclesPool)
        styleDescr = self.__styleDescriptions.get(styleID, '')
        style = first(self.__itemsCache.items.getStyles(REQ_CRITERIA.CUSTOM(lambda item: item.id == styleID)).values())
        showStylePreview(styledVehicleCD, style, styleDescr, self._backToLeaguesCallback)
        return


class RankedBattlesRewardsYearView(RankedBattlesRewardsYearMeta, IResetablePage):
    __eventsCache = dependency.descriptor(IEventsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedBattlesRewardsYearView, self).__init__()
        self.__acyclicNotifier = None
        return

    def reset(self):
        pass

    def onChooseRewardBtnClick(self):
        showRankedSelectableReward()

    def _populate(self):
        super(RankedBattlesRewardsYearView, self)._populate()
        self.__rankedController.onYearPointsChanges += self.__update
        self.__rankedController.onSelectableRewardsChanged += self.__update
        self.__acyclicNotifier = AcyclicNotifier(self.__getTillUpdateTime, self.__update)
        self.__update()
        self.__acyclicNotifier.startNotification()

    def _dispose(self):
        self.__rankedController.onYearPointsChanges -= self.__update
        self.__rankedController.onSelectableRewardsChanged -= self.__update
        self.__acyclicNotifier.stopNotification()
        self.__acyclicNotifier.clear()
        super(RankedBattlesRewardsYearView, self)._dispose()

    def __update(self):
        currentPoints = self.__rankedController.getYearRewardPoints()
        rewardingComplete, awardPoints, isAwarded = self.__getAwardingStatus(currentPoints)
        points = awardPoints if rewardingComplete else currentPoints
        awardType = self.__rankedController.getAwardTypeByPoints(points)
        exchange = self.__rankedController.getCurrentPointToCrystalRate()
        compensation = self.__rankedController.getCompensation(points)
        awards = self.__getAwardsData(points, rewardingComplete, isAwarded)
        self.as_setDataS(rewards_vos.getYearRewardDataVO(points, awards, rewardingComplete, awardType, compensation, exchange))

    def __getAwardingStatus(self, currentPoints):
        if currentPoints > 0:
            return (False, 0, False)
        else:
            maxPoints, _ = self.__rankedController.getYearAwardsPointsMap().get(YEAR_AWARDS_ORDER[-1], (0, 0))
            for points in range(STANDARD_POINTS_COUNT, maxPoints + 1):
                finalQuest = self.__eventsCache.getHiddenQuests().get(FINAL_QUEST_PATTERN.format(points))
                if finalQuest is None:
                    return (False, 0, False)
                if finalQuest.isCompleted():
                    return (True, getDataFromFinalTokenQuestID(finalQuest.getID()), True)

            standardQuest = self.__getStandardFinalQuest()
            return (standardQuest is not None and standardQuest.getStartTimeLeft() == 0, 0, False)

    def __getAwardsData(self, points, rewardingComplete, isAwarded):
        data = []
        awardsMap = self.__rankedController.getYearAwardsPointsMap()
        for awardName in YEAR_AWARDS_ORDER:
            minPoints, maxPoints = awardsMap[awardName]
            statusText = None
            if points > maxPoints:
                status = _RBC.YEAR_REWARD_STATUS_PASSED_FINAL if rewardingComplete else _RBC.YEAR_REWARD_STATUS_PASSED
            elif maxPoints >= points >= minPoints:
                selectableRewardsCount = self.__rankedController.getYearRewardCount()
                if selectableRewardsCount:
                    status = _RBC.YEAR_REWARD_STATUS_CURRENT_CHOOSE
                    statusText = backport.text(R.strings.ranked_battles.rewardsView.tabs.year.currentChoose())
                    self.as_setChooseRewardBtnCounterS(str(selectableRewardsCount))
                elif rewardingComplete:
                    status = _RBC.YEAR_REWARD_STATUS_CURRENT_FINAL
                    statusText = text_styles.statInfo(backport.text(R.strings.ranked_battles.rewardsView.tabs.year.currentFinal()))
                else:
                    status = _RBC.YEAR_REWARD_STATUS_CURRENT
                    statusText = text_styles.statusAlert(backport.text(R.strings.ranked_battles.rewardsView.tabs.year.current()))
            else:
                status = _RBC.YEAR_REWARD_STATUS_LOCKED_FINAL if rewardingComplete else _RBC.YEAR_REWARD_STATUS_LOCKED
            pointsVO = {}
            if not isAwarded:
                pointsVO = {'text': text_styles.promoTitle(minPoints),
                 'image': backport.image(R.images.gui.maps.icons.rankedBattles.ranked_point_28x28())}
            data.append({'id': awardName,
             'status': status,
             'statusText': statusText,
             'points': pointsVO})

        return data

    def __getStandardFinalQuest(self):
        return self.__eventsCache.getHiddenQuests().get(FINAL_QUEST_PATTERN.format(STANDARD_POINTS_COUNT))

    def __getTillUpdateTime(self):
        standardFinalQuest = self.__getStandardFinalQuest()
        return standardFinalQuest.getStartTimeLeft() if standardFinalQuest is not None else time_utils.ONE_MINUTE
