# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/battle_result_view.py
from adisp import adisp_process
from constants import PREBATTLE_TYPE, IGR_TYPE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.prb_control import prbInvitesProperty
from frameworks.wulf import ViewFlags, ViewSettings, WindowStatus
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, PRB_INVITE_STATE
from messenger.m_constants import PROTO_TYPE, USER_TAG, UserEntityScope
from messenger.proto.entities import SharedUserEntity
from messenger.proto.entities import ClanInfo as UserClanInfo
from messenger.proto.events import g_messengerEvents
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from halloween.gui.impl.gen.view_models.views.lobby.common.base_quest_model import QuestStatusEnum, BaseQuestModel
from halloween.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel
from halloween.gui.impl.gen.view_models.views.lobby.base_info_model import BaseInfoModel
from halloween.gui.impl.gen.view_models.views.lobby.common.base_team_member_model import BaseTeamMemberModel
from halloween.gui.impl.gen.view_models.views.lobby.common.stat_model import StatModel
from halloween.gui.impl.gen.view_models.views.lobby.common.stat_column_settings_model import ColumnEnum
from skeletons.gui.battle_results import IBattleResultsService
from halloween.gui.impl.lobby.base_event_view import BaseEventView
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IPlatoonController, IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.sounds.ambients import BattleResultsEnv
_CHECK_FRIEND_TIMEOUT = 5.0
_DEFAULT_CONTEXT_MENU_PLAYER_ID = -1

def _getRank(playerVO, players):
    return players.index(playerVO['hwXP']) + 1


class BattleResultView(BaseEventView, CallbackDelayer):
    __slots__ = ('__arenaUniqueID', '__contextMenuWindow')
    battleResults = dependency.descriptor(IBattleResultsService)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventBattlesController = dependency.descriptor(IEventBattlesController)
    settingsCore = dependency.descriptor(ISettingsCore)
    __sound_env__ = BattleResultsEnv

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID or R.views.halloween.lobby.BattleResultView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattleResultViewModel()
        super(BattleResultView, self).__init__(settings)
        self.arenaUniqueID = ctx.get('arenaUniqueID', -1)
        self.playerRank = 0
        self.currentPlayerID = 0
        self.__contextMenuWindow = None
        return

    @property
    def viewModel(self):
        return super(BattleResultView, self).getViewModel()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            dbID = event.getArgument('playerId')
            if dbID == self.currentPlayerID:
                return
            contextMenuArgs = {'dbID': event.getArgument('playerId'),
             'userName': event.getArgument('userName'),
             'clanAbbrev': event.getArgument('clanAbbrev'),
             'vehicleCD': event.getArgument('vehicleCD'),
             'isAlly': event.getArgument('isAlly'),
             'clientArenaIdx': event.getArgument('clientArenaIdx'),
             'wasInBattle': True}
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, contextMenuArgs)
            self.__contextMenuWindow = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            self.__contextMenuWindow.onStatusChanged += self.__onStatusChangedContextMenu
            self.__contextMenuWindow.load()
            with self.viewModel.transaction() as tx:
                tx.setContextMenuPlayerId(dbID)
            return self.__contextMenuWindow
        return super(BattleResultView, self).createContextMenu(event)

    def __onStatusChangedContextMenu(self, windowStatus):
        if windowStatus == WindowStatus.DESTROYED:
            with self.viewModel.transaction() as tx:
                tx.setContextMenuPlayerId(_DEFAULT_CONTEXT_MENU_PLAYER_ID)
            self.__contextMenuWindow.onStatusChanged -= self.__onStatusChangedContextMenu
            self.__contextMenuWindow = None
        return

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        self._addEventListeners()
        self.__fillViewModel()

    def _initialize(self, *args, **kwargs):
        super(BattleResultView, self)._initialize()
        self.__updateHeader(visibility=False)

    def _finalize(self):
        self._removeEventListeners()
        self.__updateHeader(visibility=True)
        self.__contextMenuWindow = None
        super(BattleResultView, self)._finalize()
        return

    def _onClose(self, *_):
        self.destroyWindow()

    def _addEventListeners(self):
        self.viewModel.playerTeamColumnSettings.onSetSortBy += self._onSetPlayerTeamSortBy
        self.viewModel.enemyTeamColumnSettings.onSetSortBy += self._onSetEnemyTeamSortBy
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated += self._onUserStatusUpdated
        self._eventController.onPrimeTimeStatusUpdated += self._updateEventStatus
        self.viewModel.sendFriendRequest += self._sendFriendRequest
        self.viewModel.sendPlatoonInvitation += self._sendPlatoonInvitation
        self.viewModel.removeFromBlacklist += self._removeFromBlacklist
        self.viewModel.onClose += self._onClose
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified += self._onSentInviteListModified
        self.platoonCtrl.onMembersUpdate += self._onMembersSquadUpdate
        self.platoonCtrl.onLeavePlatoon += self._onMembersSquadUpdate
        return

    def _removeEventListeners(self):
        self.viewModel.playerTeamColumnSettings.onSetSortBy -= self._onSetPlayerTeamSortBy
        self.viewModel.enemyTeamColumnSettings.onSetSortBy -= self._onSetEnemyTeamSortBy
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated -= self._onUserStatusUpdated
        self._eventController.onPrimeTimeStatusUpdated -= self._updateEventStatus
        self.viewModel.sendFriendRequest -= self._sendFriendRequest
        self.viewModel.sendPlatoonInvitation -= self._sendPlatoonInvitation
        self.viewModel.removeFromBlacklist -= self._removeFromBlacklist
        self.viewModel.onClose -= self._onClose
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified -= self._onSentInviteListModified
        self.platoonCtrl.onMembersUpdate -= self._onMembersSquadUpdate
        self.platoonCtrl.onLeavePlatoon -= self._onMembersSquadUpdate
        return

    def _sendFriendRequest(self, args=None):
        if not args:
            return
        else:
            dbID = int(args.get('playerId', 0))
            userName = args.get('userName')
            if not (dbID and userName):
                return
            if not self.lobbyContext.getServerSettings().roaming.isSameRealm(dbID):
                return
            user = self.usersStorage.getUser(dbID)
            if user is None:
                user = SharedUserEntity(dbID, name=userName, clanInfo=UserClanInfo(abbrev=args.get('clanAbbrev', '')), scope=UserEntityScope.LOBBY, tags={USER_TAG.SEARCH, USER_TAG.TEMP})
                self.usersStorage.addUser(user)
            if not user.isFriend():
                self.proto.contacts.addFriend(dbID, userName)
                self.delayCallback(_CHECK_FRIEND_TIMEOUT, self.__checkFriendOnDelay, dbID)
            elif self.proto.contacts.isBidiFriendshipSupported() and USER_TAG.SUB_NONE in user.getTags():
                self.proto.contacts.requestFriendship(dbID)
                self.delayCallback(_CHECK_FRIEND_TIMEOUT, self.__checkFriendOnDelay, dbID)
            return

    @adisp_process
    def _sendPlatoonInvitation(self, args):
        if not (args and self._eventController.isEnabled()):
            return
        dbID = args.get('playerId')
        if not dbID:
            return
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_SQUAD, accountsToInvite=(int(dbID),)))

    def _removeFromBlacklist(self, args=None):
        if not args:
            return
        dbID = args.get('playerId')
        if not dbID:
            return
        self.proto.contacts.removeIgnored(dbID)

    @args2params(str)
    def _onSetPlayerTeamSortBy(self, column):
        previous = self.viewModel.playerTeamColumnSettings.getSortBy()
        with self.viewModel.transaction() as tx:
            tx.playerTeamColumnSettings.setSortBy(column)
            if previous == column:
                tx.playerTeamColumnSettings.setSortDirection(not tx.playerTeamColumnSettings.getSortDirection())
            else:
                tx.playerTeamColumnSettings.setSortDirection(True)

    @args2params(str)
    def _onSetEnemyTeamSortBy(self, column):
        previous = self.viewModel.enemyTeamColumnSettings.getSortBy()
        with self.viewModel.transaction() as tx:
            tx.enemyTeamColumnSettings.setSortBy(column)
            if previous == column:
                tx.enemyTeamColumnSettings.setSortDirection(not tx.enemyTeamColumnSettings.getSortDirection())
            else:
                tx.enemyTeamColumnSettings.setSortDirection(True)

    def _updateEventStatus(self, _):
        self.__updateMembersStatus()

    def _onMembersSquadUpdate(self):
        self.__fillViewModel()

    def _onUserActionReceived(self, _, user, __):
        self.__checkUserStatusUpdate(user)

    def _onUserStatusUpdated(self, user):
        self.__checkUserStatusUpdate(user)

    def _onSentInviteListModified(self, added, changed, deleted):
        if not self._eventController.isEnabled():
            return
        allChangedInvites = set(added) | set(changed) | set(deleted)
        for inviteID in allChangedInvites:
            invite = self.prbInvites.getInvite(inviteID)
            if invite.type != PREBATTLE_TYPE.EVENT:
                continue
            dbID = invite.receiverID
            state = invite.getState()
            self.__setStatusPlatoonRequestSent(dbID, state)

    def __fillViewModel(self):
        vo = self.battleResults.getResultsVO(self.arenaUniqueID)
        with self.viewModel.transaction() as tx:
            self.__fillCommonInfo(tx, vo['common'])
            self.__fillQuests(tx, vo['quests'])
            self.__fillTeams(tx, vo)
            self.__fillPlayerInfo(tx, vo)
            self.__fillBattleInfo(tx, vo['common'])
            self.__fillBaseCaptureInfo(tx, vo)

    def __fillCommonInfo(self, model, vo):
        model.setTitle(backport.text(R.strings.battle_results.hw_battle_result.status.dyn(vo['resultShortStr'])()))
        model.setSubTitle(vo['finishReasonStr'])
        model.playerTeamColumnSettings.setSortBy(ColumnEnum.EXPERIENCE.value)
        model.enemyTeamColumnSettings.setSortBy(ColumnEnum.EXPERIENCE.value)
        model.playerTeamColumnSettings.setSortDirection(True)
        model.enemyTeamColumnSettings.setSortDirection(True)

    def __fillQuests(self, model, questsVO):
        if not questsVO:
            return
        currentPhaseIndex = questsVO[0]['currentPhaseIndex']
        phase = self._hwController.phasesHalloween.getPhaseByIndex(currentPhaseIndex)
        if not phase:
            return
        data = phase.getAbilityInfo(dailyQuest=False)
        if not data:
            return
        model.setSelectedPhase(currentPhaseIndex)
        equipment, _, _ = data
        questModels = model.getQuests()
        questModels.clear()
        for quest in questsVO:
            questInfo = quest['info']
            questModel = BaseQuestModel()
            questModel.setName(questInfo['qID'].replace(':', '_'))
            questModel.setStatus(QuestStatusEnum.COMPLETED if questInfo['isCompleted'] else QuestStatusEnum.INPROGRESS)
            questModel.setAbilityIcon(equipment.descriptor.iconName)
            questModel.setAbilityName(equipment.shortUserName)
            questModel.setAmount(questInfo['totalProgress'])
            questModel.setProgress(questInfo['currentProgress'])
            questModel.setDeltaFrom(questInfo['prevProgress'])
            questModels.addViewModel(questModel)

        questModels.invalidate()

    def __fillTeams(self, model, vo):
        for team, playerVO, isAlly in ((model.getPlayerTeam(), vo['team1'], True), (model.getEnemyTeam(), vo['team2'], False)):
            self.__fillTeamsModel(team, playerVO, isAlly)

    def __fillTeamsModel(self, model, playersVO, isAlly):
        model.clear()
        playersXP = sorted(list({playerVO['hwXP'] for playerVO in playersVO}), reverse=True)
        for index, playerVO in enumerate(playersVO, start=1):
            model.addViewModel(self.__createTeamMember(index, _getRank(playerVO, playersXP), playerVO, isAlly))

        model.invalidate()

    def __createTeamMember(self, index, rank, playerVO, isAlly):
        member = BaseTeamMemberModel()
        isSelf = playerVO['isSelf']
        dbID = playerVO['playerId']
        if isSelf:
            self.playerRank = rank
            self.currentPlayerID = dbID
        member.setId(index)
        member.setIsCurrentPlayer(isSelf)
        member.setPlayerId(dbID)
        member.setIsOwnSquad(playerVO['isSelf'] or playerVO['isOwnSquad'])
        member.setIsPrematureLeave(playerVO['isPrematureLeave'])
        member.setSquadNum(playerVO['squadID'])
        member.setIsWarned(playerVO['fairplayViolations'])
        member.setIsAlly(isAlly)
        member.setIsFriendRequestSent(self.__isRequestFriendSent(dbID))
        member.setIsInFriendList(self.__isFriend(dbID))
        member.setIsPlatoonRequestCanBeMade(self.__canCreateSquad() and not self.__isPlayerInSquad(dbID))
        member.setIsPlatoonRequestSent(self.__isRequestSquadSent(dbID))
        member.setIsBlacklisted(self.__isPlayerInIgnoreList(dbID))
        member.stats.setPlace(rank)
        member.stats.setDamage(playerVO['damageDealt'])
        member.stats.setExperience(playerVO['hwXP'])
        member.stats.setKills(playerVO['kills'])
        member.user.setUserName(playerVO['userVO']['userName'])
        member.user.setClanAbbrev(playerVO['userVO']['clanAbbrev'])
        member.user.setIgrType(IGR_TYPE.PREMIUM if playerVO['isPremiumIGR'] else IGR_TYPE.NONE)
        badgeID = playerVO['badgeID']
        member.user.badge.setBadgeID('' if badgeID == 0 else str(badgeID))
        member.user.setIsFakeNameVisible(False)
        member.vehicle.setVehicleName(playerVO['vehicleName'])
        member.vehicle.setVehicleFullName(playerVO['vehicleFullName'])
        member.vehicle.setVehicleType(playerVO['vehicleType'])
        member.vehicle.setVehicleLvl(playerVO['vehicleLvl'])
        member.vehicle.setIconPath(playerVO['tankIcon'])
        member.vehicle.setVehicleCD(playerVO['vehicleCD'])
        self.__fillTeamMemberDetailedStats(member, playerVO)
        return member

    def __fillTeamMemberDetailedStats(self, model, vo):
        for voStat in vo['statValues'][0]:
            stat = StatModel()
            stat.setStatName(voStat['label'])
            stat.setStatValue(voStat['value'])
            model.detailedStats.getStats().addViewModel(stat)

    def __fillPlayerInfo(self, model, vo):
        model.playerInfo.user.setUserName(vo['playerName'])
        model.playerInfo.user.setClanAbbrev(vo['playerClan'])
        model.playerInfo.vehicle.setVehicleName(vo['vehicleName'])
        model.playerInfo.setNumberOfRespawns(vo['respawns'])
        model.playerInfo.stats.setKills(vo['kills'])
        model.playerInfo.stats.setDamage(vo['damageDelta'])
        model.playerInfo.stats.setPlace(self.playerRank)
        model.playerInfo.stats.setExperience(vo['hwXP'])

    def __fillBattleInfo(self, model, vo):
        model.battleInfo.setMapName(vo['arenaStr'])
        model.battleInfo.setStartDate(vo['arenaCreateTimeStr'])
        model.battleInfo.setDuration(vo['duration'])
        model.battleInfo.setClientArenaIdx(vo['clientArenaIdx'])

    def __fillBaseCaptureInfo(self, model, vo):
        basesModel = model.baseCaptureInfo.getBases()
        basesModel.clear()
        for _, voStat in enumerate(vo['bases']):
            base = BaseInfoModel()
            base.setBaseState(voStat['baseState'])
            base.setBaseLetter(voStat['baseLetter'])
            basesModel.addViewModel(base)

        model.baseCaptureInfo.setTotalPlayerTeamDamage(vo['allyTeamDamage'])
        model.baseCaptureInfo.setTotalEnemyTeamDamage(vo['enemyTeamDamage'])
        isColorBlind = self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        model.baseCaptureInfo.setIsColorBlind(isColorBlind)
        model.baseCaptureInfo.setDuration(vo['arenaDuration'])

    def __isFriend(self, dbID):
        user = self.usersStorage.getUser(dbID)
        if user is None:
            return False
        else:
            tags = user.getTags()
            return user.isFriend() and USER_TAG.SUB_PENDING_OUT not in tags and USER_TAG.SUB_NONE not in tags

    def __isRequestFriendSent(self, dbID):
        user = self.usersStorage.getUser(dbID)
        return False if user is None else USER_TAG.SUB_PENDING_OUT in user.getTags() and user.isFriend()

    def __isRequestSquadSent(self, dbID):
        for invite in self.prbInvites.getInvites(incoming=False):
            if invite.type != PREBATTLE_TYPE.EVENT or dbID != invite.receiverID:
                continue
            return invite.getState() == PRB_INVITE_STATE.PENDING

        return False

    def __isPlayerInSquad(self, dbID):
        return False if not self.platoonCtrl.isInPlatoon() or self.platoonCtrl.getPrbEntityType() != PREBATTLE_TYPE.EVENT else dbID in self.prbEntity.getPlayers()

    def __isPlayerInIgnoreList(self, dbID):
        user = self.usersStorage.getUser(dbID)
        return user is not None and user.isIgnored()

    def __canCreateSquad(self):
        progressCtrl = self._eventController.getHWProgressCtrl()
        result = self.prbEntity.getPermissions().canCreateSquad() and self._eventController.isEnabled() and progressCtrl and not progressCtrl.isPostPhase()
        if self.platoonCtrl.isInPlatoon() and self.platoonCtrl.getPrbEntityType() == PREBATTLE_TYPE.EVENT:
            result = result and self.prbEntity.getPermissions().canSendInvite()
        return result

    def __checkUserStatusUpdate(self, user):
        if user is None:
            return
        else:
            isFriend = self.__isFriend(user.getID())
            isPending = self.__isRequestFriendSent(user.getID())
            isIgnored = user is not None and user.isIgnored()
            with self.viewModel.transaction() as tx:
                for baseTeamMember in (tx.getPlayerTeam(), tx.getEnemyTeam()):
                    for index in xrange(len(baseTeamMember)):
                        member = baseTeamMember.getValue(index)
                        if not member.getPlayerId() == user.getID():
                            continue
                        member.setIsFriendRequestSent(isPending)
                        member.setIsInFriendList(isFriend)
                        member.setIsBlacklisted(isIgnored)

            return

    def __checkFriendOnDelay(self, dbID):
        user = self.usersStorage.getUser(dbID)
        self.__checkUserStatusUpdate(user)

    def __updateMembersStatus(self):
        progressCtrl = self._eventController.getHWProgressCtrl()
        if self._eventController.isEnabled() and progressCtrl and not progressCtrl.isPostPhase():
            return
        with self.viewModel.transaction() as tx:
            for baseTeamMember in (tx.getPlayerTeam(), tx.getEnemyTeam()):
                for index in xrange(len(baseTeamMember)):
                    member = baseTeamMember.getValue(index)
                    member.setIsPlatoonRequestCanBeMade(False)
                    member.setIsPlatoonRequestSent(False)
                    member.setIsPlatoonRequestReceived(False)

    def __setStatusPlatoonRequestSent(self, dbID, state):
        with self.viewModel.transaction() as tx:
            for baseTeamMember in (tx.getPlayerTeam(), tx.getEnemyTeam()):
                for index in xrange(len(baseTeamMember)):
                    member = baseTeamMember.getValue(index)
                    if member.getPlayerId() != dbID:
                        continue
                    member.setIsPlatoonRequestSent(state == PRB_INVITE_STATE.PENDING)
                    member.setIsPlatoonRequestCanBeMade(state != PRB_INVITE_STATE.ACCEPTED)

    def __updateHeader(self, visibility):
        state = HeaderMenuVisibilityState.ALL if visibility else HeaderMenuVisibilityState.NOTHING
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), scope=EVENT_BUS_SCOPE.LOBBY)
