# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/common.py
import BigWorld
from constants import ARENA_GUI_TYPE, FINISH_REASON
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.components import base
from gui.battle_results.components import style
from gui.battle_results.settings import PLAYER_TEAM_RESULT as _TEAM_RESULT, UI_VISIBILITY
from gui.shared.utils import toUpper
from helpers import i18n, dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import WinStatus
_ARENA_TYPE_FORMAT = '#arenas:type/{0}/name'
_ARENA_TYPE_EXT_FORMAT = '#menu:loading/battleTypes/{0}'
_ARENA_FULL_NAME_FORMAT = '#battle_results:common/arena/fullName'
_ARENA_ICON_PATH = '../maps/icons/map/stats/%s.png'

def makeArenaFullName(arenaTypeName, i18nKey):
    arenaFullName = i18n.makeString(_ARENA_FULL_NAME_FORMAT)
    return arenaFullName.format(i18n.makeString(arenaTypeName), i18n.makeString(i18nKey))


def makeRegularFinishResultLabel(finishReason, teamResult):
    return backport.text(R.strings.battle_results.finish.reason.dyn('c_{}{}'.format(finishReason, teamResult))()) if finishReason == FINISH_REASON.EXTERMINATION else backport.text(R.strings.battle_results.finish.reason.dyn('c_{}'.format(finishReason))())


def makeEpicBattleFinishResultLabel(finishReason, teamResult):
    if finishReason is FINISH_REASON.TIMEOUT:
        finishReason = FINISH_REASON.DESTROYED_OBJECTS
        teamResult = _TEAM_RESULT.DEFEAT
    elif finishReason is FINISH_REASON.DESTROYED_OBJECTS:
        teamResult = _TEAM_RESULT.WIN
    return backport.text(R.strings.battle_results.finish.reason.dyn('c_{}{}'.format(finishReason, teamResult))()) if finishReason in {FINISH_REASON.EXTERMINATION, FINISH_REASON.TIMEOUT, FINISH_REASON.DESTROYED_OBJECTS} else backport.text(R.strings.battle_results.finish.reason.dyn('c_{}'.format(finishReason))())


def convertStrToNumber(value):
    return '{:,}'.format(value).replace(',', ' ')


class ArenaShortTimeVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return style.makeTimeStatsVO(self._field, backport.getShortTimeFormat(record))


class ArenaDateTimeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return ' '.join((backport.getShortDateFormat(record), backport.getShortTimeFormat(record)))


class RegularArenaFullNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaGuiType = reusable.common.arenaGuiType
        arenaType = reusable.common.arenaType
        if arenaGuiType in (ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.EPIC_RANDOM):
            i18nKey = _ARENA_TYPE_FORMAT.format(arenaType.getGamePlayName())
        else:
            i18nKey = _ARENA_TYPE_EXT_FORMAT.format(arenaGuiType)
        return makeArenaFullName(arenaType.getName(), i18nKey)


class ArenaIconItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return reusable.common.getArenaIcon(_ARENA_ICON_PATH)


class ArenaDurationItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record:
            converted = backport.text(R.strings.battle_results.details.time.value(), min=int(record / ONE_MINUTE), sec=int(record % ONE_MINUTE))
        else:
            converted = None
        return converted


class ObjectivesReachedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record:
            yes = backport.text(R.strings.battle_results.details.time.val_yes())
            no = backport.text(R.strings.battle_results.details.time.val_no())
            reached = yes if record['commonNumStarted'] > 0 else no
        else:
            reached = ''
        return style.makeTimeStatsVO(self._field, reached)


class ObjectivesDestroyedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record:
            destroyed = str(record['commonNumDestroyed'])
        else:
            destroyed = '0'
        return style.makeTimeStatsVO(self._field, destroyed)


class BasesCapturedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record:
            captured = str(record['commonNumCaptured'])
        else:
            captured = '0'
        return style.makeTimeStatsVO(self._field, captured)


class ArenaDurationVO(ArenaDurationItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return style.makeTimeStatsVO(self._field, super(ArenaDurationVO, self)._convert(record, reusable))


class PlayerKillingTimeVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        info = reusable.personal.getLifeTimeInfo()
        if info.isKilled:
            minutes = int(info.lifeTime / ONE_MINUTE)
            seconds = int(info.lifeTime % ONE_MINUTE)
            converted = backport.text(R.strings.battle_results.details.time.value(), min=minutes, sec=seconds)
        else:
            converted = '-'
        return style.makeTimeStatsVO(self._field, converted)


class FinishResultMeta(base.DictMeta):
    __slots__ = ()

    def __init__(self, finishReasonLabel, shortResultLabel, fullResultLabel):
        meta = {finishReasonLabel: '',
         shortResultLabel: '',
         fullResultLabel: ''}
        auto = ((0, base.StatsItem(finishReasonLabel, 'finishReasonLabel')), (1, base.StatsItem(shortResultLabel, 'shortResultLabel')), (2, base.StatsItem(fullResultLabel, 'fullResultLabel')))
        super(FinishResultMeta, self).__init__(meta, auto)


class RegularFinishResultBlock(base.StatsBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')

    def __init__(self, meta=None, field='', *path):
        super(RegularFinishResultBlock, self).__init__(meta, field, *path)
        self.finishReasonLabel = None
        self.shortResultLabel = None
        self.fullResultLabel = None
        return

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        self.finishReasonLabel = self._getFinishReasonLabel(reusable, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(teamResult)()))

    @classmethod
    def _getFinishReasonLabel(cls, reusable, teamResult):
        return makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)


class StrongholdBattleFinishResultBlock(RegularFinishResultBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        team = reusable.getPersonalTeam()
        winnerIfDraw = reusable.personal.avatar.winnerIfDraw
        if teamResult == _TEAM_RESULT.DRAW and winnerIfDraw:
            if team == winnerIfDraw:
                teamResult = _TEAM_RESULT.WIN
                winStatus = WinStatus.WIN
            else:
                teamResult = _TEAM_RESULT.DEFEAT
                winStatus = WinStatus.LOSE
            sessionCtx = self.sessionProvider.getCtx()
            if sessionCtx.extractLastArenaWinStatus() is not None:
                sessionCtx.setLastArenaWinStatus(WinStatus(winStatus))
        self.finishReasonLabel = makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(teamResult)()))
        return


class EpicBattleBattleFinishResultBlock(RegularFinishResultBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        team = reusable.getPersonalTeam()
        winnerIfDraw = reusable.personal.avatar.winnerIfDraw
        if teamResult == _TEAM_RESULT.DRAW and winnerIfDraw:
            if team == winnerIfDraw:
                teamResult = _TEAM_RESULT.WIN
                winStatus = WinStatus.WIN
            else:
                teamResult = _TEAM_RESULT.DEFEAT
                winStatus = WinStatus.LOSE
            sessionCtx = self.sessionProvider.getCtx()
            if sessionCtx.extractLastArenaWinStatus() is not None:
                sessionCtx.setLastArenaWinStatus(WinStatus(winStatus))
        self.finishReasonLabel = makeEpicBattleFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(teamResult)()))
        return


class AllyTeamClanTitle(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return '{} [{}]'.format(backport.text(R.strings.battle_results.team.stats.ownTeam()), reusable.players.getFirstAllyClan(reusable.getPersonalTeam()).clanAbbrev)


class EnemyTeamClanTitle(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return '{} [{}]'.format(backport.text(R.strings.battle_results.team.stats.enemyTeam()), reusable.players.getFirstEnemyClan(reusable.getPersonalTeam()).clanAbbrev)


class ClanInfoBlock(base.StatsBlock):
    __slots__ = ('clanDBID', 'clanAbbrev')

    def __init__(self, meta=None, field='', *path):
        super(ClanInfoBlock, self).__init__(meta, field, *path)
        self.clanDBID = None
        self.clanAbbrev = None
        return

    def setRecord(self, record, reusable):
        if record is not None:
            self.clanDBID = record.clanDBID
            self.clanAbbrev = '[{}]'.format(record.clanAbbrev)
        return


class ClansInfoBlock(base.StatsBlock):
    __slots__ = ('allies', 'enemies')

    def __init__(self, meta=None, field='', *path):
        super(ClansInfoBlock, self).__init__(meta, field, *path)
        self.allies = None
        self.enemies = None
        return

    def setRecord(self, record, reusable):
        team = reusable.getPersonalTeam()
        players = reusable.players
        self.allies = players.getFirstAllyClan(team)
        self.enemies = players.getFirstEnemyClan(team)


class TeamsUiVisibility(base.StatsItem):

    def _convert(self, value, reusable):
        ui_visibility = 0
        if reusable.isSquadSupported:
            ui_visibility |= UI_VISIBILITY.SHOW_SQUAD
        return ui_visibility


class EligibleForCrystalRewards(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.personal.avatar.eligibleForCrystalRewards


class SortieTeamsUiVisibility(TeamsUiVisibility):

    def _convert(self, value, reusable):
        ui_visibility = super(SortieTeamsUiVisibility, self)._convert(value, reusable)
        ui_visibility |= UI_VISIBILITY.SHOW_RESOURCES
        return ui_visibility


class SpaFlagItem(base.StatsItem):
    __slots__ = ('_spaFlag',)

    def __init__(self, field, spaFlag):
        super(SpaFlagItem, self).__init__(field)
        self._spaFlag = spaFlag

    def clone(self):
        return self.__class__(self._field, self._spaFlag)

    def _convert(self, value, reusable):
        return BigWorld.player().spaFlags.getFlag(self._spaFlag)
