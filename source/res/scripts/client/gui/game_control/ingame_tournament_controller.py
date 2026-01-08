# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/ingame_tournament_controller.py
import logging
import typing
from adisp import adisp_process
from gui.shared.event_dispatcher import showOfferGiftsWindow
from shared_utils import findFirst, first
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, INGAME_TOURNAMENT_SECTION, INGAME_TOURNAMENT_WCI_INTRO_SEEN, INGAME_TOURNAMENT_OLS_INTRO_SEEN
from constants import CURRENT_REALM
from constants import Configs
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.game_control.links import URLMacros
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import events, g_eventBus
from gui.shop import showIngameShop
from gui.wgcg import IWebController
from gui.wgcg.ingame_tournaments.context import IngameTournamentGetDataCtx
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.ingame_tournament_helper import IngameTournamentState, IngameTournamentMatchState, IngameTournamentUrlType, IngameTournamentLogoSize, IngameTournamentBracketType, IngameTournamentType
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IIngameTournamentController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
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
 ('teamScore2', int),
 ('stageIndex', int)))):

    @classmethod
    def fromParamsDict(cls, params, bracketType, stageIndex):
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
            return cls(round, start, victories, bracketType, teamID1, teamScore1, teamID2, teamScore2, stageIndex)

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
    def fromParamsDict(cls, params, bracketType, stageIndex):
        matches = params.get('matches', [])
        if not matches:
            _logger.warning('Ingame tournament parsing error - matches are missing or empty')
        formattedMatches = []
        for match in matches:
            formattedMatch = _MatchData.fromParamsDict(match, bracketType, stageIndex)
            if formattedMatch is not None:
                formattedMatches.append(formattedMatch)

        formattedMatches.sort(key=lambda formattedMatch: formattedMatch.startTime)
        groupID = params.get('id')
        if not groupID:
            _logger.warning('Ingame tournament parsing error - group id not set')
        return cls(groupID, formattedMatches)


class _StageData(typing.NamedTuple('_StageData', (('groups', list),))):

    @classmethod
    def fromParamsDict(cls, params, stageIndex):
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
            formattedGroups.append(_GroupData.fromParamsDict(group, bracketType, stageIndex))

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
            for i, stage in enumerate(stages):
                formattedStages.append(_StageData.fromParamsDict(stage, i))

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
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        super(IngameTournamentController, self).__init__()
        self.__serverSettings = None
        self.__availabilityByTournamentType = {}
        self.__callbackDelayer = CallbackDelayer()
        self.__eventsManager = em = EventManager()
        self.onTournamentEntryPointUpdated = Event(em)
        self.onTournamentWGCGDataUpdated = Event(em)
        return

    def fini(self):
        self.__serverSettings = None
        self.__availabilityByTournamentType = None
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
        self.__updateTournamentEntryPoint()
        return

    def onAccountBecomeNonPlayer(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onConfigUpdated
        self.__serverSettings = None
        self.__callbackDelayer.clearCallbacks()
        return

    def isTournamentAvailable(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        return config is not None and config.isEnabled

    def getTournamentState(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        if config is None or not config.isEnabled:
            return
        currentTime = getServerUTCTime()
        if currentTime < config.startTime or config.endTime < currentTime:
            return
        elif not self.getIsIntroSeen(tournamentType):
            return IngameTournamentState.INTRO
        elif self.getCurrentShowmatch(tournamentType):
            return IngameTournamentState.IN_PROGRESS
        else:
            return IngameTournamentState.BETWEEN_SHOWMATCHES if self.getNextShowmatch(tournamentType) else IngameTournamentState.FINISHED

    def getCurrentShowmatch(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        if config is None or not config.isEnabled:
            return
        else:
            currentTime = getServerUTCTime()
            return findFirst(lambda showmatch: showmatch.startTime <= currentTime <= showmatch.endTime, config.showmatches)

    def getNextShowmatch(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        if config is None or not config.isEnabled:
            return
        else:
            currentTime = getServerUTCTime()
            upcomingShowmatches = [ showmatch for showmatch in config.showmatches if currentTime < showmatch.startTime ]
            upcomingShowmatches.sort(key=lambda showmatch: showmatch.startTime)
            return first(upcomingShowmatches)

    def getTournamentShowmatchPeriod(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        if config is None or not config.isEnabled:
            return (None, None)
        else:
            start = min([ showmatch.startTime for showmatch in config.showmatches ])
            end = max([ showmatch.endTime for showmatch in config.showmatches ])
            return (start, end)

    def getIsIntroSeen(self, tournamentType):
        settings = AccountSettings.getUIFlag(INGAME_TOURNAMENT_SECTION)
        if tournamentType == IngameTournamentType.WCI:
            return settings.get(INGAME_TOURNAMENT_WCI_INTRO_SEEN, False)
        return settings.get(INGAME_TOURNAMENT_OLS_INTRO_SEEN, False) if tournamentType == IngameTournamentType.OLS else False

    def setIsIntroSeen(self, tournamentType):
        settings = AccountSettings.getUIFlag(INGAME_TOURNAMENT_SECTION)
        if tournamentType == IngameTournamentType.WCI:
            settings[INGAME_TOURNAMENT_WCI_INTRO_SEEN] = True
        if tournamentType == IngameTournamentType.OLS:
            settings[INGAME_TOURNAMENT_OLS_INTRO_SEEN] = True
        AccountSettings.setUIFlag(INGAME_TOURNAMENT_SECTION, settings)

    @adisp_process
    def requestTournamentWGCGData(self):
        res = yield self.__webCtrl.sendRequest(IngameTournamentGetDataCtx())
        self.onTournamentWGCGDataUpdated(_IngameTournamentData.fromRequestResponse(res))

    def getOfferGiftsToken(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
        return config.offerGiftsToken if config else ''

    def openOfferGifts(self, tournamentType, overrideOnBackCallback=None):
        tokenStoreToken = self.getOfferGiftsToken(tournamentType)
        if not tokenStoreToken:
            _logger.warning('offerGiftsToken is not defined in tournament config')
            return
        else:
            offer = self.__offersProvider.getOfferByToken(tokenStoreToken)
            offerID = offer.id if offer else None
            if not offerID:
                _logger.warning('Could not find offer for token %s', tokenStoreToken)
                return
            showOfferGiftsWindow(offerID=offerID, overrideOnBackCallback=overrideOnBackCallback)
            return

    @adisp_process
    def openShop(self, tournamentType):
        config = self.__getConfigByTournamentType(tournamentType)
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
        self.__updateTournamentEntryPoint()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onConfigUpdated
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onConfigUpdated
        return

    def __onConfigUpdated(self, serverSettingsDiff):
        if Configs.INGAME_TOURNAMENT_CONFIG.value in serverSettingsDiff:
            self.__updateTournamentEntryPoint()

    def __updateTournamentEntryPoint(self):
        self.__callbackDelayer.clearCallbacks()
        nextTimestamp = self.__getNextUpdateTimestamp()
        if nextTimestamp is not None:
            delay = nextTimestamp - getServerUTCTime()
            if delay > 0:
                self.__callbackDelayer.delayCallback(delay, self.__updateTournamentEntryPoint)
        for tournamentType in IngameTournamentType:
            isAvailable = self.isTournamentAvailable(tournamentType)
            if self.__availabilityByTournamentType.get(tournamentType) != isAvailable:
                self.__availabilityByTournamentType[tournamentType] = isAvailable
                self.__eventsService.updateEntries()

        self.onTournamentEntryPointUpdated()
        return

    def __getNextUpdateTimestamp(self):
        timers = []
        for showmatch in (self.getCurrentShowmatch(IngameTournamentType.WCI), self.getCurrentShowmatch(IngameTournamentType.OLS)):
            if showmatch is not None:
                timers.append(showmatch.endTime)

        for showmatch in (self.getNextShowmatch(IngameTournamentType.WCI), self.getNextShowmatch(IngameTournamentType.OLS)):
            if showmatch is not None:
                timers.append(showmatch.startTime)

        return min(timers) if timers else None

    def __getConfig(self):
        return self.__serverSettings.ingameTournamentConfig if self.__serverSettings is not None else None

    def __getConfigByTournamentType(self, tournamentType):
        config = self.__getConfig()
        return getattr(config, tournamentType.value, None) if config is not None else None
