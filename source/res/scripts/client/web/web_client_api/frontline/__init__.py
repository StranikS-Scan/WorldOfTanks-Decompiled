# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/frontline/__init__.py
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkIfVehicleIsHidden
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkEpicRewardVehAlreadyBought
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getAwardsForLevel
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getFrontLineSkills
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IEpicBattleMetaGameController, IEventProgressionController
from skeletons.gui.server_events import IEventsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field
from skeletons.gui.shared import IItemsCache

class _RewardsSchema(W2CSchema):
    category = Field(type=basestring)


class _SkillSchema(W2CSchema):
    skill_id = Field(required=False, type=int)


_REWARD_VEHICLE_AVAILABLE = 'available'
_REWARD_VEHICLE_OWNED = 'owned'
_REWARD_VEHICLE_PURCHASED = 'purchased'

@w2capi(name='frontline', key='action')
class FrontLineWebApi(W2CSchema):
    __frontlineCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __eventProgCtrl = dependency.descriptor(IEventProgressionController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='get_metascreen_data')
    def handleGetMetaScreenData(self, _):
        _, level, exp = self.__frontlineCtrl.getPlayerLevelInfo()
        nextLevelExp = self.__frontlineCtrl.getPointsProgressForLevel(level)
        metaGameStats = self.__itemsCache.items.epicMetaGame
        dossier = self.__itemsCache.items.getAccountDossier()
        achievements = dossier.getDossierDescr().expand('epicSeasons')
        seasonsAchievements = []
        for seasonID, episodeID in achievements:
            key = (seasonID, episodeID)
            battleCount, averageXp, awardPoints, lvl = achievements[key]
            seasonsAchievements.append({'season_id': seasonID,
             'episode_id': episodeID,
             'battle_count': battleCount,
             'average_xp': averageXp,
             'award_points': awardPoints,
             'lvl': lvl})

        data = {'lvl': level,
         'max_lvl': self.__frontlineCtrl.getMaxPlayerLevel(),
         'exp': exp,
         'exp_for_lvl': nextLevelExp,
         'rewards_for_lvl': getAwardsForLevel(level + 1),
         'quest_ids': self.__eventProgCtrl.questIDs,
         'average_xp': metaGameStats.averageXP,
         'battle_count': metaGameStats.battleCount,
         'award_points': self.__eventProgCtrl.actualRewardPoints,
         'season_award_points': self.__eventProgCtrl.seasonRewardPoints,
         'max_award_points': self.__eventProgCtrl.maxRewardPoints,
         'seasons_achievements': seasonsAchievements}
        return data

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        calendarData = dict()
        seasons = (self.__frontlineCtrl.getCurrentSeason(), self.__frontlineCtrl.getNextSeason(), self.__frontlineCtrl.getPreviousSeason())
        selectedSeason = first(filter(None, seasons))
        if selectedSeason is not None:
            calendarData['season'] = {'id': selectedSeason.getSeasonID(),
             'start': selectedSeason.getStartDate(),
             'end': selectedSeason.getEndDate()}
            calendarData['cycles'] = list()
            for cycle in selectedSeason.getAllCycles().values():
                calendarData['cycles'].append({'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate,
                 'announce_only': cycle.announceOnly})

        return calendarData

    @w2c(_RewardsSchema, name='get_rewards_data')
    def handleGetRewardsData(self, cmd):
        if hasattr(cmd, 'category') and cmd.category:
            if cmd.category == 'level':
                return getAwardsForLevel()
            if cmd.category == 'vehicles':
                rewardsData = {}
                vehicleInfo = []
                for intCD, price in self.__eventProgCtrl.rewardVehicles:
                    vehicle = self.__itemsCache.items.getItemByCD(intCD)
                    obtained = checkEpicRewardVehAlreadyBought(intCD)
                    owned = bool(vehicle.inventoryCount)
                    if owned:
                        state = _REWARD_VEHICLE_OWNED
                    elif obtained:
                        state = _REWARD_VEHICLE_PURCHASED
                    else:
                        state = _REWARD_VEHICLE_AVAILABLE
                    vehicleInfo.append({'vehIntCD': intCD,
                     'price': price,
                     'state': state,
                     'show_ttc': not checkIfVehicleIsHidden(intCD)})

                rewardsData['vehicles'] = sorted(vehicleInfo, key=lambda v: v['price'])
                return rewardsData
        return None

    @w2c(W2CSchema, name='get_all_skills')
    def handleSkillsInfo(self, _):
        return getFrontLineSkills()

    @w2c(W2CSchema, name='get_player_skills_status')
    def handleSkillStatus(self, _):
        result = {}
        for skillID, epicSkillsListGenerator in self.__frontlineCtrl.getAllUnlockedSkillLevelsBySkillId().iteritems():
            skills = list(epicSkillsListGenerator)
            if skills:
                result[skillID] = skills[-1].level
            result[skillID] = 0

        return result

    @w2c(W2CSchema, name='get_player_skill_points')
    def handleGetSkillPoints(self, _):
        return self.__frontlineCtrl.getSkillPoints()

    @w2c(_SkillSchema, name='increase_player_skill')
    def handleIncreaseSkillLevel(self, cmd):
        if hasattr(cmd, 'skill_id') and cmd.skill_id:
            self.__frontlineCtrl.increaseSkillLevel(cmd.skill_id)

    @w2c(W2CSchema, name='get_player_discount')
    def handleGetPlayerDiscount(self, _):
        return self.__frontlineCtrl.getStoredEpicDiscount()
