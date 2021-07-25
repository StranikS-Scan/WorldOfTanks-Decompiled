# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/maps_training.py
import logging
from ArenaType import parseTypeID
from constants import VEHICLE_CLASSES
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.components import base
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from maps_training_common.helpers import getMapsTrainingAwards
from maps_training_common.maps_training_constants import MAX_SCENARIO_PROGRESS
from skeletons.gui.game_control import IMapsTrainingController
_logger = logging.getLogger(__name__)
_IMAGES_FOLDER_PATH = '../maps/icons/maps_training/battle_result/'
_BG_FOLDER_PATH = _IMAGES_FOLDER_PATH + 'background/'
_BG_IMAGE_FORMAT = '{team_result}.png'
_STAT_ICON_PATH = _IMAGES_FOLDER_PATH + '{0}.png'
_STAT_ICON_TOOLTIP_PATH = _IMAGES_FOLDER_PATH + 'tooltip/{0}.png'
_STAT_FIELD_NAMES = ('damageDealt', 'damageBlockedByArmor')
BATTLE_STATS_KILLS = 'kills'
BATTLE_STATS_RESULT_FIELDS = {BATTLE_STATS_KILLS: 'kills'}
BATTLE_STATS_ICONS = {BATTLE_STATS_KILLS: 'statIconDestroyed'}

class BattleResultBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        teamResultStr = backport.text(R.strings.maps_training.result.dyn('title' + teamResult.title())())
        self.addNextComponent(base.DirectStatsItem('win', teamResult == PLAYER_TEAM_RESULT.WIN))
        self.addNextComponent(base.DirectStatsItem('value', teamResult))
        self.addNextComponent(base.DirectStatsItem('str', teamResultStr))


class BattleGoalsBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        battleGoals = result['personal']['avatar']['vseBattleResults']
        classes = ('heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG')
        totalClasses = len(classes)
        for vehClass, goal, res in zip(classes, battleGoals[:totalClasses], battleGoals[totalClasses:]):
            self.addNextComponent(base.DirectStatsItem(vehClass, [goal, res]))


class BattleDurationItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return result['common']['duration']


class StatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result['personal'])
        for statType, statFieldName in BATTLE_STATS_RESULT_FIELDS.iteritems():
            statVal = info.__getattribute__(statFieldName)
            self.addNextComponent(base.DirectStatsItem('', {'id': statType,
             'value': statVal}))

        totalClasses = len(VEHICLE_CLASSES)
        questKills = 0
        battleResult = result['personal']['avatar']['vseBattleResults']
        for goal, kills in zip(battleResult[:totalClasses], battleResult[totalClasses:]):
            if goal == 0:
                continue
            questKills += goal if kills > goal else kills

        self.addNextComponent(base.DirectStatsItem('', {'id': 'questKills',
         'value': questKills}))


class GeometryIdItem(base.StatsItem):

    def _convert(self, result, reusable):
        typeId = reusable.common.arenaType.getID()
        _, geometryID = parseTypeID(typeId)
        return geometryID


class TeamItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['personal']['avatar']['team']


class VehicleBlock(base.StatsBlock):

    def setRecord(self, result, reusable):
        vehicle = reusable.getPersonalVehiclesInfo(result['personal']).vehicle
        self.addNextComponent(base.DirectStatsItem('type', vehicle.type))
        self.addNextComponent(base.DirectStatsItem('name', vehicle.name))


class MTProgressMixin(object):
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def _getScenarioData(self, result, reusable):
        typeId = reusable.common.arenaType.getID()
        _, geometryID = parseTypeID(typeId)
        vehType = reusable.getPersonalVehiclesInfo(result['personal']).vehicle.type
        team = result['personal']['avatar']['team']
        config = self.mapsTrainingController.getConfig()
        rewardsConfig = config.get('rewards', {}).get(geometryID, {})
        scenarioConfig = config.get('scenarios', {}).get(geometryID, {}).get(team, {}).get(vehType, {})
        playerProgress = result['personal']['avatar']['scenarioProgress']
        return (scenarioConfig, rewardsConfig, playerProgress)


class DoneValueItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return result['personal']['avatar']['scenarioProgress']['result']


class ScenarioProgressBlock(base.StatsBlock, MTProgressMixin):
    __slots__ = ()

    def setRecord(self, result, reusable):
        scenarioConfig, _, playerProgress = self._getScenarioData(result, reusable)
        totalTargets = sum(scenarioConfig['goals'].values())
        self.addNextComponent(base.DirectStatsItem('', (totalTargets, playerProgress['level'] > 0, playerProgress['level'] > 0 and playerProgress['prevBest'] > 0)))


class RewardsBlock(base.StatsBlock, MTProgressMixin):
    __slots__ = ()

    def setRecord(self, result, reusable):
        _, rewardsConfig, playerProgress = self._getScenarioData(result, reusable)
        bonus = getMapsTrainingAwards(rewardsConfig, playerProgress['prevBest'], playerProgress['level'], result['personal']['avatar']['mt_mapComplete'])
        for rewardName, rewardData in bonus.iteritems():
            for item in getNonQuestBonuses(rewardName, rewardData):
                self.addNextComponent(base.DirectStatsItem('', item))


class AccountProgressBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        hasImproved = result['personal']['avatar']['mt_progressImproved']
        self.addNextComponent(base.DirectStatsItem('hasImproved', hasImproved))


class WasDoneItem(base.StatsItem, MTProgressMixin):

    def _convert(self, result, reusable):
        _, __, playerProgress = self._getScenarioData(result, reusable)
        return playerProgress['prevBest'] == MAX_SCENARIO_PROGRESS
