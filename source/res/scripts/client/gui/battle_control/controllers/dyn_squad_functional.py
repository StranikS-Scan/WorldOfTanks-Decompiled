# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/dyn_squad_functional.py
import BigWorld
import CommandMapping
import Keys
from account_helpers.settings_core import g_settingsCore
from account_helpers.settings_core.settings_constants import SOUND
from constants import IS_CHINA
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.app_loader.decorators import sf_battle
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.prb_control.prb_helpers import prbInvitesProperty
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers.i18n import makeString
from messenger.m_constants import USER_TAG
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage
from messenger.proto.shared_messages import ACTION_MESSAGE_TYPE
SQUAD_MEMBERS_COUNT = 2
FULL_SQUAD_MEMBERS_COUNT = 3

def _getKey(command):
    """Get bigworld's keyboard key assigned to the provided command
    """
    commandName = CommandMapping.g_instance.getName(command)
    return CommandMapping.g_instance.get(commandName)


def _getVIOPState(key):
    """Get the current state of VOIP in the client considering bind key, region and VOIP settings.
    """
    if IS_CHINA:
        return 'withoutVOIP'
    elif key == Keys.KEY_NONE:
        return 'specifyVOIP'
    elif g_settingsCore.getSetting(SOUND.VOIP_ENABLE):
        return 'disableVOIP'
    else:
        return 'enableVOIP'


def _getReadableKey(key):
    """Get a human readable key name.
    """
    return makeString(READABLE_KEY_NAMES.all('KEY_%s' % BigWorld.keyToString(key)))


class DynSquadArenaController(object):

    def __init__(self):
        super(DynSquadArenaController, self).__init__()
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified += self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified += self.__onSentInviteListModified

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def process(self, playerVehVO, arenaDP):
        voSquadIndex = playerVehVO.squadIndex
        squadMembersCount = arenaDP.getVehiclesCountInPrebattle(playerVehVO.team, playerVehVO.prebattleID)
        if squadMembersCount == SQUAD_MEMBERS_COUNT:
            myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
            if playerVehVO.prebattleID == myAvatarVehicle.prebattleID:
                if myAvatarVehicle.player.isPrebattleCreator:
                    self._squadCreatedImOwner(squadNum=voSquadIndex)
                else:
                    self._squadCreatedImRecruit(squadNum=voSquadIndex)
            elif myAvatarVehicle.team == playerVehVO.team:
                self._squadCreatedByAllies(squadNum=voSquadIndex)
            else:
                self._squadCreatedByEnemies(squadNum=voSquadIndex)
        elif squadMembersCount == FULL_SQUAD_MEMBERS_COUNT:
            myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
            playerVO = playerVehVO.player
            if playerVO.accountDBID == myAvatarVehicle.player.accountDBID:
                self._iAmJoinedSquad(squadNum=voSquadIndex)
            elif myAvatarVehicle.team == playerVehVO.team:
                if myAvatarVehicle.squadIndex == voSquadIndex:
                    self._someoneJoinedMySquad(squadNum=voSquadIndex, receiver=playerVO.name)
                else:
                    self._someoneJoinedAlliedSquad(squadNum=voSquadIndex, receiver=playerVO.name)
            else:
                self._someoneJoinedEnemySquad(squadNum=voSquadIndex, receiver=playerVO.name)

    def destroy(self):
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified -= self.__onSentInviteListModified

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
        if len(allChangedInvites) > 0:
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


class DynSquadMessagesController(DynSquadArenaController):

    def __init__(self):
        super(DynSquadMessagesController, self).__init__()

    def _inviteReceived(self, invite):
        self.__sendMessage('#messenger:client/dynSquad/inviteReceived', creator=invite.creator)

    def _inviteSent(self, invite):
        self.__sendMessage('#messenger:client/dynSquad/inviteSent', receiver=invite.receiver)

    def _squadCreatedImOwner(self, squadNum):
        key = _getKey(CommandMapping.CMD_VOICECHAT_ENABLE)
        state = _getVIOPState(key)
        message = '#messenger:client/dynSquad/created/owner/%s' % state
        self.__sendMessage(message, squadNum=squadNum, keyName=_getReadableKey(key))

    def _squadCreatedImRecruit(self, squadNum):
        key = _getKey(CommandMapping.CMD_VOICECHAT_ENABLE)
        state = _getVIOPState(key)
        message = '#messenger:client/dynSquad/created/recruit/%s' % state
        self.__sendMessage(message, squadNum=squadNum, keyName=_getReadableKey(key))

    def _squadCreatedByAllies(self, squadNum):
        self.__sendMessage('#messenger:client/dynSquad/created/allies', squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ALLY)

    def _squadCreatedByEnemies(self, squadNum):
        self.__sendMessage('#messenger:client/dynSquad/created/enemies', squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ENEMY)

    def _iAmJoinedSquad(self, squadNum):
        key = _getKey(CommandMapping.CMD_VOICECHAT_ENABLE)
        state = _getVIOPState(key)
        message = '#messenger:client/dynSquad/inviteAccepted/myself/%s' % state
        self.__sendMessage(message, squadNum=squadNum, keyName=_getReadableKey(key))

    def _someoneJoinedAlliedSquad(self, squadNum, receiver):
        self.__sendMessage('#messenger:client/dynSquad/inviteAccepted/user', squadNum=squadNum, receiver=receiver, squadType=DYN_SQUAD_TYPE.ALLY)

    def _someoneJoinedMySquad(self, squadNum, receiver):
        self.__sendMessage('#messenger:client/dynSquad/inviteAccepted/user', squadNum=squadNum, receiver=receiver)

    def destroy(self):
        super(DynSquadMessagesController, self).destroy()

    def __sendMessage(self, key, **kwargs):
        message = makeString(key, **kwargs)
        g_messengerEvents.onWarningReceived(_DynSquadActionMessage(message, kwargs.get('squadType', DYN_SQUAD_TYPE.OWN), kwargs.get('squadNum')))


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
        app = self.app
        if app is not None and app.soundManager is not None:
            app.soundManager.playEffectSound(SoundEffectsId.DYN_SQUAD_STARTING_DYNAMIC_PLATOON)
        notifications = avatar_getter.getSoundNotifications()
        if notifications is not None and hasattr(notifications, 'play'):
            notifications.play(sound)
        return


class DynSquadFunctional(IArenaVehiclesController):
    __slots__ = ('__soundCtrl', '__msgsCtrl')

    def __init__(self, setup):
        super(DynSquadFunctional, self).__init__()
        self.__soundCtrl = _DynSquadSoundsController()
        self.__msgsCtrl = DynSquadMessagesController()
        if setup.isReplayPlaying:
            g_messengerEvents.users.onUsersListReceived({USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.IGNORED_TMP})

    def getControllerID(self):
        return BATTLE_CTRL_ID.DYN_SQUADS

    def stopControl(self):
        if self.__soundCtrl is not None:
            self.__soundCtrl.destroy()
            self.__soundCtrl = None
        if self.__msgsCtrl is not None:
            self.__msgsCtrl.destroy()
            self.__msgsCtrl = None
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        """Vehicle has been updated on arena. Updates required player's panel, frags panel.
        """
        if updated:
            first = updated[0][1]
            self.__soundCtrl.process(first, arenaDP)
            self.__msgsCtrl.process(first, arenaDP)
