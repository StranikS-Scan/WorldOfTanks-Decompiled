# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/player_menu_handler.py
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import USER
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import UserContextMenuInfo
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS as _D_STATUS
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.denunciator import DENUNCIATIONS, BattleDenunciator, DENUNCIATIONS_MAP
from helpers import dependency
from helpers import i18n
from constants import DENUNCIATIONS_PER_DAY
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from skeletons.gui.battle_session import IBattleSessionProvider

class DYN_SQUAD_OPTION_ID(object):
    SENT_INVITATION = 'sendInvitationToSquad'
    ACCEPT_INVITATION = 'acceptInvitationToSquad'
    REJECT_INVITATION = 'rejectInvitationToSquad'
    IN_SQUAD = 'inSquad'


class BATTLE_CHAT_OPTION_ID(object):
    ENABLE_COMMUNICATIONS = 'enableCommunications'
    DISABLE_COMMUNICATIONS = 'disableCommunications'


_OPTIONS_HANDLERS = {USER.ADD_TO_FRIENDS: 'addFriend',
 USER.REMOVE_FROM_FRIENDS: 'removeFriend',
 USER.ADD_TO_IGNORED: 'setIgnored',
 USER.REMOVE_FROM_IGNORED: 'unsetIgnored',
 BATTLE_CHAT_OPTION_ID.ENABLE_COMMUNICATIONS: 'enableCommunications',
 BATTLE_CHAT_OPTION_ID.DISABLE_COMMUNICATIONS: 'disableCommunications',
 USER.SET_MUTED: 'setMuted',
 USER.UNSET_MUTED: 'unsetMuted',
 DENUNCIATIONS.INCORRECT_BEHAVIOR: 'appealIncorrectBehavior',
 DENUNCIATIONS.NOT_FAIR_PLAY: 'appealNotFairPlay',
 DENUNCIATIONS.FORBIDDEN_NICK: 'appealForbiddenNick',
 DENUNCIATIONS.BOT: 'appealBot',
 DYN_SQUAD_OPTION_ID.SENT_INVITATION: 'sendInvitation',
 DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION: 'acceptInvitation',
 DYN_SQUAD_OPTION_ID.REJECT_INVITATION: 'rejectInvitation'}
_OPTION_ICONS = {USER.ADD_TO_FRIENDS: 'addToFriends',
 USER.REMOVE_FROM_FRIENDS: 'removeFromFriends',
 USER.ADD_TO_IGNORED: 'addToBlacklist',
 USER.REMOVE_FROM_IGNORED: 'removeFromBlacklist',
 BATTLE_CHAT_OPTION_ID.ENABLE_COMMUNICATIONS: 'enableCommunications',
 BATTLE_CHAT_OPTION_ID.DISABLE_COMMUNICATIONS: 'disableCommunications',
 USER.SET_MUTED: 'disableVoice',
 USER.UNSET_MUTED: 'enableVoice',
 DYN_SQUAD_OPTION_ID.SENT_INVITATION: 'addToSquad',
 DYN_SQUAD_OPTION_ID.IN_SQUAD: 'inSquad',
 DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION: 'acceptInvitation',
 DYN_SQUAD_OPTION_ID.REJECT_INVITATION: 'rejectInvitation'}

class PlayerContextMenuInfo(UserContextMenuInfo):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, databaseID, userName):
        super(PlayerContextMenuInfo, self).__init__(databaseID, userName)
        self.isAlly = self.sessionProvider.getCtx().isAlly(accID=databaseID)


class PlayerMenuHandler(AbstractContextMenuHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cmProxy, ctx=None):
        self.__denunciator = BattleDenunciator()
        self.__arenaUniqueID = BattleDenunciator.getArenaUniqueID()
        g_eventBus.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(PlayerMenuHandler, self).__init__(cmProxy, ctx=ctx, handlers=_OPTIONS_HANDLERS)

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @property
    def arenaGuiType(self):
        return self.sessionProvider.arenaVisitor.gui

    def fini(self):
        g_eventBus.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.__denunciator = None
        super(PlayerMenuHandler, self).fini()
        return

    def addFriend(self):
        self.proto.contacts.addFriend(self.__userInfo.databaseID, self.__userInfo.userName)

    def removeFriend(self):
        self.proto.contacts.removeFriend(self.__userInfo.databaseID)

    def setIgnored(self):
        self.proto.contacts.addIgnored(self.__userInfo.databaseID, self.__userInfo.userName)

    def unsetIgnored(self):
        self.proto.contacts.removeIgnored(self.__userInfo.databaseID)

    def disableCommunications(self):
        self.proto.contacts.addTmpIgnored(self.__userInfo.databaseID, self.__userInfo.userName)

    def enableCommunications(self):
        self.proto.contacts.removeTmpIgnored(self.__userInfo.databaseID)

    def setMuted(self):
        self.proto.contacts.setMuted(self.__userInfo.databaseID, self.__userInfo.userName)

    def unsetMuted(self):
        self.proto.contacts.unsetMuted(self.__userInfo.databaseID)

    def appealIncorrectBehavior(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.INCORRECT_BEHAVIOR, self.__arenaUniqueID)

    def appealNotFairPlay(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.NOT_FAIR_PLAY, self.__arenaUniqueID)

    def appealForbiddenNick(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.FORBIDDEN_NICK, self.__arenaUniqueID)

    def appealBot(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.BOT, self.__arenaUniqueID)

    def sendInvitation(self):
        self.sessionProvider.invitations.send(self.__userInfo.databaseID)

    def acceptInvitation(self):
        self.sessionProvider.invitations.accept(self.__userInfo.databaseID)

    def rejectInvitation(self):
        self.sessionProvider.invitations.reject(self.__userInfo.databaseID)

    def _initFlashValues(self, ctx):
        self.__vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(long(ctx.vehicleID))
        player = self.__vInfo.player
        self.__userInfo = PlayerContextMenuInfo(player.accountDBID, player.name)

    def _clearFlashValues(self):
        self.__userInfo = None
        self.__vInfo = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        options = self.__addDyncSquadInfo(options)
        options = self.__addFriendshipInfo(options)
        options = self.__addIgnoreInfo(options)
        options = self.__addCommunicationInfo(options)
        options = self.__addMutedInfo(options)
        options = self.__addDenunciationsInfo(options)
        return options

    @classmethod
    def _getOptionIcon(cls, optionID):
        return _OPTION_ICONS.get(optionID, '')

    @classmethod
    def _getOptionInitData(cls, optionID, isEnabled=True):
        return {'enabled': isEnabled,
         'iconType': cls._getOptionIcon(optionID)}

    def __addDyncSquadInfo(self, options):
        make = self._makeItem
        ctx = self.sessionProvider.getCtx()
        if not ctx.isInvitationEnabled() or ctx.hasSquadRestrictions():
            return options
        elif not self.__userInfo.isAlly:
            return options
        else:
            contact = self.usersStorage.getUser(self.__userInfo.databaseID)
            isIgnored = contact is not None and contact.isIgnored()
            status = self.__vInfo.invitationDeliveryStatus
            if status & _D_STATUS.FORBIDDEN_BY_RECEIVER > 0 or status & _D_STATUS.SENT_TO > 0 and not status & _D_STATUS.SENT_INACTIVE:
                optionID = DYN_SQUAD_OPTION_ID.SENT_INVITATION
                isEnabled = False
            elif status & _D_STATUS.RECEIVED_FROM > 0 and not status & _D_STATUS.RECEIVED_INACTIVE:
                optionID = None
            elif self.__vInfo.isSquadMan():
                optionID = DYN_SQUAD_OPTION_ID.IN_SQUAD
                isEnabled = False
            else:
                optionID = DYN_SQUAD_OPTION_ID.SENT_INVITATION
                isEnabled = not isIgnored
            if optionID is not None:
                options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
            if status & _D_STATUS.RECEIVED_FROM > 0 and not status & _D_STATUS.RECEIVED_INACTIVE:
                options.append(make(DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION), optInitData=self._getOptionInitData(DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION, not isIgnored)))
                options.append(make(DYN_SQUAD_OPTION_ID.REJECT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.REJECT_INVITATION), optInitData=self._getOptionInitData(DYN_SQUAD_OPTION_ID.REJECT_INVITATION, not isIgnored)))
            return options

    def __addFriendshipInfo(self, options):
        isEnabled = self.__userInfo.isSameRealm
        if self.__userInfo.isFriend:
            optionID = USER.REMOVE_FROM_FRIENDS
        else:
            optionID = USER.ADD_TO_FRIENDS
        options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
        return options

    def __addIgnoreInfo(self, options):
        isEnabled = self.__userInfo.isSameRealm
        if self.__userInfo.isTemporaryIgnored:
            optionID = USER.ADD_TO_IGNORED
            isEnabled = False
        elif self.__userInfo.isIgnored:
            optionID = USER.REMOVE_FROM_IGNORED
        else:
            optionID = USER.ADD_TO_IGNORED
        options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
        return options

    def __addCommunicationInfo(self, options):
        if self.__userInfo.isAlly and not self.arenaGuiType.isTrainingBattle():
            isEnabled = self.__userInfo.isSameRealm
            if self.__userInfo.isTemporaryIgnored:
                optionID = BATTLE_CHAT_OPTION_ID.ENABLE_COMMUNICATIONS
            elif not self.__userInfo.isIgnored:
                optionID = BATTLE_CHAT_OPTION_ID.DISABLE_COMMUNICATIONS
            else:
                optionID = BATTLE_CHAT_OPTION_ID.DISABLE_COMMUNICATIONS
                isEnabled = False
            options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
        return options

    def __addMutedInfo(self, options):
        isVisible = self.bwProto.voipController.isVOIPEnabled() and (self.__userInfo.isAlly or self.arenaGuiType.isTrainingBattle())
        isEnabled = not self.__userInfo.isIgnored or self.__userInfo.isTemporaryIgnored
        if self.__userInfo.isMuted:
            optionID = USER.UNSET_MUTED
        else:
            optionID = USER.SET_MUTED
        if isVisible:
            options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
        return options

    def __isAppealsForTopicEnabled(self, topic):
        topicID = DENUNCIATIONS_MAP[topic]
        return self.__denunciator.isAppealsForTopicEnabled(self.__userInfo.databaseID, topicID, self.__arenaUniqueID)

    def __addDenunciationsInfo(self, options):
        make = self._makeItem
        if self.__userInfo.isAlly or self.arenaGuiType.isTrainingBattle():
            order = DENUNCIATIONS.ORDER
        else:
            order = DENUNCIATIONS.ENEMY_ORDER
        sub = [ make(denunciation, MENU.contextmenu(denunciation), optInitData={'enabled': self.__isAppealsForTopicEnabled(denunciation)}) for denunciation in order ]
        label = '{} {}/{}'.format(i18n.makeString(MENU.CONTEXTMENU_APPEAL), self.__denunciator.getDenunciationsLeft(), DENUNCIATIONS_PER_DAY)
        options.append(make(DENUNCIATIONS.APPEAL, label, optInitData={'enabled': self.__denunciator.isAppealsEnabled()}, optSubMenu=sub))
        return options

    def __handleHideCursor(self, _):
        self.onContextMenuHide()
