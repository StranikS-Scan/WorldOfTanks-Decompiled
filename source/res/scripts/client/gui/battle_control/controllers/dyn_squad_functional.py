# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/dyn_squad_functional.py
from typing import TYPE_CHECKING
import CommandMapping
import Keys
import Event
import VOIP
from constants import IS_CHINA
from debug_utils import LOG_DEBUG
from gui.app_loader import sf_battle
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.prb_control import prbInvitesProperty
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.utils.key_mapping import getKey, getReadableKey
from helpers import dependency
from messenger.m_constants import USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage
from messenger.proto.shared_messages import ACTION_MESSAGE_TYPE
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus
from gui.shared import EVENT_BUS_SCOPE, events
from skeletons.gui.game_control import IAnonymizerController
from gui.impl.gen import R
from gui.impl import backport
if TYPE_CHECKING:
    from typing import Sequence as TSequence, Tuple as TTuple
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from gui.battle_control.arena_info.arena_dp import ArenaDataProvider
SQUAD_MEMBERS_COUNT = 2
FULL_SQUAD_MEMBERS_COUNT = 3

def _getVIOPState(key):
    voipMgr = VOIP.getVOIPManager()
    if IS_CHINA or not voipMgr.isVoiceSupported():
        return 'withoutVOIP'
    if key == Keys.KEY_NONE:
        return 'specifyVOIP'
    return 'disableVOIP' if voipMgr.isEnabled() and voipMgr.isCurrentChannelEnabled() else 'enableVOIP'


class DynSquadArenaController(object):

    def __init__(self):
        super(DynSquadArenaController, self).__init__()
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onReceivedInviteListModified += self.__onReceivedInviteModified
            invitesManager.onSentInviteListModified += self.__onSentInviteListModified
        self._isBattleLoadingVisible = False
        self.__sentOwnJoinMessage = False
        self.__sentOwnCreateMessage = False
        self.__sentEnemyCreatePlatoons = []
        self.__sentAllyCreatePlatoons = []
        self.__squadMembersAlly = {}
        self.__squadMembersEnemy = {}
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        return

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            guiSessionProvider = dependency.instance(IBattleSessionProvider)
            arenaDP = guiSessionProvider.getArenaDP()
            mySquad = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID()).squadIndex
            myTeams = arenaDP.getAllyTeams()
            if mySquad > 0:
                self.__sentOwnJoinMessage = True
                self.__sentOwnCreateMessage = True
            squadSizes = arenaDP.getSquadSizes()
            otherTeams = arenaDP.getEnemyTeams()
            for myTeam in myTeams:
                for squadIdx, squadSize in squadSizes[myTeam].iteritems():
                    self.__sentAllyCreatePlatoons.append(squadIdx)
                    self.__squadMembersAlly[squadIdx] = squadSize

            for otherTeam in otherTeams:
                for squadIdx, squadSize in squadSizes[otherTeam].iteritems():
                    self.__sentEnemyCreatePlatoons.append(squadIdx)
                    self.__squadMembersEnemy[squadIdx] = squadSize

        self._isBattleLoadingVisible = event.ctx['isShown']

    def process(self, playerVehVO, arenaDP):
        voSquadIndex = playerVehVO.squadIndex
        if voSquadIndex == 0:
            return
        squadMembersCount = arenaDP.getVehiclesCountInPrebattle(playerVehVO.team, playerVehVO.prebattleID)
        myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
        isAlly = arenaDP.isAllyTeam(playerVehVO.team)
        if squadMembersCount == SQUAD_MEMBERS_COUNT:
            if playerVehVO.prebattleID == myAvatarVehicle.prebattleID:
                if myAvatarVehicle.player.isPrebattleCreator:
                    if not self.__sentOwnCreateMessage:
                        self._squadCreatedImOwner(squadNum=voSquadIndex)
                        self.__sentOwnCreateMessage = True
                        self.__squadMembersAlly[voSquadIndex] = squadMembersCount
                elif not self.__sentOwnJoinMessage:
                    self._squadCreatedImRecruit(squadNum=voSquadIndex)
                    self.__sentOwnJoinMessage = True
                    self.__squadMembersAlly[voSquadIndex] = squadMembersCount
            elif isAlly:
                if voSquadIndex not in self.__sentAllyCreatePlatoons:
                    self._squadCreatedByAllies(squadNum=voSquadIndex)
                    self.__sentAllyCreatePlatoons.append(voSquadIndex)
                    self.__squadMembersAlly[voSquadIndex] = squadMembersCount
            elif voSquadIndex not in self.__sentEnemyCreatePlatoons:
                self._squadCreatedByEnemies(squadNum=voSquadIndex)
                self.__sentEnemyCreatePlatoons.append(voSquadIndex)
                self.__squadMembersEnemy[voSquadIndex] = squadMembersCount
        elif isAlly and squadMembersCount != self.__squadMembersAlly.get(voSquadIndex, 0) or not isAlly and squadMembersCount != self.__squadMembersEnemy.get(voSquadIndex, 0):
            playerVO = playerVehVO.player
            if playerVO.accountDBID == myAvatarVehicle.player.accountDBID:
                self._iAmJoinedSquad(squadNum=voSquadIndex)
                self.__squadMembersAlly[voSquadIndex] = squadMembersCount
            elif myAvatarVehicle.team == playerVehVO.team:
                if myAvatarVehicle.squadIndex == voSquadIndex:
                    self._someoneJoinedMySquad(squadNum=voSquadIndex, receiver=playerVO.name)
                else:
                    self._someoneJoinedAlliedSquad(squadNum=voSquadIndex, receiver=playerVO.name)
                self.__squadMembersAlly[voSquadIndex] = squadMembersCount
            else:
                self._someoneJoinedEnemySquad(squadNum=voSquadIndex, receiver=playerVO.name)
                self.__squadMembersEnemy[voSquadIndex] = squadMembersCount

    def destroy(self):
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteModified
            invitesManager.onSentInviteListModified -= self.__onSentInviteListModified
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        return

    def _inviteReceived(self, invite):
        LOG_DEBUG('Handler: Invite received', invite)

    def _inviteSent(self, invite):
        LOG_DEBUG('Handler: Invite sent', invite)

    def _squadCreatedImOwner(self, squadNum):
        LOG_DEBUG('Handler: Squad created by myself, Squad Number = ', squadNum)

    def _squadCreatedImRecruit(self, squadNum):
        LOG_DEBUG("Handler: Squad created and I'm not commander, Squad Number = ", squadNum)

    def _squadCreatedByAllies(self, squadNum):
        LOG_DEBUG('Handler: Allies created new squad: Squad number = ', squadNum)

    def _squadCreatedByEnemies(self, squadNum):
        LOG_DEBUG('Handler: Enemies created new squad: Squad number = ', squadNum)

    def _iAmJoinedSquad(self, squadNum):
        LOG_DEBUG("Handler: I'm just have joined the squad: Squad number = ", squadNum)

    def _someoneJoinedAlliedSquad(self, squadNum, receiver):
        LOG_DEBUG('Handler: Someone just have joined Allied squad: Squad Number, receiver = ', squadNum, receiver)

    def _someoneJoinedEnemySquad(self, squadNum, receiver):
        LOG_DEBUG('Handler: Someone just have joined Enemy squad: Squad Number, receiver = ', squadNum, receiver)

    def _someoneJoinedMySquad(self, squadNum, receiver):
        LOG_DEBUG('Handler: Someone just have joined MY squad: Squad Number, receiver = ', squadNum, receiver)

    def __onReceivedInviteModified(self, added, changed, deleted):
        self.__handleModifiedInvitesList(added, changed, deleted, self.prbInvites.getReceivedInvites, self._inviteReceived)

    def __onSentInviteListModified(self, added, changed, deleted):
        self.__handleModifiedInvitesList(added, changed, deleted, self.prbInvites.getSentInvites, self._inviteSent)

    def __handleModifiedInvitesList(self, added, changed, deleted, inviteDataReceiver, callback):
        allChangedInvites = set(added) | set(changed) | set(deleted)
        arenaUniqueID = avatar_getter.getArenaUniqueID()
        if allChangedInvites:
            for invite in inviteDataReceiver(allChangedInvites):
                if invite.isSameBattle(arenaUniqueID) and invite.isActive():
                    callback(invite)


class DYN_SQUAD_TYPE(object):
    OWN = 0
    ALLY = 1
    ENEMY = 2


class _DynSquadActionMessage(ClientActionMessage):

    def __init__(self, message, squadType, squadNum):
        ClientActionMessage.__init__(self, msg=message, type_=ACTION_MESSAGE_TYPE.WARNING)
        self.__squadType = squadType
        self.__squadNum = squadNum

    @property
    def squadType(self):
        return self.__squadType

    @property
    def squadNum(self):
        return self.__squadNum


_R_DYN_SQUAD = R.strings.messenger.client.dynSquad

class DynSquadMessagesController(DynSquadArenaController):

    @dependency.replace_none_kwargs(ctrl=IAnonymizerController)
    def _inviteReceived(self, invite, ctrl=None):
        self.__sendMessage(_R_DYN_SQUAD.inviteReceived if not ctrl.isAnonymized else _R_DYN_SQUAD.inviteReceived.anonymized, creator=invite.creator)

    def _inviteSent(self, invite):
        self.__sendMessage(_R_DYN_SQUAD.inviteSent, receiver=invite.receiver)

    def _squadCreatedImOwner(self, squadNum):
        self.__sendMessage(_R_DYN_SQUAD.created.owner.dyn(self.__getState(CommandMapping.CMD_VOICECHAT_ENABLE)), squadNum=squadNum, keyName=getReadableKey(CommandMapping.CMD_VOICECHAT_ENABLE))

    def _squadCreatedImRecruit(self, squadNum):
        self.__sendMessage(_R_DYN_SQUAD.created.recruit.dyn(self.__getState(CommandMapping.CMD_VOICECHAT_ENABLE)), squadNum=squadNum, keyName=getReadableKey(CommandMapping.CMD_VOICECHAT_ENABLE))

    def _squadCreatedByAllies(self, squadNum):
        self.__sendMessage(_R_DYN_SQUAD.created.allies, squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ALLY)

    def _squadCreatedByEnemies(self, squadNum):
        self.__sendMessage(_R_DYN_SQUAD.created.enemies, squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ENEMY)

    def _iAmJoinedSquad(self, squadNum):
        self.__sendMessage(_R_DYN_SQUAD.inviteAccepted.myself.dyn(self.__getState(CommandMapping.CMD_VOICECHAT_ENABLE)), squadNum=squadNum, keyName=getReadableKey(CommandMapping.CMD_VOICECHAT_ENABLE))

    def _someoneJoinedAlliedSquad(self, squadNum, receiver):
        self.__sendMessage(_R_DYN_SQUAD.inviteAccepted.user, squadNum=squadNum, receiver=receiver, squadType=DYN_SQUAD_TYPE.ALLY)

    def _someoneJoinedMySquad(self, squadNum, receiver):
        self.__sendMessage(_R_DYN_SQUAD.inviteAccepted.user, squadNum=squadNum, receiver=receiver)

    def __sendMessage(self, resource, **kwargs):
        g_messengerEvents.onWarningReceived(_DynSquadActionMessage(backport.text(resource(), **kwargs), kwargs.get('squadType', DYN_SQUAD_TYPE.OWN), kwargs.get('squadNum')))

    def __getState(self, command):
        return _getVIOPState(getKey(command))


_DYN_SQUAD_PLATOON_JOINED = 'dyn_squad_platoon_joined'
_DYN_SQUAD_PLATOON_CREATED = 'dyn_squad_platoon_created'
_DYN_SQUAD_PLATOON_DISMISSED = 'dyn_squad_platoon_dismissed'
_DYN_SQUAD_BEEN_EXCLUDED_PLATOON = 'dyn_squad_been_excluded_platoon'
_DYN_SQUAD_LEFT_PLATOON = 'dyn_squad_left_platoon'
_DYN_SQUAD_ASSISTANCE_BEEN_REQUESTED = 'dyn_squad_assistance_been_requested'
_DYN_SQUAD_PLAYER_JOINED_PLATOON = 'dyn_squad_player_joined_platoon'

class _DynSquadSoundsController(DynSquadArenaController):
    __slots__ = ()

    @sf_battle
    def app(self):
        return None

    def _squadCreatedImOwner(self, squadNum):
        self.__playSound(_DYN_SQUAD_PLATOON_CREATED)

    def _squadCreatedImRecruit(self, squadNum):
        self.__playSound(_DYN_SQUAD_PLATOON_CREATED)

    def _inviteReceived(self, invite):
        self.__playSound(_DYN_SQUAD_ASSISTANCE_BEEN_REQUESTED)

    def _iAmJoinedSquad(self, squadNum):
        self.__playSound(_DYN_SQUAD_PLATOON_JOINED)

    def _someoneJoinedMySquad(self, squadNum, receiver):
        self.__playSound(_DYN_SQUAD_PLAYER_JOINED_PLATOON)

    def __playSound(self, sound):
        if self._isBattleLoadingVisible:
            return
        else:
            app = self.app
            if app is not None and app.soundManager is not None:
                app.soundManager.playEffectSound(SoundEffectsId.DYN_SQUAD_STARTING_DYNAMIC_PLATOON)
            notifications = avatar_getter.getSoundNotifications()
            if notifications is not None and hasattr(notifications, 'play'):
                notifications.play(sound)
            return


class DynSquadFunctional(IArenaVehiclesController):
    __slots__ = ('__soundCtrl', '__msgsCtrl', '__eManager', '__wasOwnSquadCreated', 'onDynSquadCreatedOrJoined')

    def __init__(self, setup):
        super(DynSquadFunctional, self).__init__()
        self.__soundCtrl = _DynSquadSoundsController()
        self.__msgsCtrl = DynSquadMessagesController()
        self.__eManager = Event.EventManager()
        if setup.isReplayPlaying:
            g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.IGNORED_TMP})
        self.__wasOwnSquadCreated = False
        self.onDynSquadCreatedOrJoined = Event.Event(self.__eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.DYN_SQUADS

    def stopControl(self):
        if self.__soundCtrl is not None:
            self.__soundCtrl.destroy()
            self.__soundCtrl = None
        if self.__msgsCtrl is not None:
            self.__msgsCtrl.destroy()
            self.__msgsCtrl = None
        self.__eManager.clear()
        self.__wasOwnSquadCreated = False
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        if updated:
            playerVehVO = updated[0][1]
            self.__soundCtrl.process(playerVehVO, arenaDP)
            self.__msgsCtrl.process(playerVehVO, arenaDP)
            self.__checkIfAccountCreatedOrJoinedDynSquad(playerVehVO, arenaDP)

    def __checkIfAccountCreatedOrJoinedDynSquad(self, playerVehVO, arenaDP):
        voSquadIndex = playerVehVO.squadIndex
        if voSquadIndex == 0 or self.__wasOwnSquadCreated:
            return
        myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
        if playerVehVO.prebattleID == myAvatarVehicle.prebattleID:
            self.__wasOwnSquadCreated = True
            self.onDynSquadCreatedOrJoined(myAvatarVehicle.player.isPrebattleCreator, myAvatarVehicle.prebattleID)
