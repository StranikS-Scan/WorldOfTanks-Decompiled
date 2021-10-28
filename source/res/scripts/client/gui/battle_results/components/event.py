# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/event.py
import itertools
from constants import EVENT
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import dependency
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.awards_formatters import getEventBattleResultsFormatter, AWARDS_SIZES
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.Vehicle import getNationLessName

def makeSimpleTooltip(header, body):
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


def _getTeamFightPlace(results):
    return results.hwTeamFightPlace if results.environmentID > 0 else EVENT.INVALID_BATTLE_PLACE


class ArenaDateTimeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return backport.text(R.strings.event.resultScreen.time(), date=backport.getShortDateFormat(record), time=backport.getShortTimeFormat(record))


class CaptureStatusItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        world = info.environmentID
        return backport.text(R.strings.event.battleResults.captureStatus.num(str(world))())


class BackGroundItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        world = info.environmentID
        return backport.image(R.images.gui.maps.icons.event.battleResult.num(str(world))())


class TankNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.vehicle.shortUserName


class TankTypeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.vehicle.type


class DeathReason(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.deathReason


class DamageItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageDealt


class HW21NarrativeInfoItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return (info.environmentID, info.difficultyLevel)


class HW21RewardsItem(base.StatsItem):
    __slots__ = ()
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def _convert(self, result, reusable):
        questsProgress = reusable.personal.getQuestsProgress()
        info = reusable.getPersonalVehiclesInfo(result)
        teamFightPlace = _getTeamFightPlace(info)
        creditsReward = reusable.personal.getBaseCreditsRecords().getRecord('credits')
        keys = {'efficiency': info.hwRewardBoxKeys - info.hwRewardBoxBossKeys,
         'boss': info.hwRewardBoxBossKeys,
         'daily': self.__getDailyKeysReward(info, questsProgress)}
        return {'efficiency': self._buildMedals(keys, teamFightPlace, info.vehicle),
         'rewardBoxes': self._buildRewards(keys, creditsReward, questsProgress)}

    def _buildMedals(self, keys, teamFightPlace, vehicle):
        result = []
        if keys['daily'] > 0:
            result.append(self.__makeDailyKeysMedalVO(vehicle))
        if teamFightPlace != EVENT.INVALID_BATTLE_PLACE:
            result.append(self.__makeMedalVO(teamFightPlace, keys))
        return result

    def _buildRewards(self, keys, creditsReward, questsProgress):
        result = []

        def filterQuestsIDs(prefix):
            return [ ID for ID in questsProgress.iterkeys() if ID.startswith(prefix) ]

        result += self.__getQuestsRewardsVOs(filterQuestsIDs(EVENT.HW21_ACHIEVEMENTS_QUESTS_PREFIX))
        keysSum = sum(keys.itervalues(), 0)
        if keysSum:
            result.append(self.__makeKeysRewardVO(keys, keysSum))
        result += self.__getQuestsRewardsVOs(filterQuestsIDs(EVENT.REWARD_BOX.QUEST_PREFIX))
        result.append(self.__makeCreditsRewardVO(creditsReward))
        return result

    def __getDailyKeysReward(self, info, questsProgress):
        vehIntCD = info.vehicle.intCD
        vehDailyQuestID = EVENT.REWARD_BOX.KEY_DAILY_QUEST_FORMAT.format(vehIntCD)
        isQuestCompleted = lambda (_, prev, cur): cur.get('bonusCount', 0) - prev.get('bonusCount', 0) > 0
        progress = questsProgress.get(vehDailyQuestID, None)
        return 0 if progress is None or not isQuestCompleted(progress) else self.gameEventController.getVehiclesController().getDailyKeysReward(vehIntCD)

    def __getQuestsRewardsVOs(self, questIDs):
        if not questIDs:
            return []
        formatter = getEventBattleResultsFormatter()
        quests = self.eventsCache.getAllQuests(lambda q: q.getID() in questIDs)
        return [ self.__getBonusVO(bonus) for bonus in formatter.format(itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues()))) ]

    def __getBonusVO(self, bonus):
        return {'icon': bonus.getImage(AWARDS_SIZES.BIG),
         'tooltip': bonus.tooltip,
         'specialArgs': bonus.specialArgs,
         'specialAlias': bonus.specialAlias,
         'isSpecial': bonus.isSpecial,
         'label': bonus.label}

    def __makeDailyKeysMedalVO(self, vehicle):
        return {'icon': backport.image(R.images.gui.maps.icons.event.battleResult.rewards.daily()),
         'isTooltipWulf': True,
         'specialArgs': [vehicle.intCD],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_DAILY_INFO,
         'label': backport.text(R.strings.event.resultScreen.medal.dailyQuest.label())}

    def __makeMedalVO(self, teamFightPlace, keys):
        return {'icon': backport.image(R.images.gui.maps.icons.event.battleResult.medals.personal.num(teamFightPlace)()),
         'tooltip': '',
         'isSpecial': True,
         'specialArgs': [backport.image(R.images.gui.maps.icons.event.battleResult.medals.personal.num(teamFightPlace)()), keys['efficiency']],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_EFFICIENT_INFO,
         'label': backport.text(R.strings.event.resultScreen.medal.teamFightPlace.label())}

    def __makeKeysRewardVO(self, keys, keysSum):
        return {'icon': backport.image(R.images.gui.maps.icons.event.battleResult.rewards.key()),
         'tooltip': '',
         'isSpecial': False,
         'specialArgs': [keys],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_KEY_INFO,
         'label': str(keysSum)}

    def __makeCreditsRewardVO(self, creditsReward):
        result = makeSimpleTooltip(header=backport.text(R.strings.tooltips.credits.header()), body=backport.text(R.strings.tooltips.credits.body()))
        result.update({'icon': backport.image(R.images.gui.maps.icons.event.battleResult.rewards.money_silver_big()),
         'label': backport.getNiceNumberFormat(creditsReward)})
        return result


class EventPointsLeftItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.eventPointsLeft


class MatterTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltips.matterHeader()), body=backport.text(R.strings.event.resultScreen.tooltips.matter()))


class KillTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.battle_results.team.fragHeader.header()), body=backport.text(R.strings.battle_results.team.fragHeader.body()))


class DamageTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.battle_results.team.damageHeader.header()), body=backport.text(R.strings.battle_results.team.damageHeader.body()))


class DamageBlockedByArmorTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.damageBlockedByArmor.header()), body=backport.text(R.strings.event.resultScreen.tooltip.damageBlockedByArmor.description()))


class RewardBoxKeysTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.rewardBoxKeysTooltip.header()), body=backport.text(R.strings.event.resultScreen.tooltip.rewardBoxKeysTooltip.description()))


class MedalsTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.medalsTooltip.header()), body=backport.text(R.strings.event.resultScreen.tooltip.medalsTooltip.description()))


class PlatoonTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.platoonTooltip.header()), body=backport.text(R.strings.event.resultScreen.tooltip.platoonTooltip.description()))


class NameTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.nameTooltip.header()), body=backport.text(R.strings.event.resultScreen.tooltip.nameTooltip.description()))


class TankTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.tankTooltip.header()), body=backport.text(R.strings.event.resultScreen.tooltip.tankTooltip.description()))


class EventVehicleStatsBlock(vehicles.RegularVehicleStatsBlock):
    __slots__ = ('matter', 'matterOnTank', 'tankType', 'banStatus', 'banStatusTooltip', 'teamFightPlace', 'rewardBoxKeys', 'damageBlockedByArmor', 'medals')
    _NO_BAN = 'ok'
    _BANNED = 'ban'
    _WARNED = 'warning'
    _MEDAL_IMG_FORMAT = 'battle_place_{}'

    def __init__(self, meta=None, field='', *path):
        super(EventVehicleStatsBlock, self).__init__(meta, field, *path)
        self.matter = 0
        self.matterOnTank = 0
        self.banStatus = self._NO_BAN
        self.banStatusTooltip = ''
        self.teamFightPlace = EVENT.INVALID_BATTLE_PLACE
        self.rewardBoxKeys = 0
        self.damageBlockedByArmor = 0
        self.medals = []

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        self.matter = result.eventPoints
        self.matterOnTank = result.eventPointsLeft
        self.teamFightPlace = _getTeamFightPlace(result)
        self.rewardBoxKeys = result.hwRewardBoxKeys
        self.damageBlockedByArmor = result.damageBlockedByArmor
        self.medals = self.__buildMedals(self.teamFightPlace)
        gotWarning = result.eventAFKViolator
        if result.eventAFKBanned:
            self.banStatus = self._BANNED
            self.banStatusTooltip = TOOLTIPS.EVENT_AFK_BAN
        elif gotWarning:
            self.banStatus = self._WARNED
            self.banStatusTooltip = TOOLTIPS.EVENT_AFK_WARNING
        else:
            self.banStatus = self._NO_BAN
            self.banStatusTooltip = ''

    def _setVehicleInfo(self, vehicle):
        super(EventVehicleStatsBlock, self)._setVehicleInfo(vehicle)
        self.tankType = vehicle.type

    def __buildMedals(self, teamFightPlace):
        return [] if teamFightPlace == EVENT.INVALID_BATTLE_PLACE else [self.__makeMedalVO(teamFightPlace)]

    def __makeMedalVO(self, teamFightPlace):
        return {'icon': backport.image(R.images.gui.maps.icons.event.battleResult.medals.team.num(teamFightPlace)()),
         'tooltip': '',
         'isSpecial': False,
         'label': backport.text(R.strings.event.resultScreen.medal.teamFightPlace.label())}


class PersonalFirstTeamItemSortKey(sort_keys.TeamItemSortKey):
    __slots__ = ('_sortKey',)

    def __init__(self, vehicleInfo, compareKey):
        super(PersonalFirstTeamItemSortKey, self).__init__(vehicleInfo)
        self._sortKey = compareKey

    def _cmp(self, other):
        sortKey = self._sortKey
        return cmp(getattr(other.info, sortKey), getattr(self.info, sortKey))


class EventBattlesTeamStatsBlock(vehicles.TeamStatsBlock):
    gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(EventBattlesTeamStatsBlock, self).__init__(EventVehicleStatsBlock, meta, field, *path)

    def setRecord(self, result, reusable):
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: PersonalFirstTeamItemSortKey(info, 'eventPoints'))
        super(EventBattlesTeamStatsBlock, self).setRecord(allies, reusable)


class EventCombinedTeamStatBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        vo = {'damage': 0,
         'matter': 0,
         'kills': 0,
         'blocked': 0,
         'keys': 0}
        allies, _ = reusable.getBiDirectionTeamsIterator(result)
        for veh in allies:
            vo['damage'] += veh.damageDealt
            vo['matter'] += veh.eventPoints
            vo['kills'] += veh.kills
            vo['blocked'] += veh.damageBlockedByArmor
            vo['keys'] += veh.hwRewardBoxKeys

        return vo


class VehicleIconItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        vehIconName = getNationLessName(info.vehicle.name).replace('-', '_')
        return backport.image(R.images.gui.maps.shop.vehicles.c_600x450.dyn(vehIconName)())


class IsWinItem(base.StatsItem):
    eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        difficultyEnv = self.eventsCache.getGameEventData()['difficulty']['levelsEnvironment'][info.difficultyLevel]
        return info.environmentID > difficultyEnv['maxEnvironmentID']


class DifficultyTextItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return backport.text(R.strings.event.resultScreen.difficultyLevel.num(str(info.difficultyLevel))())


class DifficultyIconItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return backport.image(R.images.gui.maps.icons.event.battleResult.difficulty.num(str(info.difficultyLevel))())


class PlayerNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.player.realName


class PlayerClanItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.player.clanAbbrev
