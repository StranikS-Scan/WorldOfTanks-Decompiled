# Embedded file name: scripts/client/gui/battle_control/dyn_squad_functional.py
from account_helpers.settings_core import g_settingsCore
from account_helpers.settings_core.settings_constants import SOUND
from constants import ARENA_GUI_TYPE, IS_CHINA
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.battle_control import avatar_getter, arena_info
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control.prb_helpers import prbInvitesProperty
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers.i18n import makeString
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage, ACTION_MESSAGE_TYPE
SQUAD_MEMBERS_COUNT = 2
FULL_SQUAD_MEMBERS_COUNT = 3

class IDynSquadEntityClient(object):

    def updateSquadmanVeh(self, vehID):
        raise NotImplementedError, 'This method invokes by DynSquadEntityController it must be implemented %s' % self


class _DynSquadEntityController(IArenaVehiclesController):
    __slots__ = ('__clients',)

    def __init__(self, clients):
        super(_DynSquadEntityController, self).__init__()
        self.__clients = clients

    def setBattleCtx(self, battleCtx):
        pass

    def invalidateVehicleInfo(self, flags, playerVehVO, arenaDP):
        if arena_info.getArenaGuiType == ARENA_GUI_TYPE.RANDOM:
            if flags & INVALIDATE_OP.PREBATTLE_CHANGED and playerVehVO.squadIndex > 0:
                vID = playerVehVO.vehicleID
                squadMansToUpdate = ()
                avatarVehID = avatar_getter.getPlayerVehicleID()
                aVehInfo = arenaDP.getVehicleInfo(avatarVehID)
                if vID == avatarVehID:
                    squadMansToUpdate = arenaDP.getVehIDsByPrebattleID(aVehInfo.team, aVehInfo.prebattleID) or tuple()
                    if avatarVehID in squadMansToUpdate:
                        del squadMansToUpdate[squadMansToUpdate.index(avatarVehID)]
                elif aVehInfo.team == playerVehVO.team:
                    if arenaDP.isSquadMan(vID):
                        squadMansToUpdate = (vID,)
                for sqVehID in squadMansToUpdate:
                    for client in self.__clients:
                        client.updateSquadmanVeh(sqVehID)

    def destroy(self):
        self.__clients = None
        return


class DynSquadArenaController(IArenaVehiclesController):

    def __init__(self):
        super(DynSquadArenaController, self).__init__()
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified += self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified += self.__onSentInviteListModified

    def setBattleCtx(self, battleCtx):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def invalidateVehicleInfo(self, flags, playerVehVO, arenaDP):
        voSquadIndex = playerVehVO.squadIndex
        if flags & INVALIDATE_OP.PREBATTLE_CHANGED and voSquadIndex > 0:
            squadMembersCount = arenaDP.getPrbVehCount(playerVehVO.team, playerVehVO.prebattleID)
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
        self.__sendMessage(makeString(MESSENGER.CLIENT_DYNSQUAD_INVITERECEIVED, creator=invite.creator))

    def _inviteSent(self, invite):
        self.__sendMessage(makeString(MESSENGER.CLIENT_DYNSQUAD_INVITESENT, receiver=invite.receiver))

    def _squadCreatedImOwner(self, squadNum):
        param = {'squadNum': squadNum}
        if IS_CHINA:
            key = MESSENGER.CLIENT_DYNSQUAD_CREATED_OWNER_WITHOUTVOIP
        else:
            key = '#messenger:client/dynSquad/created/owner/disableVOIP' if g_settingsCore.getSetting(SOUND.VOIP_ENABLE) else '#messenger:client/dynSquad/created/owner/enableVOIP'
            param['hotkey'] = 'ALT+Q'
        self.__sendMessage(key, **param)

    def _squadCreatedImRecruit(self, squadNum):
        param = {'squadNum': squadNum}
        if IS_CHINA:
            key = MESSENGER.CLIENT_DYNSQUAD_CREATED_RECRUIT_WITHOUTVOIP
        else:
            key = '#messenger:client/dynSquad/created/recruit/disableVOIP' if g_settingsCore.getSetting(SOUND.VOIP_ENABLE) else '#messenger:client/dynSquad/created/owner/enableVOIP'
            param['hotkey'] = 'ALT+Q'
        self.__sendMessage(key, **param)

    def _squadCreatedByAllies(self, squadNum):
        self.__sendMessage(MESSENGER.CLIENT_DYNSQUAD_CREATED_ALLIES, squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ALLY)

    def _squadCreatedByEnemies(self, squadNum):
        self.__sendMessage(MESSENGER.CLIENT_DYNSQUAD_CREATED_ENEMIES, squadNum=squadNum, squadType=DYN_SQUAD_TYPE.ENEMY)

    def _iAmJoinedSquad(self, squadNum):
        param = {'squadNum': squadNum}
        if IS_CHINA:
            key = MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_MYSELF_WITHOUTVOIP
        else:
            key = '#messenger:client/dynSquad/inviteAccepted/myself/disableVOIP' if g_settingsCore.getSetting(SOUND.VOIP_ENABLE) else '#messenger:client/dynSquad/inviteAccepted/myself/enableVOIP'
            param['hotkey'] = 'ALT+Q'
        self.__sendMessage(key, **param)

    def _someoneJoinedAlliedSquad(self, squadNum, receiver):
        self.__sendMessage(MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_USER, squadNum=squadNum, receiver=receiver, squadType=DYN_SQUAD_TYPE.ALLY)

    def _someoneJoinedMySquad(self, squadNum, receiver):
        self.__sendMessage(MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_USER, squadNum=squadNum, receiver=receiver)

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
    __slots__ = ('__soundManager',)

    def __init__(self, soundMgr):
        super(_DynSquadSoundsController, self).__init__()
        self.__soundManager = soundMgr

    def destroy(self):
        super(_DynSquadSoundsController, self).destroy()
        self.__soundManager = None
        return

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
        self.__soundManager.playSound('effects.%s' % SoundEffectsId.DYN_SQUAD_STARTING_DYNAMIC_PLATOON)
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(sound)


class DynSquadFunctional(object):

    def __init__(self):
        super(DynSquadFunctional, self).__init__()
        self.__soundCtrl = None
        self.__entitiesCtrl = None
        self.__msgsCtrl = None
        self.__inited = False
        return

    def setUI(self, battleUI, sessionProviderRef):
        self.__soundCtrl = _DynSquadSoundsController(battleUI.soundManager)
        sessionProviderRef.addArenaCtrl(self.__soundCtrl)
        self.__entitiesCtrl = _DynSquadEntityController((battleUI.minimap, battleUI.markersManager))
        sessionProviderRef.addArenaCtrl(self.__entitiesCtrl)
        self.__msgsCtrl = DynSquadMessagesController()
        sessionProviderRef.addArenaCtrl(self.__msgsCtrl)
        self.__inited = True

    def clearUI(self, sessionProviderRef):
        if self.__inited:
            sessionProviderRef.removeArenaCtrl(self.__soundCtrl)
            self.__soundCtrl.destroy()
            sessionProviderRef.removeArenaCtrl(self.__entitiesCtrl)
            self.__entitiesCtrl.destroy()
            sessionProviderRef.removeArenaCtrl(self.__msgsCtrl)
            self.__msgsCtrl.destroy()
            self.__soundCtrl = None
            self.__entitiesCtrl = None
            self.__msgsCtrl = None
        self.__inited = False
        return
