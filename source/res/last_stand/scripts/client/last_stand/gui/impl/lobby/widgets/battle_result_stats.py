# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/battle_result_stats.py
import logging
from adisp import adisp_process
from constants import DEATH_REASON_ALIVE
from frameworks.wulf import ViewFlags, ViewSettings, WindowStatus
from gui.impl.backport import createContextMenuData, BackportContextMenuWindow
from gui.prb_control import prbInvitesProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from last_stand.gui.impl.gen.view_models.views.common.stat_column_settings_model import ColumnEnum
from last_stand.gui.impl.gen.view_models.views.battle.event_stats_view_model import EventStatsViewModel
from last_stand.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberBanType
from last_stand.gui.impl.gen.view_models.views.battle.event_stats_team_member_model import EventStatsTeamMemberModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from last_stand.gui.scaleform.genConsts.LS_CM_HANDLER_TYPE import LS_CM_HANDLER_TYPE
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
from messenger.m_constants import UserEntityScope, USER_TAG, PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.entities import SharedUserEntity
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IPlatoonController
from messenger.proto.entities import ClanInfo as UserClanInfo
from gui.prb_control.settings import PRB_INVITE_STATE
from last_stand.gui.ls_gui_constants import PREBATTLE_ACTION_NAME
from last_stand_common.last_stand_constants import PREBATTLE_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from helpers.CallbackDelayer import CallbackDelayer
_CHECK_FRIEND_TIMEOUT = 5.0
_DEFAULT_CONTEXT_MENU_PLAYER_ID = -1
_logger = logging.getLogger(__name__)

class BattleResultStats(ViewImpl, IGlobalListener, CallbackDelayer):
    battleResults = dependency.descriptor(IBattleResultsService)
    platoonCtrl = dependency.descriptor(IPlatoonController)
    lsCtrl = dependency.descriptor(ILSController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, arenaUniqueID, flags=ViewFlags.VIEW, *args, **kwargs):
        settings = ViewSettings(layoutID=R.aliases.last_stand.shared.TeamStats(), flags=flags, model=EventStatsViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__arenaUniqueID = arenaUniqueID
        self.__contextMenuWindow = None
        super(BattleResultStats, self).__init__(settings)
        return

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            dbID = event.getArgument('playerId')
            contextMenuArgs = {'dbID': dbID,
             'userName': event.getArgument('userName'),
             'clanAbbrev': event.getArgument('clanAbbrev'),
             'vehicleCD': event.getArgument('vehicleCD'),
             'isAlly': True,
             'clientArenaIdx': self.lobbyContext.getClientIDByArenaUniqueID(self.__arenaUniqueID),
             'wasInBattle': True}
            contextMenuData = createContextMenuData(LS_CM_HANDLER_TYPE.LS_BATTLE_RESULTS, contextMenuArgs)
            self.__contextMenuWindow = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            self.__contextMenuWindow.onStatusChanged += self.__onStatusChangedContextMenu
            self.__contextMenuWindow.load()
            with self.viewModel.transaction() as tx:
                tx.setContextMenuPlayerId(dbID)
            return self.__contextMenuWindow
        return super(BattleResultStats, self).createContextMenu(event)

    @property
    def viewModel(self):
        return super(BattleResultStats, self).getViewModel()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def _finalize(self):
        CallbackDelayer.destroy(self)
        self._removeEventListeners()
        self.__contextMenuWindow = None
        super(BattleResultStats, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(BattleResultStats, self)._onLoading(*args, **kwargs)
        self._addEventListeners()
        self.__updateView()

    def _onUserActionReceived(self, _, user, __):
        self.__checkUserStatusUpdate(user)

    def _onUserStatusUpdated(self, user):
        self.__checkUserStatusUpdate(user)

    def _addEventListeners(self):
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated += self._onUserStatusUpdated
        self.viewModel.onSendFriendRequest += self._sendFriendRequest
        self.viewModel.onSendPlatoonInvitation += self._sendPlatoonInvitation
        self.viewModel.onRemoveFromBlacklist += self._removeFromBlacklist
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified += self._onSentInviteListModified
        self.platoonCtrl.onMembersUpdate += self._onMembersSquadUpdate
        return

    def _removeEventListeners(self):
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated -= self._onUserStatusUpdated
        self.viewModel.onSendFriendRequest -= self._sendFriendRequest
        self.viewModel.onSendPlatoonInvitation -= self._sendPlatoonInvitation
        self.viewModel.onRemoveFromBlacklist -= self._removeFromBlacklist
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified -= self._onSentInviteListModified
        self.platoonCtrl.onMembersUpdate -= self._onMembersSquadUpdate
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
        if not (args and self.lsCtrl.isAvailable()):
            return
        dbID = args.get('playerId')
        if not dbID:
            return
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.LAST_STAND_SQUAD, accountsToInvite=[int(dbID)], extData={'arenaUniqueID': self.__arenaUniqueID}))

    def _removeFromBlacklist(self, args=None):
        if not args:
            return
        dbID = args.get('playerId')
        if not dbID:
            return
        self.proto.contacts.removeIgnored(dbID)

    def _onSentInviteListModified(self, added, changed, deleted):
        if not self.lsCtrl.isAvailable():
            return
        allChangedInvites = set(added) | set(changed) | set(deleted)
        for inviteID in allChangedInvites:
            invite = self.prbInvites.getInvite(inviteID)
            if not invite or invite.type != PREBATTLE_TYPE.LAST_STAND:
                continue
            dbID = invite.receiverID
            state = invite.getState()
            self.__setStatusPlatoonRequestSent(dbID, state)

    def _onMembersSquadUpdate(self):
        with self.viewModel.transaction() as tx:
            self.__fillViewModel(model=tx)

    def __onStatusChangedContextMenu(self, windowStatus):
        if windowStatus == WindowStatus.DESTROYED:
            with self.viewModel.transaction() as tx:
                tx.setContextMenuPlayerId(_DEFAULT_CONTEXT_MENU_PLAYER_ID)
            self.__contextMenuWindow.onStatusChanged -= self.__onStatusChangedContextMenu
            self.__contextMenuWindow = None
        return

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
        for invite in self.prbInvites.getInvites(incoming=False, onlyActive=True):
            if invite.type != PREBATTLE_TYPE.LAST_STAND or dbID != invite.receiverID:
                continue
            return invite.getState() == PRB_INVITE_STATE.PENDING

        return False

    def __isPlayerInSquad(self, dbID):
        return False if not self.platoonCtrl.isInPlatoon() or self.platoonCtrl.getPrbEntityType() != PREBATTLE_TYPE.LAST_STAND else dbID in self.prbEntity.getPlayers()

    def __isPlayerInIgnoreList(self, dbID):
        user = self.usersStorage.getUser(dbID)
        return user is not None and user.isIgnored()

    def __canCreateSquad(self):
        result = self.prbEntity.getPermissions().canCreateSquad() and self.lsCtrl.isAvailable()
        if self.platoonCtrl.isInPlatoon() and self.platoonCtrl.getPrbEntityType() == PREBATTLE_TYPE.LAST_STAND:
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
                for member in tx.getTeam():
                    if not member.getPlayerId() == user.getID():
                        continue
                    member.setIsFriendRequestSent(isPending)
                    member.setIsInFriendList(isFriend)
                    member.setIsBlacklisted(isIgnored)

            return

    def __setStatusPlatoonRequestSent(self, dbID, state):
        with self.viewModel.transaction() as tx:
            for member in tx.getTeam():
                if member.getPlayerId() != dbID:
                    continue
                member.setIsPlatoonRequestSent(state == PRB_INVITE_STATE.PENDING)
                member.setIsPlatoonRequestCanMade(state != PRB_INVITE_STATE.ACCEPTED)
                member.setIsPlatoonRequestInSquad(self.__isPlayerInSquad(dbID))

    def __checkFriendOnDelay(self, dbID):
        user = self.usersStorage.getUser(dbID)
        self.__checkUserStatusUpdate(user)

    def __setColumns(self, model=None):
        columns = model.columnSettings.getVisibleColumns()
        columns.clear()
        columns.addString(ColumnEnum.PLACE.value)
        columns.addString(ColumnEnum.DAMAGE.value)
        columns.addString(ColumnEnum.KILLS.value)
        columns.addString(ColumnEnum.KEYS.value)
        columns.invalidate()

    def __makeTeamMemberModel(self, idx, playerVO):
        member = EventStatsTeamMemberModel()
        dbID = playerVO['playerDBID']
        member.setId(idx)
        member.setPlayerId(dbID)
        member.setIsCurrentPlayer(playerVO['isPlayer'])
        member.setIsOwnSquad(playerVO['isPlayer'] or playerVO['isOwnSquad'])
        member.setSquadNum(playerVO['squadID'])
        member.setBanType(TeamMemberBanType.NOTBANNED)
        member.setIsFriendRequestSent(self.__isRequestFriendSent(dbID))
        member.setIsInFriendList(self.__isFriend(dbID))
        member.setIsPlatoonRequestCanMade(self.__canCreateSquad())
        member.setIsPlatoonRequestInSquad(self.__isPlayerInSquad(dbID))
        member.setIsPlatoonRequestSent(self.__isRequestSquadSent(dbID))
        member.setIsBlacklisted(self.__isPlayerInIgnoreList(dbID))
        member.stats.setPlace(idx + 1)
        member.stats.setDamage(playerVO['damageDealt'])
        member.stats.setKeys(playerVO['artefactKeys'])
        member.stats.setKills(playerVO['kills'])
        member.setIsAlive(playerVO['deathReason'] == DEATH_REASON_ALIVE)
        member.user.setUserName(playerVO['playerName'])
        member.user.setClanAbbrev(playerVO['clanAbbrev'])
        member.user.setIsFakeNameVisible(False)
        badgeID = playerVO['badgeID']
        member.user.badge.setBadgeID(str(badgeID) if badgeID != 0 else '')
        badgeSuffixID = playerVO['badgeSuffixID']
        member.user.suffixBadge.setBadgeID(str(badgeSuffixID) if badgeSuffixID != 0 else '')
        member.vehicle.setVehicleName(playerVO['vehicleName'])
        member.vehicle.setVehicleShortName(playerVO['vehicleShortName'])
        member.vehicle.setVehicleType(playerVO['vehicleType'])
        member.vehicle.setVehicleLvl(playerVO['vehicleLvl'])
        member.vehicle.setVehicleCD(playerVO['vehicleCD'])
        if playerVO.get('vehicleIsIGR', False):
            member.vehicle.setTags(VEHICLE_TAGS.PREMIUM_IGR)
        return member

    def __fillViewModel(self, model):
        totalVO = self.battleResults.getResultsVO(self.__arenaUniqueID)
        teamModel = model.getTeam()
        teamModel.clear()
        for idx, playerVO in enumerate(totalVO['players']):
            member = self.__makeTeamMemberModel(idx, playerVO)
            teamModel.addViewModel(member)

        teamModel.invalidate()

    def __updateView(self):
        with self.viewModel.transaction() as tx:
            self.__setColumns(model=tx)
            self.__fillViewModel(model=tx)
