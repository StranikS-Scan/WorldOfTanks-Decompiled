# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/frontline/__init__.py
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import triggerPrestige, checkIfVehicleIsHidden
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkEpicRewardVehAlreadyBought
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getAwardsForLevel, getAwardsForPrestige
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getFrontLineSkills, getEpicGamePlayerPrestigePoints
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
from web_client_api import w2c, w2capi, W2CSchema, Field
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache

class _RewardsSchema(W2CSchema):
    category = Field(type=basestring)


class _SkillSchema(W2CSchema):
    skill_id = Field(required=False, type=int)


@w2capi(name='frontline', key='action')
class FrontLineWebApi(W2CSchema):
    _frontLineCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='get_metascreen_data')
    def handleGetMetaScreenData(self, _):
        prestige, level, exp = self._frontLineCtrl.getPlayerLevelInfo()
        nextLevelExp = self._frontLineCtrl.getPointsProgressForLevel(level)
        maxPrestige = self._frontLineCtrl.getMaxPlayerPrestigeLevel()
        data = {'lvl': level if prestige < maxPrestige else '',
         'max_lvl': self._frontLineCtrl.getMaxPlayerLevel(),
         'prestige': prestige,
         'max_prestige': maxPrestige,
         'stageLimit': self._frontLineCtrl.getStageLimit(),
         'exp': exp,
         'exp_for_lvl': nextLevelExp,
         'rewards_for_lvl': getAwardsForLevel(level + 1),
         'rewards_for_prestige': getAwardsForPrestige(prestige + 1)}
        return data

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        calendarData = dict()
        currentSeason = self._frontLineCtrl.getCurrentSeason()
        if currentSeason is not None:
            calendarData['season'] = {'id': currentSeason.getSeasonID(),
             'start': currentSeason.getStartDate(),
             'end': currentSeason.getEndDate()}
            calendarData['cycles'] = list()
            for cycle in currentSeason.getAllCycles().values():
                calendarData['cycles'].append({'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate})

        return calendarData

    @w2c(_RewardsSchema, name='get_rewards_data')
    def handleGetRewardsData(self, cmd):
        if hasattr(cmd, 'category') and cmd.category:
            if cmd.category == 'level':
                return getAwardsForLevel()
            if cmd.category == 'prestige':
                return getAwardsForPrestige()
            if cmd.category == 'vehicles':
                rewardsData = dict()
                rewardsData['prestige_points'] = getEpicGamePlayerPrestigePoints()
                vehicleInfo = []
                inventoryVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
                for intCD, price in self._frontLineCtrl.getRewardVehicles().iteritems():
                    vehicleInfo.append({'vehIntCD': intCD,
                     'price_in_prestige_points': price,
                     'is_in_inventory': intCD in inventoryVehicles,
                     'already_bought_by_rewards_points': checkEpicRewardVehAlreadyBought(intCD),
                     'show_ttc': not checkIfVehicleIsHidden(intCD)})

                rewardsData['vehicles'] = sorted(vehicleInfo, key=lambda v: v['price_in_prestige_points'])
                return rewardsData
        return None

    @w2c(W2CSchema, name='up_prestige')
    def handlePrestigeUp(self, _):
        triggerPrestige()

    @w2c(W2CSchema, name='get_all_skills')
    def handleSkillsInfo(self, _):
        return getFrontLineSkills()

    @w2c(W2CSchema, name='get_player_skills_status')
    def handleSkillStatus(self, _):
        result = {}
        for skillID, epicSkillsListGenerator in self._frontLineCtrl.getAllUnlockedSkillLevelsBySkillId().iteritems():
            skills = list(epicSkillsListGenerator)
            if skills:
                result[skillID] = skills[-1].level
            result[skillID] = 0

        return result

    @w2c(W2CSchema, name='get_player_skill_points')
    def handleGetSkillPoints(self, _):
        return self._frontLineCtrl.getSkillPoints()

    @w2c(_SkillSchema, name='increase_player_skill')
    def handleIncreaseSkillLevel(self, cmd):
        if hasattr(cmd, 'skill_id') and cmd.skill_id:
            self._frontLineCtrl.increaseSkillLevel(cmd.skill_id)

    @w2c(W2CSchema, name='get_player_discount')
    def handleGetPlayerDiscount(self, _):
        return self._frontLineCtrl.getStoredEpicDiscount()
