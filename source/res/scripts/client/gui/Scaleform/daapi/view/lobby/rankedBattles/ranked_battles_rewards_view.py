# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_rewards_view.py
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_STYLED_VEHICLES_POOL
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsLeaguesMeta import RankedBattlesRewardsLeaguesMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsMeta import RankedBattlesRewardsMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsRanksMeta import RankedBattlesRewardsRanksMeta
from gui.Scaleform.daapi.view.meta.RankedBattlesRewardsYearMeta import RankedBattlesRewardsYearMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import DEFAULT_REWARDS_COUNT, YEAR_AWARDS_ORDER, YEAR_AWARDS_POINTS_MAP
from gui.ranked_battles.ranked_builders import rewards_vos
from gui.ranked_battles.ranked_formatters import getRanksColumnRewardsFormatter
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.event_dispatcher import showStylePreview
from helpers import dependency
from items.vehicles import VehicleDescriptor
from shared_utils import first
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
_REWARDS_COMPONENTS = (RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI, RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI, RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI)

class RankedBattlesRewardsView(RankedBattlesRewardsMeta, IResetablePage):
    _rankedController = dependency.descriptor(IRankedBattlesController)

    def onTabChanged(self, viewId):
        self._updateSounds(viewId)

    def setActiveTab(self, linkage=None):
        raise NotImplementedError

    def _populate(self):
        super(RankedBattlesRewardsView, self)._populate()
        self.setActiveTab()

    def _updateSounds(self, selectedLinkage):
        raise NotImplementedError()


class RankedRewardsSeasonOffView(RankedBattlesRewardsView):

    def reset(self):
        self._updateSounds(None)
        return

    def setActiveTab(self, linkage=None):
        tabs = rewards_vos.getSeasonOffTabs()
        self.as_setTabsDataS(tabs)

    def _updateSounds(self, _):
        self._rankedController.getSoundManager().setProgressSound()


class RankedRewardsSeasonOnView(RankedBattlesRewardsView):

    def onTabChanged(self, viewId):
        super(RankedRewardsSeasonOnView, self).onTabChanged(viewId)
        component = self.getComponent(viewId)
        if component is not None:
            component.reset()
        return

    def reset(self):
        self.setActiveTab()
        for linkage in _REWARDS_COMPONENTS:
            component = self.getComponent(linkage)
            if component is not None:
                component.reset()

        return

    def setActiveTab(self, linkage=None):
        if linkage not in _REWARDS_COMPONENTS:
            if self._rankedController.isAccountMastered():
                linkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI
            else:
                linkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI
        tabs = rewards_vos.getSeasonOnTabs(linkage)
        self.as_setTabsDataS(tabs)

    def _updateSounds(self, linkage):
        isMastered = self._rankedController.isAccountMastered()
        soundManager = self._rankedController.getSoundManager()
        if linkage == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI or isMastered:
            soundManager.setProgressSound()
        else:
            soundManager.setProgressSound(self._rankedController.getCurrentDivision().getUserID())


class RankedBattlesRewardsRanksView(RankedBattlesRewardsRanksMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedBattlesRewardsRanksView, self).__init__()
        self.__selectedDivision = self.__rankedController.getCurrentDivision()
        self.__iconSize = AWARDS_SIZES.SMALL
        self.__maxRewardsCountInRow = DEFAULT_REWARDS_COUNT
        self.__bonusFormatter = getRanksColumnRewardsFormatter(self.__maxRewardsCountInRow)

    def onDivisionIdxChanged(self, divisionIdx):
        self.__selectedDivision = self.__rankedController.getDivisions()[int(divisionIdx)]
        self.__updateSounds()
        self.as_setRewardsS(self.__getRewardsData(self.__selectedDivision))

    def onRequestData(self, iconSizeID, rewardsCount):
        self.__iconSize = iconSizeID
        self.__maxRewardsCountInRow = int(rewardsCount)
        self.as_setRewardsS(self.__getRewardsData(self.__selectedDivision))

    def reset(self):
        currentDivision = self.__rankedController.getCurrentDivision()
        if self.__selectedDivision != currentDivision:
            self.__selectedDivision = currentDivision
            self.__onUpdate(True)
        self.__updateSounds()

    def _populate(self):
        super(RankedBattlesRewardsRanksView, self)._populate()
        self.__rankedController.onUpdated += self.__onUpdate
        self.as_setDivisionsDataS(self.__getDivisionsData(), False)

    def _dispose(self):
        self.__bonusFormatter = None
        self.__selectedDivision = None
        self.__rankedController.onUpdated -= self.__onUpdate
        super(RankedBattlesRewardsRanksView, self)._dispose()
        return

    def __getRankRewards(self, rank):
        quest = rank.getQuest()
        return self.__bonusFormatter.getFormattedBonuses(quest.getBonuses(), self.__iconSize) if quest else []

    def __getDivisionsData(self):
        data = []
        for division in self.__rankedController.getDivisions():
            data.append(rewards_vos.getDivisionVO(division))

        return data

    def __getRewardsData(self, division):
        rewards = []
        self.__bonusFormatter.setMaxRewardsCount(self.__maxRewardsCountInRow)
        currentRankID, _ = self.__rankedController.getMaxRank()
        for rankID in division.getRanksIDs():
            rank = self.__rankedController.getRank(rankID)
            rewards.append(rewards_vos.getRankRewardsVO(rank, self.__getRankRewards(rank), currentRankID))

        return rewards

    def __onUpdate(self, immediately=False):
        self.as_setDivisionsDataS(self.__getDivisionsData(), immediately)
        self.as_setRewardsS(self.__getRewardsData(self.__selectedDivision))

    def __updateSounds(self):
        soundManager = self.__rankedController.getSoundManager()
        if self.__selectedDivision.isUnlocked():
            soundManager.setProgressSound(self.__selectedDivision.getUserID())
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID(), isLoud=False)


_DEFAULT_STYLED_VEHICLES = ('uk:GB91_Super_Conqueror', 'china:Ch41_WZ_111_5A', 'ussr:R148_Object_430_U', 'japan:J20_Type_2605')

class RankedBattlesRewardsLeaguesView(RankedBattlesRewardsLeaguesMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RankedBattlesRewardsLeaguesView, self).__init__()
        self.__styleDescriptions = {}

    def onStyleClick(self, styleCD):
        self.__showStylePreview(int(styleCD))

    def reset(self):
        pass

    @classmethod
    def _backToLeaguesCallback(cls):
        cls.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
         'rewardsSelectedTab': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI})

    def _populate(self):
        super(RankedBattlesRewardsLeaguesView, self)._populate()
        data = self.__getLeaguesData()
        self.as_setRewardsS({'leagues': data,
         'description': backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.description())})

    def __getLeaguesData(self):
        leaguesRewardsData = self.__rankedController.getLeagueRewards('customizations')
        result = []
        formatter = getRanksColumnRewardsFormatter()
        for data in leaguesRewardsData:
            leagueID = data['league']
            styleBonus = first(formatter.getPreformattedBonuses(data['awards']))
            if leagueID and styleBonus:
                isCurrent = self.__rankedController.getLeagueProvider().webLeague.league == leagueID
                styleCD = styleBonus.specialArgs[0]
                self.__styleDescriptions[styleCD] = backport.text(R.strings.ranked_battles.rewardsView.tabs.leagues.description.dyn('league%s' % leagueID)())
                result.append(rewards_vos.getLeagueRewardVO(leagueID, styleBonus, isCurrent))

        return result

    def __showStylePreview(self, styleCD):
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
                styledVehicleCD = sortedVehicles[0][0]
            if not styledVehicleCD:
                vehiclesPool = AccountSettings.getSettings(RANKED_STYLED_VEHICLES_POOL)
                if not vehiclesPool:
                    vehiclesPool = list(_DEFAULT_STYLED_VEHICLES)
                vehicleName = vehiclesPool.pop(0)
                styledVehicleCD = VehicleDescriptor(typeName=vehicleName).type.compactDescr
                vehiclesPool.append(vehicleName)
                AccountSettings.setSettings(RANKED_STYLED_VEHICLES_POOL, vehiclesPool)
        styleDescr = self.__styleDescriptions.get(styleCD, '')
        showStylePreview(styledVehicleCD, self.__itemsCache.items.getItemByCD(styleCD), styleDescr, self._backToLeaguesCallback)
        return


class RankedBattlesRewardsYearView(RankedBattlesRewardsYearMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def reset(self):
        pass

    def _populate(self):
        super(RankedBattlesRewardsYearView, self)._populate()
        self.__rankedController.onYearPointsChanges += self.__updatePoints
        self.__updatePoints()

    def _dispose(self):
        self.__rankedController.onYearPointsChanges -= self.__updatePoints
        super(RankedBattlesRewardsYearView, self)._dispose()

    def __updatePoints(self):
        points = self.__rankedController.getYearRewardPoints()
        data = {'title': backport.text(R.strings.ranked_battles.rewardsView.tabs.year.title(), points=points),
         'titleIcon': backport.image(R.images.gui.maps.icons.rankedBattles.ranked_point_28x28()),
         'points': points,
         'rewards': self.__getAwardsData(points)}
        self.as_setDataS(data)

    @classmethod
    def __getAwardsData(cls, points):
        data = []
        for awardName in YEAR_AWARDS_ORDER:
            minPoints, maxPoints = YEAR_AWARDS_POINTS_MAP[awardName]
            if points > maxPoints:
                status = RANKEDBATTLES_CONSTS.YEAR_REWARD_STATUS_PASSED
            elif maxPoints >= points >= minPoints:
                status = RANKEDBATTLES_CONSTS.YEAR_REWARD_STATUS_CURRENT
            else:
                status = RANKEDBATTLES_CONSTS.YEAR_REWARD_STATUS_LOCKED
            data.append({'id': awardName,
             'status': status})

        return data
