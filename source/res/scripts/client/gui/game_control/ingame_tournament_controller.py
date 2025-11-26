# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ingame_tournament_controller.py
import logging
import typing
from adisp import adisp_process
from shared_utils import findFirst, first
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from constants import CURRENT_REALM
from constants import Configs
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.game_control.links import URLMacros
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared import events, g_eventBus
from gui.shop import showIngameShop
from gui.wgcg import IWebController
from gui.wgcg.ingame_tournaments.context import IngameTournamentGetDataCtx
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.ingame_tournament_helper import IngameTournamentState, IngameTournamentMatchState, IngameTournamentUrlType, IngameTournamentLogoSize, IngameTournamentBracketType
from helpers.time_utils import getCurrentLocalServerTimestamp, getServerUTCTime
from skeletons.gui.game_control import IIngameTournamentController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class _TeamData(typing.NamedTuple('_TeamData', (('teamID', int), ('name', str), ('logoURLs', dict)))):

    @classmethod
    def fromParamsDict(cls, params):
        teamID = params.get('id', 0)
        name = params.get('name', '')
        logoURLs = {}
        for sizeStr, url in params.get('logo_urls', {}).iteritems():
            logoSize = cls.__getLogoSizeByStr(sizeStr)
            if logoSize:
                logoURLs[logoSize] = url

        if not teamID or not name or not logoURLs:
            _logger.warning('Ingame tournament parsing error - team data error')
        return cls(teamID, name, logoURLs)

    @staticmethod
    def __getLogoSizeByStr(logoSizeStr):
        logoSizeStr = logoSizeStr.replace('\xc3\x97', 'x')
        return findFirst(lambda logo: logo.value == logoSizeStr, IngameTournamentLogoSize)


class _MatchData(typing.NamedTuple('_MatchData', (('round', int),
 ('startTime', int),
 ('victories', int),
 ('bracketType', IngameTournamentBracketType),
 ('teamID1', int),
 ('teamScore1', int),
 ('teamID2', int),
 ('teamScore2', int)))):

    @classmethod
    def fromParamsDict(cls, params, bracketType):
        round = params.get('round')
        start = params.get('start_at')
        victories = params.get('victories')
        if round is None or start is None or victories is None:
            _logger.info('Ingame tournament parsing error - match params must be set to valid values')
            return
        else:
            team1 = params.get('team_1') or {}
            teamID1 = team1.get('id')
            teamScore1 = team1.get('score')
            team2 = params.get('team_2') or {}
            teamID2 = team2.get('id')
            teamScore2 = team2.get('score')
            return cls(round, start, victories, bracketType, teamID1, teamScore1, teamID2, teamScore2)

    @property
    def state(self):
        currentTime = getServerUTCTime()
        if currentTime < self.startTime:
            return IngameTournamentMatchState.UPCOMING
        else:
            return IngameTournamentMatchState.COMPLETED if self.teamScore1 is not None and self.teamScore2 is not None else IngameTournamentMatchState.IN_LIVE

    @property
    def bestOf(self):
        return self.victories * 2 - 1


class _GroupData(typing.NamedTuple('_GroupData', (('groupID', int), ('matches', list)))):

    @classmethod
    def fromParamsDict(cls, params, bracketType):
        matches = params.get('matches', [])
        if not matches:
            _logger.warning('Ingame tournament parsing error - matches are missing or empty')
        formattedMatches = []
        for match in matches:
            formattedMatch = _MatchData.fromParamsDict(match, bracketType)
            if formattedMatch is not None:
                formattedMatches.append(formattedMatch)

        formattedMatches.sort(key=lambda formattedMatch: formattedMatch.startTime)
        groupID = params.get('id')
        if not groupID:
            _logger.warning('Ingame tournament parsing error - group id not set')
        return cls(groupID, formattedMatches)


class _StageData(typing.NamedTuple('_StageData', (('groups', list),))):

    @classmethod
    def fromParamsDict(cls, params):
        groups = params.get('groups')
        if not groups:
            _logger.warning('Ingame tournament parsing error - groups are missing or empty')
            return cls([])
        bracketTypeStr = params.get('bracket_type')
        bracketType = findFirst(lambda bracket: bracket.value == bracketTypeStr, IngameTournamentBracketType)
        if not bracketType:
            _logger.warning('Ingame tournament parsing error - bracket_type is missing or incorrect')
        formattedGroups = []
        for group in groups:
            formattedGroups.append(_GroupData.fromParamsDict(group, bracketType))

        return cls(formattedGroups)


class _RewardData(typing.NamedTuple('_RewardData', (('fromPosition', int), ('toPosition', int), ('amount', int)))):

    @classmethod
    def fromParamsDict(cls, params):
        fromPosition = params.get('from_position')
        toPosition = params.get('to_position')
        if fromPosition is None or toPosition is None:
            _logger.warning('Ingame tournament parsing error - reward positions not set')
        amount = params.get('prize_count', 0)
        if amount == 0:
            _logger.warning('Ingame tournament parsing error - prize_count is not set')
        return cls(fromPosition, toPosition, amount)


class _LeaderboardData(typing.NamedTuple('_LeaderboardData', (('fromPosition', int), ('toPosition', int), ('teamIDs', list)))):

    @classmethod
    def fromParamsData(cls, paramsData):
        position = first(paramsData).get('position')
        teams = [ data.get('team_id') for data in paramsData ]
        if not position or not teams:
            _logger.warning('Ingame tournament parsing error - wrong leaderboard position params')
        return cls(position - len(teams) + 1, position, teams)


class _IngameTournamentData(typing.NamedTuple('_IngameTournamentData', (('stages', list),
 ('rewards', list),
 ('streamURLs', dict),
 ('teams', dict),
 ('leaderboard', list)))):

    @classmethod
    def fromRequestResponse(cls, wgcgResponse):
        if not wgcgResponse or not wgcgResponse.isSuccess():
            _logger.warning('Ingame tournament parsing error - WGCG response is in error state')
            return None
        else:
            data = wgcgResponse.data or {}
            stages = data.get('stages', [])
            if not stages:
                _logger.warning('Ingame tournament parsing error - stages section are missing or empty')
            formattedStages = []
            for stage in stages:
                formattedStages.append(_StageData.fromParamsDict(stage))

            rewards = data.get('rewards', [])
            if not rewards:
                _logger.warning('Ingame tournament parsing error - rewards section are missing or empty')
            formattedRewards = []
            for reward in rewards:
                formattedRewards.append(_RewardData.fromParamsDict(reward))

            streamURLs = data.get('stream_urls', [])
            if not streamURLs:
                _logger.warning('Ingame tournament parsing error - stream_urls section are missing or empty')
            formattedURLs = {}
            for streamURL in streamURLs:
                urlType, url = cls.__getStreamUrlData(streamURL)
                if urlType and url:
                    formattedURLs[urlType] = url

            teams = data.get('teams', [])
            if not teams:
                _logger.warning('Ingame tournament parsing error - teams section are missing or empty')
            formattedTeams = {}
            for team in teams:
                formattedTeam = _TeamData.fromParamsDict(team)
                formattedTeams[formattedTeam.teamID] = formattedTeam

            leaderboard = data.get('positions', [])
            leaderboardByPositionData = {}
            for paramsSection in leaderboard:
                leaderboardByPositionData.setdefault(paramsSection.get('position'), []).append(paramsSection)

            formattedLeaderboard = []
            for positionData in leaderboardByPositionData.itervalues():
                formattedLeaderboard.append(_LeaderboardData.fromParamsData(positionData))

            formattedLeaderboard.sort(key=lambda leaderboardPosition: leaderboardPosition.fromPosition)
            return cls(formattedStages, formattedRewards, formattedURLs, formattedTeams, formattedLeaderboard)

    def getLiveMatch(self):
        for stage in self.stages:
            for group in stage.groups:
                liveMatch = findFirst(lambda match: match.state == IngameTournamentMatchState.IN_LIVE, group.matches)
                if liveMatch is not None:
                    return liveMatch

        return

    def getUpcomingMatches(self):
        matches = []
        for stage in self.stages:
            for group in stage.groups:
                matches.extend([ match for match in group.matches if match.state == IngameTournamentMatchState.UPCOMING ])

        matches.sort(key=lambda match: match.startTime)
        return matches

    def getAllMatches(self):
        matches = []
        for stage in self.stages:
            for group in stage.groups:
                matches.extend(group.matches)

        matches.sort(key=lambda match: match.startTime)
        return matches

    def getTotalRewardAmount(self):
        return sum([ reward.amount for reward in self.rewards ])

    def getLeaderboardDataByTeam(self, teamID):
        return findFirst(lambda data: teamID in data.teamIDs, self.leaderboard)

    def getRewardForPosition(self, position):
        return findFirst(lambda reward: reward.fromPosition <= position <= reward.toPosition, self.rewards)

    @classmethod
    def __getStreamUrlData(cls, params):
        url = params.get('url', '')
        urlTypeStr = params.get('type')
        urlType = findFirst(lambda urlType: urlType.value == urlTypeStr, IngameTournamentUrlType)
        if not url or not urlType:
            _logger.warning('Ingame tournament parsing error - stream URL or type must be set to valid value')
            return (None, None)
        else:
            return (urlType, url)


class IngameTournamentController(IIngameTournamentController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __webCtrl = dependency.descriptor(IWebController)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(IngameTournamentController, self).__init__()
        self.__serverSettings = None
        self.__isAvailable = None
        self.__callbackDelayer = CallbackDelayer()
        self.__eventsManager = em = EventManager()
        self.onTournamentBannerUpdated = Event(em)
        self.onTournamentWGCGDataUpdated = Event(em)
        return

    def fini(self):
        self.__serverSettings = None
        self.__isAvailable = None
        self.__callbackDelayer.destroy()
        self.__callbackDelayer = None
        self.__eventsManager.clear()
        self.__eventsManager = None
        return

    def onAccountBecomePlayer(self):
        self.__serverSettings = self.__lobbyContext.getServerSettings()
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange += self.__onConfigUpdated
        if self.prbDispatcher:
            self.startGlobalListening()
        else:
            g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated
        self.__updateTournamentBanner()
        return

    def onAccountBecomeNonPlayer(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onConfigUpdated
        self.__serverSettings = None
        self.stopGlobalListening()
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        self.__callbackDelayer.clearCallbacks()
        return

    def onPrbEntitySwitched(self):
        self.__updateTournamentBanner()

    def isTournamentBannerAvailable(self):
        if not self.__isRandomPrbActive():
            return False
        else:
            config = self.__getConfig()
            return False if config is None or not config.isEnabled else bool(self.getActiveBannerData())

    def getActiveBannerData(self):
        config = self.__getConfig()
        banners = config.banners if config else None
        if not banners:
            return
        else:
            currentTime = getServerUTCTime()
            return findFirst(lambda banner: banner.startTime <= currentTime <= banner.endTime, banners)

    def getTournamentDates(self):
        config = self.__getConfig()
        allBanners = config.banners if config else None
        if not allBanners:
            return (0, 0)
        else:
            inProgressBanners = [ banner for banner in allBanners if banner.state == IngameTournamentState.IN_PROGRESS ]
            if inProgressBanners:
                startDate = min([ banner.startTime for banner in inProgressBanners ])
                endDate = max([ banner.endTime for banner in inProgressBanners ])
                return (startDate, endDate)
            return (0, 0)

    @adisp_process
    def requestTournamentWGCGData(self):
        res = yield self.__webCtrl.sendRequest(IngameTournamentGetDataCtx())
        self.onTournamentWGCGDataUpdated(_IngameTournamentData.fromRequestResponse(res))

    @adisp_process
    def openShop(self):
        config = self.__getConfig()
        shopConfigs = config.shop if config else []
        realmConfig = findFirst(lambda config: CURRENT_REALM in config.realms, shopConfigs)
        if realmConfig is not None:
            if realmConfig.ingameShopRelativePath:
                url = '{}{}'.format(getShopURL(), realmConfig.ingameShopRelativePath)
                showIngameShop(url)
            elif realmConfig.shopUrl:
                parsedUrl = yield URLMacros().parse(realmConfig.shopUrl)
                g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=parsedUrl))
            else:
                _logger.warning('None from ingameShopRelativePath or shorUrl are specified')
        else:
            _logger.warning('Could not open Ingame Tournament shop')
        return

    def __onPrbDispatcherCreated(self):
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        self.startGlobalListening()
        self.__updateTournamentBanner()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onConfigUpdated
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onConfigUpdated
        return

    def __onConfigUpdated(self, serverSettingsDiff):
        if Configs.INGAME_TOURNAMENT_CONFIG.value in serverSettingsDiff:
            self.__updateTournamentBanner()

    def __updateTournamentBanner(self):
        self.__callbackDelayer.clearCallbacks()
        if self.__isRandomPrbActive():
            nextTimestamp = self.__getNextUpdateTimestamp()
            if nextTimestamp is not None:
                delay = nextTimestamp - getServerUTCTime()
                if delay > 0:
                    self.__callbackDelayer.delayCallback(delay, self.__updateTournamentBanner)
        isAvailable = self.isTournamentBannerAvailable()
        if self.__isAvailable != isAvailable:
            self.__isAvailable = isAvailable
            self.__eventsService.updateEntries()
        self.onTournamentBannerUpdated()
        return

    def __getNextUpdateTimestamp(self):
        config = self.__getConfig()
        banners = config.banners if config else None
        if not banners:
            return
        else:
            timers = []
            activeBanner = self.getActiveBannerData()
            if activeBanner is not None:
                timers.append(activeBanner.endTime)
            currentTime = getCurrentLocalServerTimestamp()
            nextTimers = [ banner.startTime for banner in banners if currentTime < banner.startTime ]
            timers.extend(nextTimers)
            return min(timers) if timers else None

    def __getConfig(self):
        return self.__serverSettings.ingameTournamentConfig if self.__serverSettings is not None else None

    def __isRandomPrbActive(self):
        return bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM) if self.prbEntity is not None else False
