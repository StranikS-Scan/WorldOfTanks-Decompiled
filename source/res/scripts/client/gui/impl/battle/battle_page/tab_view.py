# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/tab_view.py
from contextlib import contextmanager
import logging
import typing
import BigWorld
import VOIP
from PlayerEvents import g_playerEvents
from account_helpers.settings_core import settings_constants
from commendations_common.CommendationHelpers import CommendationsSource
from gui.battle_control import avatar_getter
from gui.doc_loaders.badges_loader import getSelectedByLayout
from gui.impl import backport
from gui.prb_control import prbInvitesProperty
from gui.prestige.prestige_helpers import fillPrestigeEmblemModel
from cgf_components.marker_component import IBattleSessionProvider
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.common.battle_player import BattlePlayer, VehicleTypeEnum
from gui.impl.gen.view_models.common.commendationStateModel import CommendationStateEnum
from gui.impl.gui_decorators import args2params
from gui.impl.gen.view_models.views.battle.battle_page.tab_view_model import TabViewModel, TabAlias
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from live_tags_constants import LIVE_TAG_TYPES
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import MutedFindCriteria, IgnoredFindCriteria
from messenger.storage import storage_getter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPlatoonController, ICommendationsController, IAnonymizerController
from skeletons.gui.goodies import IBoostersStateProvider
from helpers import dependency
from gui.impl.gen import R
from gui.battle_control.arena_info import settings, squad_finder
from frameworks.wulf import ViewModel
from gui.battle_control.battle_constants import TabsAliases
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getPersonalBoosterModelDataByResourceType, addPersonalBoostersGroup, addEventGroup
from gui.impl.lobby.personal_reserves.personal_reserves_utils import generatePersonalReserveTick
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS as _D_STATUS
from gui.shared.utils.requesters import REQ_CRITERIA
from constants import ARENA_GUI_TYPE, CommendationsState
from commendations_common import CommendationHelpers
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from messenger.proto.entities import ChatEntity
    from typing import Optional, Tuple, Set, Callable
    import ClientArena
    from gui.battle_control.arena_info.arena_vos import VehicleArenaStatsVO
    from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
    from frameworks.wulf import Array
    from gui.battle_control.controllers.battle_field_ctrl import BattleFieldCtrl
    from messenger.storage.UsersStorage import UsersStorage
    from messenger.storage.PlayerCtxStorage import PlayerCtxStorage
    from gui.prb_control.invites import InvitesManager
    from typing import List, Tuple, Dict
    from gui.goodies.booster_state_provider import BoosterStateProvider
    from gui.game_control.platoon_controller import PlatoonController
    from gui.battle_control.battle_session import BattleSessionProvider
    from gui.impl.gen_utils import DynAccessor
    from account_helpers.settings_core.SettingsCore import SettingsCore
    from TeamInfo import TeamInfo
_logger = logging.getLogger(__name__)
_VEHICLE_TYPE_SORTING_ORDER = (VehicleTypeEnum.HEAVYTANK,
 VehicleTypeEnum.MEDIUMTANK,
 VehicleTypeEnum.ATSPG,
 VehicleTypeEnum.LIGHTTANK,
 VehicleTypeEnum.SPG,
 VehicleTypeEnum.UNDEFINED)
_VEHICLE_TYPE_SORTING_ORDER_MAP = {vehicleType:order for order, vehicleType in enumerate(_VEHICLE_TYPE_SORTING_ORDER)}
_VEHICLE_TYPE_TO_VEHICLE_TYPE_ENUM = {VEHICLE_CLASS_NAME.HEAVY_TANK: VehicleTypeEnum.HEAVYTANK,
 VEHICLE_CLASS_NAME.MEDIUM_TANK: VehicleTypeEnum.MEDIUMTANK,
 VEHICLE_CLASS_NAME.LIGHT_TANK: VehicleTypeEnum.LIGHTTANK,
 VEHICLE_CLASS_NAME.AT_SPG: VehicleTypeEnum.ATSPG,
 VEHICLE_CLASS_NAME.SPG: VehicleTypeEnum.SPG}
_COMMENDATIONS_STATE_TO_ENUM = {CommendationsState.UNSENT: CommendationStateEnum.COMMENDFIRST,
 CommendationsState.SENT: CommendationStateEnum.OUTGOINGCOMMENDATION,
 CommendationsState.RECEIVED: CommendationStateEnum.COMMENDBACK,
 CommendationsState.MUTUAL: CommendationStateEnum.MUTUALCOMMENDATION}

def _playerCompositionKey(playerModel):
    return (playerModel.getIsKilled(),
     -playerModel.getVehicleLevel(),
     _VEHICLE_TYPE_SORTING_ORDER_MAP[playerModel.getVehicleType()],
     playerModel.getVehicleName(),
     playerModel.getHiddenUserName() if playerModel.getIsFakeNameVisible() else playerModel.getUserName(),
     playerModel.getVehicleId())


class BattlePlayerNotFound(SoftException):
    pass


class TabView(ViewImpl):
    __slots__ = ('_notificatorManager', '_visitor', '_battleCtx', '__playerIndexes', '_squadFinder')
    _boostersStateProvider = dependency.descriptor(IBoostersStateProvider)
    _platoonController = dependency.descriptor(IPlatoonController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    commendationsCtrl = dependency.descriptor(ICommendationsController)
    anonymizerController = dependency.descriptor(IAnonymizerController)

    def __init__(self, layoutID):
        viewSettings = ViewSettings(layoutID)
        viewSettings.flags = ViewFlags.VIEW
        viewSettings.model = TabViewModel()
        super(TabView, self).__init__(viewSettings)
        self._visitor = self.sessionProvider.arenaVisitor
        self._squadFinder = squad_finder.createSquadFinder(self._visitor)
        self._battleCtx = self.sessionProvider.getCtx()
        self._notificatorManager = Notifiable()
        self.__playerIndexes = {}

    @property
    def viewModel(self):
        return super(TabView, self).getViewModel()

    @property
    def battleField(self):
        return self.sessionProvider.dynamic.battleField

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    @property
    def arena(self):
        return avatar_getter.getArena()

    @property
    def teamInfo(self):
        return self.arena.teamInfo if self.arena else None

    def _getVehicleInfo(self, vehicleId):
        return self._visitor.getArenaVehicles().get(vehicleId) or None

    def _isAlly(self, vehicleInfo):
        return avatar_getter.getPlayerTeam() == vehicleInfo['team']

    def _getPlayerList(self, vehicleInfo):
        return self.viewModel.playerList.getAllies() if self._isAlly(vehicleInfo) else self.viewModel.playerList.getEnemies()

    def _setColorblindSettings(self, *args):
        isColorBlind = self._settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)
        self.viewModel.playerList.setIsColorblind(isColorBlind)

    def _onLoaded(self, *args, **kwargs):
        super(TabView, self)._onLoaded(*args, **kwargs)
        self._invalidateGameInfo()
        self._setColorblindSettings()
        self._setCommendationSettings()
        self._setLiveTagsSettings()
        self._setPlatoonSettings()

    def _setPlatoonSettings(self):
        self.viewModel.playerList.setPlatoonsEnabled(self._visitor.hasDynSquads())

    def _setCommendationSettings(self, *args):
        commendationAvatarComponent = CommendationHelpers.getAvatarComponent(BigWorld.player())
        self.viewModel.playerList.setIsCommendationEnabled(bool(self._visitor.hasCommendationsMessages() and commendationAvatarComponent))

    def _setLiveTagsSettings(self, *args):
        teamInfoLiveTagsComponents = CommendationHelpers.getTeamInfoLiveTagsComponent(self.teamInfo)
        self.viewModel.playerList.setIsLiveTagsEnabled(bool(self._visitor.hasLiveTags() and teamInfoLiveTagsComponents))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.personal_reserves.ReservesDisabledTooltip():
            viewSettings = ViewSettings(layoutID=R.views.common.personal_reserves.ReservesDisabledTooltip(), model=ViewModel())
            return ViewImpl(viewSettings)
        return super(TabView, self).createToolTipContent(event, contentID)

    @contextmanager
    def modifyBattlePlayer(self, vehicleId):
        player = self.__getBattlePlayer(vehicleId)
        try:
            try:
                yield player
            except BattlePlayerNotFound:
                _logger.warning('[TabView] Player model not found. (vehicleId: %d).', vehicleId)
            else:
                self.__setBattlePlayer(vehicleId, player)

        finally:
            pass

    def _finalize(self):
        self.__playerIndexes.clear()
        self._notificatorManager.clearNotification()
        super(TabView, self)._finalize()

    def _invalidateGameInfo(self, *args):
        self._squadFinder.clear()
        self._invalidateVehiclesInfo()
        self._updateInvites()
        self._resetChatActions()
        self._updateLiveTags()

    def _fillPlayerListModel(self, playerList, playerInfo):
        playerList.clear()
        playerList.reserve(len(playerInfo))
        for index, player in enumerate(playerInfo):
            playerList.addViewModel(player)
            self.__playerIndexes[player.getVehicleId()] = index

        playerList.invalidate()

    def __setBattlePlayer(self, vehicleId, player):
        if vehicleId not in self.__playerIndexes:
            _logger.warning('[TabView] Vehicle %d was not found in the cached indexes.', vehicleId)
            return
        vehicleInfo = self._visitor.getArenaVehicles()[vehicleId]
        if not vehicleInfo:
            _logger.warning('[TabView] Vehicle %d info not found.', vehicleId)
            return
        with self.viewModel.transaction():
            playerList = self._getPlayerList(vehicleInfo)
            playerList.setViewModel(self.__playerIndexes[vehicleId], player)
            playerList.invalidate()

    def __getBattlePlayer(self, vehicleId):
        vehicleInfo = self._visitor.getArenaVehicles().get(vehicleId)
        if vehicleInfo is None:
            _logger.warning('[TabView] Vehicle %d info not found.', vehicleId)
            return
        else:
            playerIndex = self.__playerIndexes.get(vehicleId)
            if playerIndex is None:
                _logger.warning('[TabView] Vehicle %d was not found in the cached indexes.', vehicleId)
                return
            return self._getPlayerList(vehicleInfo).getValue(playerIndex)

    def _invalidateVehiclesInfo(self, *args):
        self.__playerIndexes.clear()
        allies = []
        enemies = []
        for vehicleId, vehicleInfo in self._visitor.getArenaVehicles().iteritems():
            self._updateSquadFinder(vehicleId, vehicleInfo)
            player = self._fillPlayerModel(vehicleId, vehicleInfo)
            if self._isAlly(vehicleInfo):
                allies.append(player)
            enemies.append(player)

        with self.viewModel.transaction() as model:
            self._fillPlayerListModel(model.playerList.getAllies(), sorted(allies, key=_playerCompositionKey))
            self._fillPlayerListModel(model.playerList.getEnemies(), sorted(enemies, key=_playerCompositionKey))

    def _onVehicleUpdated(self, vehicleId):
        if vehicleId not in self.__playerIndexes:
            return
        vehicleInfo = self._getVehicleInfo(vehicleId)
        self._updateSquadFinder(vehicleId, vehicleInfo)
        with self.modifyBattlePlayer(vehicleId) as playerModel:
            self._invalidateVehicleStatus(playerModel)
            self._invalidatePlatoonInfo(playerModel)
        if self._needsResort(vehicleId):
            self._resortPlayerList(self._getPlayerList(vehicleInfo))

    def _needsResort(self, vehicleId):
        vehicleInfo = self._getVehicleInfo(vehicleId)
        if vehicleInfo is None:
            return False
        idx = self.__playerIndexes[vehicleId]
        playerModelList = self._getPlayerList(vehicleInfo)
        key = _playerCompositionKey(playerModelList[idx])
        previousKey = _playerCompositionKey(playerModelList[idx - 1]) if idx > 0 else None
        nextKey = _playerCompositionKey(playerModelList[idx + 1]) if idx < len(playerModelList) - 1 else None
        if previousKey is not None and key < previousKey:
            return True
        else:
            return True if nextKey is not None and key > nextKey else False

    def _updateSquadFinder(self, vehicleId, vehicleInfo):
        team = self._getTeam(vehicleInfo)
        prebattleId = self._getPrebattleID(vehicleInfo)
        if prebattleId:
            self._squadFinder.addVehicleInfo(team, prebattleId, vehicleId)

    def _onVehicleAdded(self, vehicleId):
        with self.viewModel.transaction():
            vehicleInfo = self._getVehicleInfo(vehicleId)
            player = self._fillPlayerModel(vehicleId, vehicleInfo)
            playerList = self._getPlayerList(vehicleInfo)
            self._resortPlayerList(playerList, [player])

    def _resortPlayerList(self, playerModelArray, playersToAdd=None):
        playerModelList = [ battlePlayer for battlePlayer in playerModelArray ]
        if playersToAdd is not None:
            playerModelList.extend(playersToAdd)
        self._fillPlayerListModel(playerModelArray, sorted(playerModelList, key=_playerCompositionKey))
        return

    def _fillPlayerModel(self, vehicleId, vehicleInfo):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        if not playerVehicleID:
            return
        player = BattlePlayer()
        player.setVehicleId(vehicleId)
        isCurrentPlayer = playerVehicleID == vehicleId
        player.setIsCurrentPlayer(isCurrentPlayer)
        self._invalidatePlatoonInfo(player)
        self._invalidatePersonalInfo(player)
        self._invalidateVehicleTypeInfo(player)
        self._invalidateVehicleStatus(player)
        self._invalidateDenunciationInfo(player, vehicleInfo['accountDBID'])
        self._invalidateVehicleStats(player)
        self._invalidateCommendationState(player)
        isAnonymized = self.anonymizerController.isAnonymized
        if isCurrentPlayer:
            self.viewModel.playerList.setIsAnonymized(isAnonymized)
            player.setIsFakeNameVisible(isAnonymized)
            self.viewModel.playerList.setHasClan(bool(vehicleInfo['clanAbbrev']))
            player.setAnonymizerTooltip(backport.text(self._getAnonymizerTooltipContent(player)(), fakeName=vehicleInfo['fakeName']))
        return player

    def _isSquadMember(self, memberVehID, prebattleId):
        vehInfo = self._getVehicleInfo(memberVehID)
        return self._getPrebattleID(vehInfo) == prebattleId if vehInfo is not None else False

    def _invalidatePlatoonInfo(self, playerModel):
        vehicleId = playerModel.getVehicleId()
        vehicleInfo = self._getVehicleInfo(vehicleId)
        prebattleId = self._getPrebattleID(vehicleInfo)
        isAvatarSquad = self._isAvatarSquad(prebattleId)
        if not prebattleId:
            playerModel.setIsPlatoonInvitationDisabled(not self._isPlatoonInvitationEnabled(vehicleId))
            return
        for vehId, squadIdx in self._squadFinder.findSquads():
            if self._isSquadMember(vehId, prebattleId):
                model = self.__getBattlePlayer(vehId)
                if not model:
                    continue
                model.setPlatoon(squadIdx)
                model.setIsMyPlatoon(isAvatarSquad)
                model.setIsPlatoonInvitationDisabled(not self._isPlatoonInvitationEnabled(vehId))

    def _isAvatarSquad(self, prebattleId):
        playerVehInfo = self._getVehicleInfo(avatar_getter.getPlayerVehicleID())
        return playerVehInfo and prebattleId and prebattleId == self._getPrebattleID(playerVehInfo)

    @staticmethod
    def _getTeam(vehicleInfo):
        return vehicleInfo.get('team', 0) if vehicleInfo is not None else 0

    @staticmethod
    def _getPrebattleID(vehicleInfo):
        return vehicleInfo.get('prebattleID', 0) if vehicleInfo is not None else 0

    def _isPlatoonInvitationEnabled(self, vehicleId):
        arenaDP = self.sessionProvider.getArenaDP()
        vehicleInfo = arenaDP.getVehicleInfo(vehicleId)
        status = vehicleInfo.invitationDeliveryStatus
        if status & _D_STATUS.FORBIDDEN_BY_RECEIVER > 0:
            return False
        if vehicleInfo.isSquadMan():
            return False
        if not self._visitor.hasDynSquads():
            return False
        _, ignoredUsers = self._getChatUserStatuses()
        return False if vehicleId in ignoredUsers else self._battleCtx.isInvitationEnabled() and not self._battleCtx.hasSquadRestrictions()

    def _invalidateVehicleStats(self, player):
        vehicleId = player.getVehicleId()
        if vehicleId:
            player.setKills(self._visitor.getArenaStatistics().get(vehicleId, {}).get('frags', 0))

    def _invalidateVehicleTypeInfo(self, player):
        vehicleId = player.getVehicleId()
        if not vehicleId:
            return
        else:
            vehicleInfo = self._getVehicleInfo(vehicleId)
            if vehicleInfo is None:
                return
            vehicleTypeInfo = vehicleInfo['vehicleType']
            if vehicleTypeInfo:
                player.setVehicleLevel(vehicleTypeInfo.level)
                player.setVehicleContourUrl(settings.makeVehicleIconName(vehicleTypeInfo.name))
                player.setVehicleName(vehicleTypeInfo.type.shortUserString)
                player.setVehicleType(_VEHICLE_TYPE_TO_VEHICLE_TYPE_ENUM[vehicleTypeInfo.type.classTag])
                fillPrestigeEmblemModel(player.prestigeEmblemModel, vehicleInfo['prestigeLevel'], vehicleTypeInfo.type.compactDescr)
            return

    def _invalidateDenunciationInfo(self, player, violatorDbID):
        player.setIsReported(self.playerCtx.hasAnyDenunciationSubmitted(violatorDbID))

    def _invalidateVehicleStatus(self, player):
        vehicleId = player.getVehicleId()
        if not vehicleId:
            return
        vehicleInfo = self._getVehicleInfo(vehicleId)
        if vehicleInfo:
            isTeamKiller = vehicleInfo['isTeamKiller']
            if player.getIsCurrentPlayer():
                isTeamKiller |= avatar_getter.isPlayerTeamKillSuspected()
            player.setIsTeamKiller(isTeamKiller)
            player.setIsKilled(not vehicleInfo['isAlive'])
            player.setIsLoaded(vehicleInfo['isAvatarReady'])

    def _invalidatePersonalInfo(self, player):
        vehicleId = player.getVehicleId()
        if not vehicleId:
            return
        else:
            vehicleInfo = self._getVehicleInfo(vehicleId)
            if vehicleInfo is None:
                return
            player.setClanAbbrev(vehicleInfo['clanAbbrev'])
            player.setDatabaseID(vehicleInfo['accountDBID'])
            player.setAvatarSessionID(vehicleInfo['avatarSessionID'] or '')
            player.setHiddenUserName(vehicleInfo['fakeName'])
            player.setIgrType(vehicleInfo['igrType'])
            player.setUserName(vehicleInfo['name'])
            prefixBadge, suffixBadge = getSelectedByLayout(vehicleInfo['badges'][0])
            player.badge.setBadgeID(str(prefixBadge))
            player.suffixBadge.setBadgeID(str(suffixBadge))
            return

    def _addStats(self, *args):
        with self.viewModel.transaction() as model:
            for playersArray in (model.playerList.getAllies(), model.playerList.getEnemies()):
                for player in playersArray:
                    self._invalidateVehicleStats(player)

                playersArray.invalidate()

    def _updateStats(self, vehicleId):
        with self.modifyBattlePlayer(vehicleId) as player:
            if player is None:
                raise BattlePlayerNotFound
            self._invalidateVehicleStats(player)
        return

    def _onFogOfWarEnabled(self, flag):
        self.viewModel.playerList.setIsFogOfWarEnabled(flag)

    def _updateInvites(self, *args):
        with self.viewModel.transaction() as model:
            playerList = model.playerList.getAllies()
            for player in playerList:
                player.setIsInviteSent(player.getAvatarSessionID() in self.__getInviteIds(received=False))
                player.setIsInviteReceived(player.getAvatarSessionID() in self.__getInviteIds(received=True))
                self._invalidatePlatoonInfo(player)

            playerList.invalidate()

    def __getInviteIds(self, received=False):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        if not playerVehicleID:
            return set()
        invites = self.prbInvites.getInvites(onlyActive=True)
        ownVehicleInfo = self._visitor.getArenaVehicles().get(playerVehicleID)
        if ownVehicleInfo is None:
            if not self.sessionProvider.isReplayPlaying:
                _logger.warning('[TabView] Vehicle %d info not found.', ownVehicleInfo)
            return set()
        else:
            return {inv.creatorID for inv in invites if inv.receiverID == ownVehicleInfo['avatarSessionID']} if received else {inv.receiverID for inv in invites if inv.creatorID == ownVehicleInfo['avatarSessionID']}

    def _updateDenunciations(self, denunciationInfo):
        violatorVehId = denunciationInfo[0]
        with self.modifyBattlePlayer(violatorVehId) as player:
            if player is None:
                raise BattlePlayerNotFound
            self._invalidateDenunciationInfo(player, violatorVehId)
        return

    def _updateStatus(self, vehicleId, *args):
        if vehicleId not in self.__playerIndexes:
            return
        else:
            with self.modifyBattlePlayer(vehicleId) as player:
                if player is None:
                    raise BattlePlayerNotFound
                vehicleInfo = self._visitor.getArenaVehicles().get(vehicleId)
                if not vehicleInfo:
                    _logger.warning('[TabView] Vehicle %d info not found.', vehicleId)
                    return
                self._invalidateVehicleStatus(player)
            return

    def _onSpottedStatusChanged(self, updated, _):
        updatedVehicles = {update[1].vehicleID for update in updated}
        for vehicleId in updatedVehicles:
            if vehicleId not in self.__playerIndexes:
                self._onVehicleAdded(vehicleId)
                return
            self._updateStats(vehicleId)

    def _onPlayerSpeaking(self, accountDBID, isSpeak):
        vehicleId = self.sessionProvider.getArenaDP().getVehIDByAccDBID(accountDBID)
        with self.modifyBattlePlayer(vehicleId) as player:
            if player is None:
                raise BattlePlayerNotFound
            player.setIsVoiceActive(isSpeak)
        return

    def _hasMutedSelfInPlatoon(self, vehicleId):
        arenaDP = self.sessionProvider.getArenaDP()
        vehicleInfo = arenaDP.getVehicleInfo(vehicleId)
        voipMgr = VOIP.getVOIPManager()
        if not vehicleId == avatar_getter.getPlayerVehicleID():
            return False
        if not vehicleInfo.isSquadMan():
            return False
        if self._visitor.gui.guiType not in ARENA_GUI_TYPE.VOIP_SUPPORTED:
            return False
        return False if self.sessionProvider.isReplayPlaying else not (voipMgr.isEnabled() and voipMgr.isCurrentChannelEnabled())

    def _invalidateChatActions(self, vehicleId):
        sessionId = self.sessionProvider.getArenaDP().getSessionIDByVehID(vehicleId)
        mutedUsers, ignoredUsers = self._getChatUserStatuses()
        isMuted = sessionId in mutedUsers or self._hasMutedSelfInPlatoon(vehicleId)
        with self.modifyBattlePlayer(vehicleId) as player:
            if player is None:
                raise BattlePlayerNotFound
            player.setIsVoiceMuted(isMuted)
            player.setIsChatMuted(sessionId in ignoredUsers)
            self._invalidatePlatoonInfo(player)
        return

    def _onVOIPChannelStateToggled(self, *args):
        vehicleId = avatar_getter.getPlayerVehicleID()
        if not vehicleId:
            return
        self._invalidateChatActions(vehicleId)

    def _updateChatActions(self, _, user):
        vehicleId = self.sessionProvider.getArenaDP().getVehIDBySessionID(user.getID())
        if not vehicleId:
            return
        self._invalidateChatActions(vehicleId)

    def _resetChatActions(self):
        mutedUsers, ignoredUsers = self._getChatUserStatuses()
        with self.viewModel.transaction() as model:
            for playersArray in (model.playerList.getAllies(), model.playerList.getEnemies()):
                for player in playersArray:
                    isMuted = player.getAvatarSessionID() in mutedUsers or self._hasMutedSelfInPlatoon(player.getVehicleId())
                    player.setIsVoiceMuted(isMuted)
                    player.setIsChatMuted(player.getAvatarSessionID() in ignoredUsers)
                    self._invalidatePlatoonInfo(player)

                playersArray.invalidate()

    def _getChatUserStatuses(self):
        mutedUsers = {user.getID() for user in self.usersStorage.getList(MutedFindCriteria())}
        ignoredUsers = {user.getID() for user in self.usersStorage.getList(IgnoredFindCriteria(includeTmpIgnore=True))}
        return (mutedUsers, ignoredUsers)

    def _updateCommendationStates(self):
        with self.viewModel.transaction() as model:
            playerArray = model.playerList.getAllies()
            for player in playerArray:
                self._invalidateCommendationState(player)

            model.setShowCommendationAnimations(True)
            playerArray.invalidate()

    def _updateLiveTags(self):
        if not self.teamInfo:
            return
        teamInfoLiveTagsComponent = CommendationHelpers.getTeamInfoLiveTagsComponent(self.teamInfo)
        if not (self._visitor.hasLiveTags() and teamInfoLiveTagsComponent):
            return
        liveTagValidator = self.__vehicleHasLiveTagValidator(self.__getLiveTagVehicleSets(teamInfoLiveTagsComponent))
        with self.viewModel.transaction() as model:
            playerArray = model.playerList.getAllies()
            for player in playerArray:
                vehId = player.getVehicleId()
                player.setLiveTagDamage(liveTagValidator(vehId, LIVE_TAG_TYPES.TOP_DAMAGE))
                player.setLiveTagBlock(liveTagValidator(vehId, LIVE_TAG_TYPES.TOP_BLOCK))
                player.setLiveTagAssist(liveTagValidator(vehId, LIVE_TAG_TYPES.TOP_ASSIST))
                tooltipTitle, tooltipBody = self._getLiveTagTooltipContent(player, liveTagValidator)
                player.setLiveTagTooltipTitle(tooltipTitle())
                player.setLiveTagTooltipBody(tooltipBody())

            playerArray.invalidate()

    def __vehicleHasLiveTagValidator(self, tagsSets):

        def vehicleHasLiveTag(vehId, tag):
            return vehId in tagsSets[tag] if tag in tagsSets else False

        return vehicleHasLiveTag

    def __getLiveTagVehicleSets(self, teamInfoLiveTagsComponent):
        return {tagInfo['tag']:set(tagInfo['vehicles']) for tagInfo in teamInfoLiveTagsComponent.liveTags}

    def _invalidateCommendationState(self, player):
        vehicleId = player.getVehicleId()
        commendationAvatarComponent = CommendationHelpers.getAvatarComponent(BigWorld.player())
        if not (self._visitor.hasCommendationsMessages() and commendationAvatarComponent):
            return
        if not self._canBeCommended(vehicleId):
            player.commendationStateModel.setCommendationState(CommendationStateEnum.UNAVAILABLE)
            return
        commendationState = _COMMENDATIONS_STATE_TO_ENUM[CommendationHelpers.getCommendationState(vehicleId)]
        isNewState = commendationState != player.commendationStateModel.getCommendationState()
        player.commendationStateModel.setCommendationState(commendationState)
        player.commendationStateModel.setIsNewState(isNewState)

    def _getAnonymizerTooltipContent(self, player):
        if bool(player.getPlatoon()):
            if bool(player.getClanAbbrev()):
                return R.strings.ingame_gui.dynamicSquad.ally.anonymized.clan
            return R.strings.ingame_gui.dynamicSquad.ally.anonymized.noClan
        return R.strings.tooltips.anonymizer.battle.teamList.clan if bool(player.getClanAbbrev()) else R.strings.tooltips.anonymizer.battle.teamList.noClan

    def _getLiveTagTooltipContent(self, player, validator):
        vehId = player.getVehicleId()
        resStrTitle = R.strings.tooltips.liveTags.title
        resStrBody = R.strings.tooltips.liveTags.body.dyn('currentPlayer' if player.getIsCurrentPlayer() else 'ally')
        for tagKey in [ LIVE_TAG_TYPES.NAMES[tag] for tag in LIVE_TAG_TYPES.ALL if validator(vehId, tag) ]:
            resStrTitle, resStrBody = resStrTitle.dyn(tagKey), resStrBody.dyn(tagKey)

        return (resStrTitle, resStrBody)

    def _canBeCommended(self, vehicleId):
        _, ignoredUsers = self._getChatUserStatuses()
        if vehicleId in ignoredUsers:
            return False
        else:
            vehicleInfo = self._visitor.getArenaVehicles().get(vehicleId)
            if vehicleInfo is None:
                _logger.warning('[TabView] Vehicle %d info not found.', vehicleId)
                return False
            return self._visitor.hasCommendationsMessages() and self._isAlly(vehicleInfo) and vehicleInfo['avatarSessionID']

    @args2params(int)
    def _onPlayerCommend(self, vehicleId):
        commsCtrl = self.sessionProvider.dynamic.commendationsMessagesController
        commsCtrl.sendCommendations(vehicleId, CommendationsSource.TAB_SCREEN)

    def _getEvents(self):
        usersEvents = g_messengerEvents.users
        events = [(usersEvents.onBattleUserActionReceived, self._updateChatActions),
         (self.viewModel.playerList.onPlatoonInvite, self._onPlatoonInvite),
         (self.viewModel.playerList.onPlayerCommend, self._onPlayerCommend),
         (self.viewModel.personalReserves.onBoosterActivate, self._onBoosterActivate),
         (self._boostersStateProvider.onStateUpdated, self._updateBoosters),
         (g_messengerEvents.voip.onPlayerSpeaking, self._onPlayerSpeaking),
         (g_messengerEvents.voip.onChannelEntered, self._onVOIPChannelStateToggled),
         (g_messengerEvents.voip.onChannelLeft, self._onVOIPChannelStateToggled),
         (g_playerEvents.onPrebattleInvitesChanged, self._updateInvites),
         (g_playerEvents.onPrebattleInvitationsChanged, self._updateInvites),
         (g_playerEvents.onPrebattleInvitesStatus, self._updateInvites)]
        if self.playerCtx is not None:
            events.append((self.playerCtx.onDenunciationsChanged, self._updateDenunciations))
        commendationAvatarComponent = CommendationHelpers.getAvatarComponent(BigWorld.player())
        if self._visitor.hasCommendationsMessages() and commendationAvatarComponent:
            events.append((commendationAvatarComponent.onStateUpdate, self._updateCommendationStates))
        if self.teamInfo:
            teamInfoLiveTagsComponents = CommendationHelpers.getTeamInfoLiveTagsComponent(self.teamInfo)
            if self._visitor.hasLiveTags() and teamInfoLiveTagsComponents:
                events.append((teamInfoLiveTagsComponents.onStateUpdate, self._updateLiveTags))
        if self.arena is not None:
            events.extend([(self.arena.onNewVehicleListReceived, self._invalidateGameInfo),
             (self.arena.onVehicleAdded, self._onVehicleAdded),
             (self.arena.onVehicleUpdated, self._onVehicleUpdated),
             (self.arena.onVehicleKilled, self._updateStatus),
             (self.arena.onVehicleRecovered, self._updateStatus),
             (self.arena.onAvatarReady, self._updateStatus),
             (self.arena.onNewStatisticsReceived, self._addStats),
             (self.arena.onVehicleStatisticsUpdate, self._updateStats),
             (self.arena.onTeamKiller, self._updateStatus),
             (self.arena.onInteractiveStats, self._addStats),
             (self.arena.onGameModeSpecificStats, self._addStats),
             (self.arena.onFogOfWarEnabled, self._onFogOfWarEnabled)])
        if self._settingsCore is not None:
            events.append((self._settingsCore.onSettingsChanged, self._setColorblindSettings))
            events.append((self._settingsCore.onSettingsChanged, self._setCommendationSettings))
            events.append((self._settingsCore.onSettingsChanged, self._setLiveTagsSettings))
        if self.prbInvites is not None:
            events.append((self.prbInvites.onInvitesListInited, self._updateInvites))
        if self.battleField is not None:
            events.append((self.battleField.onSpottedStatusChanged, self._onSpottedStatusChanged))
        return events

    def handleTabChange(self, tabAlias):
        _logger.debug('_handleFullStatsSelected: alias[%s]', tabAlias)
        if tabAlias == TabsAliases.STATS.value:
            self.viewModel.setTabSelection(TabAlias.STATS)
        elif tabAlias == TabsAliases.BOOSTERS.value:
            with self.viewModel.transaction() as model:
                model.setTabSelection(TabAlias.RESERVES)
                model.setShowCommendationAnimations(False)

    def _onLoading(self, *args, **kwargs):
        super(TabView, self)._onLoading(*args, **kwargs)
        self._notificatorManager.addNotificator(PeriodicNotifier(self._timeTillNextPersonalReserveTick, self.fillViewModel))
        self._updateBoosters()

    @args2params(str)
    def _onPlatoonInvite(self, avatarSessionID):
        if avatarSessionID in self.__getInviteIds(received=True):
            self.sessionProvider.invitations.accept(avatarSessionID)
        else:
            self.sessionProvider.invitations.send(avatarSessionID)
        self._updateInvites()

    def activatePersonalReserve(self, boosterId):
        BigWorld.player().activateGoodie(boosterId)

    @args2params(int)
    def _onBoosterActivate(self, boosterId):
        booster = self._boostersStateProvider.getBooster(boosterId)
        if booster.boosterType in self._boostersStateProvider.getActiveBoosterTypes():
            _logger.warning('[PersonalReservesTabView] Booster %d cannot be activated as another booster of the same type is already active in this battle.', booster.boosterID)
            return
        if booster.isInAccount:
            self.activatePersonalReserve(boosterId)
        else:
            _logger.warning('[PersonalReservesTabView] Cannot activate booster %d, player does not have this booster in inventory. Buy and activate action is not possible during battle.', booster.boosterID)

    def _updateBoosters(self):
        self._notificatorManager.startNotification()
        self.fillViewModel()

    def fillViewModel(self):
        boosterModelsArgsByType = getPersonalBoosterModelDataByResourceType(self._boostersStateProvider)
        with self.viewModel.personalReserves.transaction() as model:
            groupArray = model.getReserveGroups()
            groupArray.clear()
            for resourceType in PERSONAL_RESOURCE_ORDER:
                addPersonalBoostersGroup(resourceType, boosterModelsArgsByType, groupArray)

            addEventGroup(groupArray, self._boostersStateProvider)
            groupArray.invalidate()

    def _timeTillNextPersonalReserveTick(self):
        expiringReserves = self._boostersStateProvider.getBoosters(REQ_CRITERIA.BOOSTER.LIMITED).values()
        return generatePersonalReserveTick(expiringReserves)
