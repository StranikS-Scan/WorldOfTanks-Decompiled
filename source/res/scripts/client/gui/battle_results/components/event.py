# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/event.py
from constants import EVENT_MISSION_ICON_SIZES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import dependency
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from skeletons.gui.afk_controller import IAFKController
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.conditions import getProgressFromQuestWithSingleAccumulative
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
from gui.shared.money import Currency
from helpers.i18n import makeString as _ms
from gui.shared.utils.functions import makeTooltip
_MAX_PROGRESS_BAR_VALUE = 100

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


class MissionsItem(base.StatsItem):
    __slots__ = ()
    gameEventController = dependency.descriptor(IGameEventController)

    def _convert(self, result, reusable):
        gameEventController = self.gameEventController
        missions = gameEventController.getMissionsController()
        questsProgress = reusable.personal.getQuestsProgress()
        items = []
        for mission in missions.getMissions().itervalues():
            itemInQuestsProgress = False
            item = None
            for item in mission.getItems():
                if item.isCompleted() and item.getQuestID() in questsProgress:
                    itemInQuestsProgress = True
                    break

            if item and itemInQuestsProgress:
                items.append(item)
            items.append(mission.getSelectedItem())

        itemsInProgress = [ item for item in items if not item.isCompleted() or item.getQuestID() in questsProgress ]
        vo = []
        vehicle = reusable.getPersonalVehiclesInfo(result).vehicle
        commander = gameEventController.getCommander(vehicle.intCD)
        if not commander:
            return vo
        else:
            info = reusable.getPersonalVehiclesInfo(result)
            commanderSettings = gameEventController.getVehicleSettings()
            item = commander.getNextProgressItem()
            if item is None:
                item = commander.getMaxProgressItem()
            bonuses = [ self._getBonusVO(bonus) for bonus in getEventAwardFormatter().format(item.getBonuses()) ]
            rewards = [ {'icon': bonus['icon'],
             'value': bonus['label'] if not info.commanderLevelReached else str(info.commanderTokenDelta),
             'tooltip': bonus['tooltip'],
             'specialArgs': bonus['specialArgs'],
             'specialAlias': bonus['specialAlias'],
             'isSpecial': bonus['isSpecial']} for bonus in bonuses ]
            progressPrevCurrent = 0
            progressDelta = 0
            progress = _MAX_PROGRESS_BAR_VALUE
            status = _ms(backport.text(R.strings.event.resultScreen.questCompleted()))
            commanderLevel = info.commanderCurrentLevel
            commanderQuestBonusCount = info.commanderQuestBonusCount
            currentProgress = commander.getProgressForLevel(commanderLevel, commanderQuestBonusCount)
            currentProgress += info.commanderTokenCount
            if commanderLevel < commander.getMaxLevel():
                if commanderLevel == 0:
                    commanderQuestBonusCount += 1
                totalProgress = commander.getProgressForLevel(commanderLevel + 1, commanderQuestBonusCount)
            else:
                totalProgress = commander.getProgressForLevel(commanderLevel, commanderQuestBonusCount + 1)
            if currentProgress >= totalProgress or info.commanderLevelReached:
                showComplete = True
                totalProgress = None
                currentProgress = None
            else:
                showComplete = False
                progress = 0
                progressDelta = info.commanderPoints
                progressPrevCurrent = currentProgress - progressDelta
                if currentProgress > 0:
                    progress = int(currentProgress / float(totalProgress) * _MAX_PROGRESS_BAR_VALUE)
            vo.append({'header': _ms(backport.text(R.strings.event.resultScreen.collectMoreMatter())),
             'progressTotal': totalProgress,
             'progressCurrent': progressPrevCurrent if progressPrevCurrent > 0 else 0,
             'progressNewCurrent': currentProgress,
             'progressDelta': '+ ' + str(progressDelta) if progressDelta else '',
             'progress': progress,
             'showComplete': showComplete,
             'status': status,
             'icon': commanderSettings.getTankManBattleResultIcon(vehicle.intCD),
             'rewards': rewards,
             'isCommander': True,
             'showBonus': bool(info.boosterApplied),
             'showProgress': not showComplete})
            for item in itemsInProgress:
                bonuses = getEventAwardFormatter().format(item.getBonuses())
                rewards = [ {'icon': bonus.getImage(AWARDS_SIZES.BIG),
                 'value': bonus.label,
                 'isMoney': bonus.bonusName in Currency.ALL,
                 'tooltip': bonus.tooltip,
                 'specialArgs': bonus.specialArgs,
                 'specialAlias': bonus.specialAlias,
                 'isSpecial': bonus.isSpecial} for bonus in bonuses ]
                currentProgress, totalProgress = getProgressFromQuestWithSingleAccumulative(item.getQuest())
                progress = 0
                if item.isCompleted():
                    progress = _MAX_PROGRESS_BAR_VALUE
                elif currentProgress > 0:
                    progress = int(currentProgress / float(totalProgress) * _MAX_PROGRESS_BAR_VALUE)
                status = R.strings.event.resultScreen.questNotCompleted()
                if item.isCompleted():
                    status = R.strings.event.resultScreen.questCompleted()
                showComplete = False
                if totalProgress is None or item.isCompleted():
                    showComplete = True
                vo.append({'header': item.getDescr(),
                 'progressTotal': totalProgress,
                 'progressCurrent': currentProgress,
                 'progressNewCurrent': currentProgress,
                 'progressDelta': '',
                 'status': _ms(backport.text(status)),
                 'progress': progress,
                 'showComplete': showComplete,
                 'icon': missions.getMissionByID(item.getMissionID()).getIcon(EVENT_MISSION_ICON_SIZES.BIG),
                 'rewards': rewards,
                 'showProgress': totalProgress is not None})

            return vo

    def _getBonusVO(self, bonus):
        return {'icon': bonus.getImage(AWARDS_SIZES.BIG),
         'tooltip': bonus.tooltip,
         'specialArgs': bonus.specialArgs,
         'specialAlias': bonus.specialAlias,
         'isSpecial': bonus.isSpecial,
         'label': bonus.label}


class EventPointsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.eventPoints - info.eventPointsLeft


class EventPointsLeftItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.eventPointsLeft


class KillsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.kills


def makeSimpleTooltip(header, body):
    return {'tooltip': makeTooltip(header=header, body=body),
     'isSpecial': False,
     'specialArgs': []}


class MatterTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltips.matterHeader()), body=backport.text(R.strings.event.resultScreen.tooltips.matter()))


class MatterOnTankTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltips.matterOnTankHeader()), body=backport.text(R.strings.event.resultScreen.tooltips.matterOnTank()))


class KillTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.battle_results.common.tooltip.kill.header()), body=backport.text(R.strings.battle_results.common.tooltip.kill_1.description()))


class DamageTooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return makeSimpleTooltip(header=backport.text(R.strings.battle_results.common.tooltip.damage.header()), body=backport.text(R.strings.battle_results.common.tooltip.damage.description()))


class EventRewardStatsBlock(base.StatsBlock):
    __slots__ = ('exp', 'credits', 'freeXP', 'expTooltip', 'creditsTooltip', 'freeXPTooltip')

    def __init__(self, meta=None, field='', *path):
        super(EventRewardStatsBlock, self).__init__(meta, field, *path)
        self.exp = 0
        self.credits = 0
        self.freeXP = 0
        self.expTooltip = makeSimpleTooltip(header=backport.text(R.strings.event.resultScreen.tooltips.expHeader()), body=backport.text(R.strings.event.resultScreen.tooltips.exp()))
        self.creditsTooltip = makeSimpleTooltip(header=backport.text(R.strings.tooltips.credits.header()), body=backport.text(R.strings.tooltips.credits.body()))
        self.freeXPTooltip = makeSimpleTooltip(header=backport.text(R.strings.tooltips.freeXP.header()), body=backport.text(R.strings.tooltips.advanced.economyConvertExp()))

    def setRecord(self, result, reusable):
        self.exp = reusable.personal.getBaseXPRecords().getRecord('xp')
        self.credits = reusable.personal.getBaseCreditsRecords().getRecord('credits')
        self.freeXP = reusable.personal.getBaseFreeXPRecords().getRecord('freeXP')


class EventVehicleStatsBlock(vehicles.RegularVehicleStatsBlock):
    afkController = dependency.descriptor(IAFKController)
    __slots__ = ('matter', 'matterOnTank', 'tankType', 'banStatus', 'banStatusTooltip')
    _NO_BAN = 'ok'
    _BANNED = 'ban'
    _WARNED = 'warning'

    def __init__(self, meta=None, field='', *path):
        super(EventVehicleStatsBlock, self).__init__(meta, field, *path)
        self.matter = 0
        self.matterOnTank = 0
        self.banStatus = self._NO_BAN
        self.banStatusTooltip = ''

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        self.matter = result.eventPoints - result.eventPointsLeft
        self.matterOnTank = result.eventPointsLeft
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
