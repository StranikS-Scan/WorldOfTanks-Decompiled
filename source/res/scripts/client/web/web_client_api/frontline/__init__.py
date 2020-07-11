# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/frontline/__init__.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkIfVehicleIsHidden
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkEpicRewardVehAlreadyBought
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getFrontLineSkills
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IEpicBattleMetaGameController, IEventProgressionController
from skeletons.gui.server_events import IEventsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field
from skeletons.gui.shared import IItemsCache
EpicSeasonAchievements = namedtuple('EpicSeasonAchievements', ('season_id', 'episode_id', 'battle_count', 'average_xp', 'award_points', 'lvl'))
BattleRoyaleSeasonAchievements = namedtuple('EpicSeasonAchievements', ('season_id', 'episode_id', 'battle_count', 'kill_count', 'award_points', 'lvl'))

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
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_RewardsSchema, name='get_rewards_data')
    def handleGetRewardsData(self, cmd):
        if hasattr(cmd, 'category') and cmd.category:
            if cmd.category == 'level':
                return self.__eventProgression.getAllLevelAwards()
            if cmd.category == 'vehicles':
                rewardsData = {}
                vehicleInfo = []
                for intCD, price in self.__eventProgression.rewardVehicles:
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

    @w2c(W2CSchema, name='get_exchange_info')
    def getExchangeInfo(self, _):
        return self.__eventProgression.getExchangeInfo()

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

    @w2c(W2CSchema, name='get_metascreen_data')
    def handleGetMetaScreenData(self, _):
        levelInfo = self.__eventProgression.getPlayerLevelInfo()
        nextLevelExp = self.__eventProgression.getPointsProgressForLevel(levelInfo.currentLevel)
        metaGameStats = self.__eventProgression.getStats()
        data = {'lvl': levelInfo.currentLevel,
         'mode_alias': self.__eventProgression.getCurrentModeAlias(),
         'max_lvl': self.__eventProgression.getMaxPlayerLevel(),
         'exp': levelInfo.levelProgress,
         'exp_for_lvl': nextLevelExp,
         'rewards_for_lvl': self.__eventProgression.getLevelAwards(levelInfo.currentLevel + 1),
         'quest_ids': self.__eventProgression.getActiveQuestIDs(),
         'battle_count': metaGameStats.battleCount,
         'award_points': self.__eventProgression.actualRewardPoints,
         'season_award_points': self.__eventProgression.seasonRewardPoints,
         'max_award_points': self.__eventProgression.maxRewardPoints}
        modeData = self.__eventProgression.getEpicMetascreenData()
        if modeData:
            data.update(modeData)
        return data

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        return self.__eventProgression.getCalendarInfo()

    @w2c(W2CSchema, name='get_seasons_achievements')
    def getSeasonAchievements(self, _):
        dossierDescr = self.__itemsCache.items.getAccountDossier().getDossierDescr()
        seasonsAchievements = {'frontline': self.__getSeasonAchievements(dossierDescr.expand('epicSeasons'), EpicSeasonAchievements),
         'steel_hunter': self.__getSeasonAchievements(dossierDescr.expand('battleRoyaleSeasons'), BattleRoyaleSeasonAchievements)}
        return seasonsAchievements

    def __getSeasonAchievements(self, achievements, template):
        seasonsAchievements = []
        for seasonID, cycleID in achievements:
            if not self.__eventProgression.validateSeasonData(seasonID, cycleID):
                continue
            key = (seasonID, cycleID)
            seasonsAchievements.append(template(*(key + achievements[key]))._asdict())

        return seasonsAchievements
