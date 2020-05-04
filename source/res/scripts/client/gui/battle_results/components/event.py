# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/event.py
from constants import DEATH_REASON_ALIVE
from gui import makeHtmlString
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.secret_event import RewardListMixin
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.formatters.icons import makeImageTag
from helpers import dependency, int2roman
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base, vehicles, style
from items import vehicles as itemsVehicles
from helpers.i18n import makeString
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip, getAbsoluteUrl
from shared_utils import first
from gui.shared.utils import toUpper
_HUNDRED_PERCENT = 100.0

class ArenaDateTimeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return backport.text(R.strings.event.resultScreen.time(), date=backport.getShortDateFormat(record), time=backport.getShortTimeFormat(record))


class ReasonItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        messageType = reusable.getPersonalTeamResult()
        endBattleAcc = R.strings.event.endbattle
        return {'title': toUpper(backport.text(endBattleAcc.title.dyn(messageType)())),
         'subTitle': toUpper(backport.text(endBattleAcc.subtitle.dyn('{}_reason_{}'.format(messageType, reusable.common.finishReason))()))}


class BackGroundItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return backport.image(R.images.gui.maps.icons.secretEvent.backgrounds.battle_result())


class TankStatusItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        playerInfo = reusable.getPlayerInfo()
        vInfo = reusable.getPersonalVehiclesInfo(result)
        if playerInfo.clanAbbrev:
            clanTag = makeHtmlString('html_templates:eventResult', 'clanTag', ctx={'clanTag': playerInfo.clanAbbrev})
        else:
            clanTag = ''
        resultStrings = R.strings.event.resultScreen
        if vInfo.deathReason != DEATH_REASON_ALIVE:
            botInfo = reusable.getPlayerInfoByVehicleID(vInfo.killerID)
            if botInfo and botInfo.team != playerInfo.team:
                botName = backport.text(R.strings.event.bot_name.dyn(botInfo.realName)())
                status = backport.text(resultStrings.killedBy(), killerName=makeHtmlString('html_templates:eventResult', 'killerName', ctx={'text': botName}))
            else:
                status = backport.text(resultStrings.dead())
        else:
            status = backport.text(resultStrings.alive())
        ctx = {'name': playerInfo.realName,
         'clanTag': clanTag,
         'tank': toUpper(vInfo.vehicle.shortUserName),
         'status': status}
        return {'normal': makeHtmlString('html_templates:eventResult', 'tankStatus', ctx=ctx),
         'min': makeHtmlString('html_templates:eventResult', 'tankStatusMin', ctx=ctx)}


class GameStatusItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        commonInfo = reusable.common
        ctx = {'battleName': backport.text(R.strings.event.resultScreen.battleType()),
         'mapName': toUpper(makeString(commonInfo.arenaType.getName())),
         'date': backport.getShortDateFormat(commonInfo.arenaCreateTime),
         'time': backport.getShortTimeFormat(commonInfo.arenaCreateTime)}
        return {'normal': makeHtmlString('html_templates:eventResult', 'battleStatus', ctx=ctx),
         'min': makeHtmlString('html_templates:eventResult', 'battleStatusMin', ctx=ctx)}


class DamageItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageDealt


class KillsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.kills


class PointsItem(base.StatsItem):
    __slots__ = ()
    _IMAGE = 'certificateX{}_{}_1'
    gameEventController = dependency.descriptor(IGameEventController)

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        generalID = info.generalID
        secretEventAcc = R.images.gui.maps.icons.secretEvent
        iconAcc = secretEventAcc.certificate.c_96x96
        commander = self.gameEventController.getCommander(generalID)
        isBonus = bool(info.energyToken)
        energyID = info.energyToken if isBonus else commander.getQuestEnergyID()
        energy = commander.getEnergy(energyID)
        modifier = energy.modifier if energy else 1
        pointsWithBonus = info.generalPoints if isBonus else info.generalPoints * modifier
        if not isBonus:
            withoutBonusIcon = makeImageTag(backport.image(secretEventAcc.battleResult.certificate()), width=28, height=18, vSpace=-5)
            pointsText = '+{}'.format(pointsWithBonus) if pointsWithBonus > 0 else '0'
            withoutBonusPoints = makeHtmlString('html_templates:eventResult', 'withoutBonusPoints', ctx={'points': pointsText})
            withoutBonusPointsMin = makeHtmlString('html_templates:eventResult', 'withoutBonusPointsMin', ctx={'points': pointsText})
            withoutBonusID = R.strings.event.resultScreen.points.withoutBonus()
            bonusText = makeHtmlString('html_templates:eventResult', 'withoutBonus', ctx={'text': backport.text(withoutBonusID, icon=withoutBonusIcon, points=withoutBonusPoints)})
            bonusTextMin = makeHtmlString('html_templates:eventResult', 'withoutBonusMin', ctx={'text': backport.text(withoutBonusID, icon=withoutBonusIcon, points=withoutBonusPointsMin)})
        else:
            bonusText = ''
            bonusTextMin = ''
        return {'points': info.generalPoints,
         'withoutBonus': int(info.generalPoints / modifier),
         'isBonus': isBonus,
         'bonusIcon': backport.image(iconAcc.dyn(self._IMAGE.format(modifier, generalID))()),
         'bonusText': bonusText,
         'bonusTextMin': bonusTextMin,
         'bonusTooltip': {'specialArgs': [energyID, pointsWithBonus, isBonus],
                          'specialAlias': TOOLTIPS_CONSTANTS.EVENT_BONUSES_POST_BATTLE_INFO,
                          'isSpecial': True}}


def makeSimpleTooltip(header, body):
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


class KillTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return {'specialArgs': [],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_RESULT_KILL,
         'isSpecial': True}


class AssistTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        damageAssistedTrack = info.damageAssistedTrack
        damageAssistedRadio = info.damageAssistedRadio
        damageAssisted = damageAssistedTrack + damageAssistedRadio
        if damageAssisted > 0:
            values = [backport.getIntegralFormat(damageAssistedRadio), backport.getIntegralFormat(damageAssistedTrack), backport.getIntegralFormat(damageAssisted)]
            assistAcc = R.strings.battle_results.common.tooltip.assist
            tooltipStyle = style.getTooltipParamsStyle()
            descriptions = [backport.text(assistAcc.part1(), vals=tooltipStyle), backport.text(assistAcc.part2(), vals=tooltipStyle), backport.text(assistAcc.total(), vals=tooltipStyle)]
        else:
            values = None
            descriptions = None
        return {'specialArgs': [values, descriptions],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_RESULT_ASSIST,
         'isSpecial': True}


class ArmorTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        noDamage = info.noDamageDirectHitsReceived
        damageBlocked = info.damageBlockedByArmor
        if noDamage > 0 or damageBlocked > 0:
            ricochets = info.rickochetsReceived
            values = [backport.getIntegralFormat(ricochets), backport.getIntegralFormat(noDamage), backport.getIntegralFormat(damageBlocked)]
            armorAcc = R.strings.battle_results.common.tooltip.armor
            descriptions = [backport.text(armorAcc.part1()), backport.text(armorAcc.part2()), backport.text(armorAcc.part3(), vals=style.getTooltipParamsStyle())]
        else:
            values = None
            descriptions = None
        return {'specialArgs': [values, descriptions],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_RESULT_ARMOR,
         'isSpecial': True}


class DamageTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        damageDealt = info.damageDealt
        if damageDealt > 0:
            piercings = info.piercings
            values = [backport.getIntegralFormat(damageDealt), backport.getIntegralFormat(piercings)]
            armorAcc = R.strings.battle_results.common.tooltip.damage
            descriptions = [backport.text(armorAcc.part1(), vals=style.getTooltipParamsStyle()), backport.text(armorAcc.part2())]
        else:
            values = None
            descriptions = None
        return {'specialArgs': [values, descriptions],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_RESULT_DAMAGE,
         'isSpecial': True}


class AlliesKillTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.kills.header()), body=backport.text(R.strings.event.resultScreen.tooltip.kills.descr()))


class AlliesAssistTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.assist.header()), body=backport.text(R.strings.event.resultScreen.tooltip.assist.descr()))


class AlliesArmorTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.armor.header()), body=backport.text(R.strings.event.resultScreen.tooltip.armor.descr()))


class AlliesVehiclesTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.vehicles.header()), body=backport.text(R.strings.event.resultScreen.tooltip.vehicles.descr()))


class AlliesDamageTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltip.damage.header()), body=backport.text(R.strings.event.resultScreen.tooltip.damage.descr()))


class Objectives(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        eventGoals = info.eventGoals
        completed = 0
        for _, finished in eventGoals:
            if finished:
                completed += 1

        return {'total': len(eventGoals),
         'completed': completed,
         'specialArgs': [],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_RESULT_MISSION,
         'isSpecial': True}


class EventVehicleStatsBlock(vehicles.RegularVehicleStatsBlock):
    __slots__ = ('tankType', 'generalLevel', 'assist', 'armor')

    def __init__(self, meta=None, field='', *path):
        super(EventVehicleStatsBlock, self).__init__(meta, field, *path)
        self.tankType = None
        self.generalLevel = 0
        self.assist = 0
        self.armor = 0
        return

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        self.assist = result.damageAssisted
        self.armor = result.damageBlockedByArmor
        self.generalLevel = result.generalLevel

    def _setVehicleInfo(self, vehicle):
        super(EventVehicleStatsBlock, self)._setVehicleInfo(vehicle)
        self.tankType = vehicle.type


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
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: PersonalFirstTeamItemSortKey(info, 'generalPoints'))
        super(EventBattlesTeamStatsBlock, self).setRecord(allies, reusable)


class AssistItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageAssisted


class ArmorItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.damageBlockedByArmor


class _MissionsItem(base.StatsItem):
    __slots__ = ()
    gameEventController = dependency.descriptor(IGameEventController)

    def _getMissionInfo(self, progress, level, pointsEarned, pointsPrev, levelReached):
        if not progress:
            return {}
        items = progress.getItems()
        if level >= len(items):
            return {}
        maxLevel = progress.getMaxLevel()
        nextLevel = level if levelReached or level == maxLevel else level + 1
        nextItem = items[nextLevel]
        maxProgress = nextItem.getMaxProgress()
        isAlreadyCompleted = maxLevel == level and not levelReached
        if not isAlreadyCompleted:
            progressCurrent = pointsPrev
            progressNewCurrent = min(pointsPrev + pointsEarned, maxProgress)
        else:
            progressNewCurrent = progressCurrent = maxProgress
        return {'progressTotal': maxProgress,
         'progressCurrent': progressCurrent,
         'progressNewCurrent': progressNewCurrent,
         'progressDelta': 0 if isAlreadyCompleted else pointsEarned,
         'progress': float(progressCurrent) / maxProgress * _HUNDRED_PERCENT if maxProgress != 0 else 0,
         'rewards': self._getRewards(nextItem, nextLevel, progress),
         'tank': self._getTank(progress, nextLevel)}

    def _getRewards(self, nextItem, level, progress):
        return None

    def _getTank(self, progress, level):
        return None


class CrewMissionItem(_MissionsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        generalID = info.generalID
        progress = self.gameEventController.getCommander(generalID)
        missionInfo = self._getMissionInfo(progress, info.generalLevel, info.generalPoints, info.generalPointsPrev, info.gereralLevelReached)
        level = info.generalLevel + 1
        iconLevel = backport.image(R.images.gui.maps.icons.secretEvent.battleResult.dyn('unitLevel{0}'.format(level))())
        iconCrew = backport.image(R.images.gui.maps.icons.secretEvent.generalIcons.c_100x100.dyn('g_icon{0}'.format(generalID))())
        missionInfo.update({'header': backport.text(R.strings.event.unit.name.num(generalID)()),
         'description': backport.text(R.strings.event.resultScreen.generalMissionEarned()),
         'progressLabel': backport.text(R.strings.event.resultScreen.missions.progressCrew()),
         'completeLabel': backport.text(R.strings.event.awardScreen.general.header(), level=int2roman(level)),
         'iconLevel': iconLevel,
         'iconCrew': iconCrew,
         'isCrew': True,
         'isWulfTooltip': True,
         'tooltipData': {'specialArgs': [TOOLTIPS_CONSTANTS.EVENT_RESULT_GENERAL, generalID]}})
        return missionInfo

    def _getRewards(self, nextItem, level, progress):
        allAbilities = progress.getAbilitiesByLevel(level)
        imagesAcc = R.images.gui.maps.icons.secretEvent.abilities.c_48x48
        return [ {'icon': backport.image(imagesAcc.dyn(itemsVehicles.g_cache.equipments()[abilityID].iconName)()),
         'specialArgs': [abilityID],
         'specialAlias': TOOLTIPS_CONSTANTS.COMMANDER_ABILITY_INFO,
         'isSpecial': True} for abilityID in allAbilities ]

    def _getTank(self, progress, level):
        typeCompDescr = first(progress.getVehiclesByLevel(level))
        vehicle = progress.getVehicle(typeCompDescr)
        return {'icon': vehicle.icon,
         'specialArgs': [typeCompDescr],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_VEHICLE,
         'isSpecial': True}


class PersonalMissionItem(_MissionsItem, RewardListMixin):
    __slots__ = ()

    def _convert(self, result, reusable):
        gameEventController = self.gameEventController
        info = reusable.getPersonalVehiclesInfo(result)
        generalID = info.generalID
        general = gameEventController.getCommander(generalID)
        if not general:
            return {}
        front = gameEventController.getFront(general.getFrontID())
        missionInfo = self._getMissionInfo(front, info.frontLevel, info.frontPoints, info.frontPointsPrev, info.frontLevelReached)
        level = info.frontLevel if info.frontLevel == front.getMaxLevel() or info.frontLevelReached else info.frontLevel + 1
        missionInfo.update({'header': backport.text(R.strings.event.resultScreen.frontMissionHeader(), level=int2roman(level)),
         'description': backport.text(R.strings.event.resultScreen.frontMissionEarned()),
         'progressLabel': backport.text(R.strings.event.resultScreen.missions.progress()),
         'completeLabel': backport.text(R.strings.event.resultScreen.missions.completed()),
         'tooltipData': {'specialArgs': [False],
                         'specialAlias': TOOLTIPS_CONSTANTS.SECRET_EVENT_PROGRESSION_INFO,
                         'isSpecial': True}})
        return missionInfo

    def _getRewards(self, nextItem, level, progress):
        return [ {'icon': getAbsoluteUrl(reward['imgSource']),
         'highlightType': reward['highlightType'],
         'overlayType': reward['overlayType'],
         'value': reward['label'],
         'tooltip': reward['tooltip'],
         'specialArgs': reward['specialArgs'],
         'specialAlias': reward['specialAlias'],
         'isSpecial': reward['isSpecial']} for reward in self.getRewards(nextItem, iconSizes=(AWARDS_SIZES.SMALL, AWARDS_SIZES.BIG)) ]
