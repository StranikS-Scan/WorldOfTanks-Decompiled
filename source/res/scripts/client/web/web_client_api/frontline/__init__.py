# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/frontline/__init__.py
from collections import namedtuple
from battle_pass_common import BattlePassState
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getFrontLineSkills
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.utils.functions import getRelativeUrl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController, IBattlePassController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field
from web.web_client_api.common import ItemPackType
EpicSeasonAchievements = namedtuple('EpicSeasonAchievements', ('season_id', 'episode_id', 'battle_count', 'average_xp', 'lvl', 'battle_bp_points', 'season_bp_points'))

class _RewardsSchema(W2CSchema):
    category = Field(type=basestring)


class _SkillSchema(W2CSchema):
    skill_id = Field(required=False, type=int)


@w2capi(name='frontline', key='action')
class FrontLineWebApi(W2CSchema):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    _NOT_SUPPORTED_BONUSES = ('battleToken',)

    @w2c(_RewardsSchema, name='get_rewards_data')
    def handleGetRewardsData(self, cmd):
        if hasattr(cmd, 'category') and cmd.category:
            if cmd.category == 'level':
                return self.__getAllLevelAwards()
            if cmd.category == 'vehicles':
                rewardsData = {}
                return rewardsData
            if cmd.category == 'styles':
                rewardsData = {}
                return rewardsData
        return None

    @w2c(W2CSchema, name='get_all_skills')
    def handleSkillsInfo(self, _):
        return getFrontLineSkills()

    @w2c(W2CSchema, name='get_player_skills_status')
    def handleSkillStatus(self, _):
        return {skillID:int(skill.isActivated) for skillID, skill in self.__epicController.getAllSkillsInformation().iteritems()}

    @w2c(W2CSchema, name='get_player_skill_points')
    def handleGetSkillPoints(self, _):
        return self.__epicController.getSkillPoints()

    @w2c(W2CSchema, name='is_nine_vehicles_level_disabled')
    def handleIsNineVehiclesLevelDisabled(self, _):
        return not self.__epicController.isUnlockVehiclesInBattleEnabled()

    @w2c(_SkillSchema, name='increase_player_skill')
    def handleIncreaseSkillLevel(self, cmd):
        if hasattr(cmd, 'skill_id') and cmd.skill_id:
            self.__epicController.increaseSkillLevel(cmd.skill_id)

    @w2c(W2CSchema, name='get_player_discount')
    def handleGetPlayerDiscount(self, _):
        return self.__epicController.getStoredEpicDiscount()

    @w2c(W2CSchema, name='get_is_battle_pass_completed')
    def handleGetIsBattlePassBought(self, _):
        state = self.__battlePassController.getState()
        return state == BattlePassState.COMPLETED

    @w2c(W2CSchema, name='get_metascreen_data')
    def handleGetMetaScreenData(self, _):
        currentLevel, levelProgress = self.__epicController.getPlayerLevelInfo()
        nextLevelExp = self.__epicController.getPointsProgressForLevel(currentLevel)
        data = {'lvl': currentLevel,
         'mode_alias': 'frontline',
         'max_lvl': self.__epicController.getMaxPlayerLevel(),
         'exp': levelProgress,
         'exp_for_lvl': nextLevelExp,
         'rewards_for_lvl': self.__getLevelAwards(currentLevel + 1)}
        return data

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        calendarData = dict()
        seasons = (self.__epicController.getCurrentSeason(), self.__epicController.getNextSeason(), self.__epicController.getPreviousSeason())
        for season in seasons:
            if season is not None:
                calendarData['season'] = {'id': season.getSeasonID(),
                 'start': season.getStartDate(),
                 'end': season.getEndDate()}
                calendarData['cycles'] = [ {'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate,
                 'announce_only': cycle.announceOnly} for cycle in season.getAllCycles().values() ]
                break

        return calendarData

    def __getAllLevelAwards(self):
        awardsData = dict()
        abilityPts = self.__epicController.getAbilityPointsForLevel()
        allQuests = self.__eventsCache.getAllQuests()
        for questKey, questData in allQuests.iteritems():
            if self.__epicController.TOKEN_QUEST_ID in questKey:
                _, _, questNum = questKey.partition(self.__epicController.TOKEN_QUEST_ID)
                if questNum:
                    questLvl = int(questNum)
                    questBonuses = questData.getBonuses()
                    awardsData[questLvl] = self.__packBonuses(questBonuses, questLvl, abilityPts)

        return awardsData

    def __getLevelAwards(self, level):
        allAwards = self.__getAllLevelAwards()
        return allAwards[level] if level in allAwards else []

    @classmethod
    def __packBonuses(cls, bonuses, level, abilityPts):
        result = [{'id': 0,
          'type': ItemPackType.CUSTOM_SUPPLY_POINT,
          'value': abilityPts[level - 1],
          'icon': {AWARDS_SIZES.SMALL: getRelativeUrl(backport.image(R.images.gui.maps.icons.epicBattles.awards.c_48x48.abilityToken())),
                   AWARDS_SIZES.BIG: getRelativeUrl(backport.image(R.images.gui.maps.icons.epicBattles.awards.c_80x80.abilityToken()))}}] if abilityPts else []
        for bonus in bonuses:
            if bonus.getName() in cls._NOT_SUPPORTED_BONUSES:
                continue
            bonusList = bonus.getWrappedEpicBonusList()
            for bonusEntry in bonusList:
                bonusEntry['icon'] = {size:getRelativeUrl(path) for size, path in bonusEntry['icon'].iteritems()}

            result.extend(bonusList)

        return result
