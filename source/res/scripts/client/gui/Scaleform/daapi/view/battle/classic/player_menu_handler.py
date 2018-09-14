# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/player_menu_handler.py
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import USER
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import UserContextMenuInfo
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS as _D_STATUS
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.denunciator import DENUNCIATIONS, BattleDenunciator
from helpers import i18n
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter

class DYN_SQUAD_OPTION_ID(object):
    SENT_INVITATION = 'sendInvitationToSquad'
    ACCEPT_INVITATION = 'acceptInvitationToSquad'
    REJECT_INVITATION = 'rejectInvitationToSquad'
    IN_SQUAD = 'inSquad'


_OPTIONS_HANDLERS = {USER.ADD_TO_FRIENDS: 'addFriend',
 USER.REMOVE_FROM_FRIENDS: 'removeFriend',
 USER.ADD_TO_IGNORED: 'setIgnored',
 USER.REMOVE_FROM_IGNORED: 'unsetIgnored',
 USER.SET_MUTED: 'setMuted',
 USER.UNSET_MUTED: 'unsetMuted',
 DENUNCIATIONS.OFFEND: 'appealOffend',
 DENUNCIATIONS.FLOOD: 'appealFlood',
 DENUNCIATIONS.BLACKMAIL: 'appealBlackmail',
 DENUNCIATIONS.SWINDLE: 'appealSwindle',
 DENUNCIATIONS.NOT_FAIR_PLAY: 'appealNotFairPlay',
 DENUNCIATIONS.FORBIDDEN_NICK: 'appealForbiddenNick',
 DENUNCIATIONS.BOT: 'appealBot',
 DYN_SQUAD_OPTION_ID.SENT_INVITATION: 'sendInvitation',
 DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION: 'acceptInvitation',
 DYN_SQUAD_OPTION_ID.REJECT_INVITATION: 'rejectInvitation'}

class PlayerMenuHandler(AbstractContextMenuHandler):

    def __init__(self, cmProxy, ctx=None):
        self.__denunciator = BattleDenunciator()
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

    def setMuted(self):
        self.proto.contacts.setMuted(self.__userInfo.databaseID, self.__userInfo.userName)

    def unsetMuted(self):
        self.proto.contacts.unsetMuted(self.__userInfo.databaseID)

    def appealOffend(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.OFFEND)

    def appealFlood(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.FLOOD)

    def appealBlackmail(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.BLACKMAIL)

    def appealSwindle(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.SWINDLE)

    def appealNotFairPlay(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.NOT_FAIR_PLAY)

    def appealForbiddenNick(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.FORBIDDEN_NICK)

    def appealBot(self):
        self.__denunciator.makeAppeal(self.__userInfo.databaseID, self.__userInfo.userName, DENUNCIATIONS.BOT)

    def sendInvitation(self):
        g_sessionProvider.invitations.send(self.__userInfo.databaseID)

    def acceptInvitation(self):
        g_sessionProvider.invitations.accept(self.__userInfo.databaseID)

    def rejectInvitation(self):
        g_sessionProvider.invitations.reject(self.__userInfo.databaseID)

    def _initFlashValues(self, ctx):
        self.__vInfo = g_sessionProvider.getArenaDP().getVehicleInfo(long(ctx.vehicleID))
        player = self.__vInfo.player
        self.__userInfo = UserContextMenuInfo(player.accountDBID, player.name)

    def _clearFlashValues(self):
        self.__userInfo = None
        self.__vInfo = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        options = self.__addDyncSquadInfo(options)
        options = self.__addFriendshipInfo(options)
        options = self.__addIgnoreInfo(options)
        options = self.__addDenunciationsInfo(options)
        options = self.__addMutedInfo(options)
        return options

    def __addDyncSquadInfo(self, options):
        make = self._makeItem
        ctx = g_sessionProvider.getCtx()
        if not ctx.isInvitationEnabled() or ctx.hasSquadRestrictions():
            return options
        elif not g_sessionProvider.getArenaDP().isAllyTeam(self.__vInfo.team):
            return options
        else:
            contact = self.usersStorage.getUser(self.__userInfo.databaseID)
            isIgnored = contact is not None and contact.isIgnored()
            status = self.__vInfo.invitationDeliveryStatus
            if status & _D_STATUS.FORBIDDEN_BY_RECEIVER > 0 or status & _D_STATUS.RECEIVED_FROM > 0 and not status & _D_STATUS.RECEIVED_INACTIVE or status & _D_STATUS.SENT_TO > 0 and not status & _D_STATUS.SENT_INACTIVE:
                options.append(make(DYN_SQUAD_OPTION_ID.SENT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.SENT_INVITATION), optInitData={'enabled': False}))
            elif self.__vInfo.isSquadMan():
                options.append(make(DYN_SQUAD_OPTION_ID.IN_SQUAD, MENU.contextmenu(DYN_SQUAD_OPTION_ID.IN_SQUAD), optInitData={'enabled': False}))
            else:
                options.append(make(DYN_SQUAD_OPTION_ID.SENT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.SENT_INVITATION), optInitData={'enabled': not isIgnored}))
            if status & _D_STATUS.RECEIVED_FROM > 0 and not status & _D_STATUS.RECEIVED_INACTIVE:
                options.append(make(DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION), optInitData={'enabled': not isIgnored}))
                options.append(make(DYN_SQUAD_OPTION_ID.REJECT_INVITATION, MENU.contextmenu(DYN_SQUAD_OPTION_ID.REJECT_INVITATION)))
            return options

    def __addFriendshipInfo(self, options):
        data = {'enabled': self.__userInfo.isSameRealm}
        if self.__userInfo.isFriend:
            optionID = USER.REMOVE_FROM_FRIENDS
        else:
            optionID = USER.ADD_TO_FRIENDS
        options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=data))
        return options

    def __addIgnoreInfo(self, options):
        data = {'enabled': self.__userInfo.isSameRealm}
        if self.__userInfo.isIgnored:
            optionID = USER.REMOVE_FROM_IGNORED
        else:
            optionID = USER.ADD_TO_IGNORED
        options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=data))
        return options

    def __addMutedInfo(self, options):
        muted = USER.UNSET_MUTED if self.__userInfo.isMuted else USER.SET_MUTED
        if not self.__userInfo.isIgnored and self.bwProto.voipController.isVOIPEnabled():
            options.append(self._makeItem(muted, MENU.contextmenu(muted)))
        return options

    def __addDenunciationsInfo(self, options):
        make = self._makeItem
        sub = [ make(value, MENU.contextmenu(value)) for value in DENUNCIATIONS.ORDER ]
        label = '{} ({})'.format(i18n.makeString(MENU.CONTEXTMENU_APPEAL), self.__denunciator.getDenunciationsLeft())
        options.append(make(DENUNCIATIONS.APPEAL, label, optInitData={'enabled': self.__denunciator.isAppealsEnabled()}, optSubMenu=sub))
        return options

    def __handleHideCursor(self, _):
        self.onContextMenuHide()
