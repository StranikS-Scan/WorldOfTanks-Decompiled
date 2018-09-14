# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_cm_handlers.py
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui.clans.contexts import CreateInviteCtx
from gui.clans import formatters as clans_fmts
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import i18n
from gui import SystemMessages
from gui.clans.clan_controller import g_clanCtrl
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.context import SendInvitesCtx, PrebattleAction
from gui.prb_control.prb_helpers import prbDispatcherProperty, prbFunctionalProperty
from gui.shared import g_itemsCache, event_dispatcher as shared_events, utils
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.managers.context_menu.AbstractContextMenuHandler import AbstractContextMenuHandler
from helpers.i18n import makeString
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE, USER_TAG
from messenger.proto import proto_getter
from messenger.storage import storage_getter

class USER(object):
    INFO = 'userInfo'
    CLAN_INFO = 'clanInfo'
    SEND_CLAN_INVITE = 'sendClanInvite'
    CREATE_PRIVATE_CHANNEL = 'createPrivateChannel'
    ADD_TO_FRIENDS = 'addToFriends'
    ADD_TO_FRIENDS_AGAIN = 'addToFriendsAgain'
    REMOVE_FROM_FRIENDS = 'removeFromFriends'
    ADD_TO_IGNORED = 'addToIgnored'
    REMOVE_FROM_IGNORED = 'removeFromIgnored'
    COPY_TO_CLIPBOARD = 'copyToClipBoard'
    SET_MUTED = 'setMuted'
    UNSET_MUTED = 'unsetMuted'
    CREATE_SQUAD = 'createSquad'
    INVITE = 'invite'
    REQUEST_FRIENDSHIP = 'requestFriendship'


class DENUICATIONS(object):
    APPEAL = 'appeal'
    OFFEND = 'offend'
    FLOOD = 'flood'
    BLACKMAIL = 'blackmail'
    SWINDLE = 'swindle'
    NOT_FAIR_PLAY = 'notFairPlay'
    FORBIDDEN_NICK = 'forbiddenNick'
    BOT = 'bot'


class BaseUserCMHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx = None):
        super(BaseUserCMHandler, self).__init__(cmProxy, ctx, handlers=self._getHandlers())

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @prbFunctionalProperty
    def prbFunctional(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def canInvite(self):
        return self.prbDispatcher.getFunctionalCollection().canSendInvite(self.databaseID)

    def isSquadCreator(self):
        return self.prbFunctional.getEntityType() == PREBATTLE_TYPE.SQUAD and self.prbFunctional.isCreator()

    def showUserInfo(self):

        def onDossierReceived(databaseID, userName):
            shared_events.showProfileWindow(databaseID, userName)

        shared_events.requestProfile(self.databaseID, self.userName, successCallback=onDossierReceived)

    def showClanInfo(self):
        if not g_lobbyContext.getServerSettings().clanProfile.isEnabled():
            SystemMessages.pushMessage(makeString(SYSTEM_MESSAGES.CLANS_ISCLANPROFILEDISABLED), type=SystemMessages.SM_TYPE.Error)
            return

        def onDossierReceived(databaseID, _):
            clanID, _ = g_itemsCache.items.getClanInfo(databaseID)
            if clanID != 0:
                shared_events.showClanProfileWindow(clanID)
            else:
                from gui import DialogsInterface
                key = 'clan data is not available'
                DialogsInterface.showI18nInfoDialog(key, lambda result: None, I18nInfoDialogMeta(key, messageCtx={'userName': key}))

        shared_events.requestProfile(self.databaseID, self.userName, successCallback=onDossierReceived)

    @process
    def sendClanInvite(self):
        profile = g_clanCtrl.getAccountProfile()
        context = CreateInviteCtx(profile.getClanDbID(), [self.databaseID])
        result = yield g_clanCtrl.sendRequest(context, allowDelay=True)
        if result.isSuccess():
            SystemMessages.pushMessage(clans_fmts.getAppSentSysMsg(profile.getClanName(), profile.getClanAbbrev()))
        else:
            SystemMessages.pushMessage(clans_fmts.getInvitesNotSentSysMsg([self.userName or '']), type=SystemMessages.SM_TYPE.Error)

    def createPrivateChannel(self):
        self.proto.contacts.createPrivateChannel(self.databaseID, self.userName)

    def addFriend(self):
        self.proto.contacts.addFriend(self.databaseID, self.userName)

    def requestFriendship(self):
        self.proto.contacts.requestFriendship(self.databaseID)

    def removeFriend(self):
        self.proto.contacts.removeFriend(self.databaseID)

    def setMuted(self):
        self.proto.contacts.setMuted(self.databaseID, self.userName)

    def unsetMuted(self):
        self.proto.contacts.unsetMuted(self.databaseID)

    def setIgnored(self):
        self.proto.contacts.addIgnored(self.databaseID, self.userName)

    def unsetIgnored(self):
        self.proto.contacts.removeIgnored(self.databaseID)

    def copyToClipboard(self):
        utils.copyToClipboard(self.userName)

    def createSquad(self):
        self.prbDispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.SQUAD, accountsToInvite=(self.databaseID,)))

    def invite(self):
        user = self.usersStorage.getUser(self.databaseID)
        for func in self.prbDispatcher.getFunctionalCollection().getIterator():
            if func.getPermissions().canSendInvite():
                func.request(SendInvitesCtx([self.databaseID], ''))
                self.__showInviteMessage(user)
                break

    def getOptions(self, ctx = None):
        if not self._getUseCmInfo().isCurrentPlayer:
            return self._generateOptions(ctx)
        else:
            return None

    def _getHandlers(self):
        return {USER.INFO: 'showUserInfo',
         USER.CLAN_INFO: 'showClanInfo',
         USER.SEND_CLAN_INVITE: 'sendClanInvite',
         USER.CREATE_PRIVATE_CHANNEL: 'createPrivateChannel',
         USER.ADD_TO_FRIENDS: 'addFriend',
         USER.REMOVE_FROM_FRIENDS: 'removeFriend',
         USER.ADD_TO_IGNORED: 'setIgnored',
         USER.REMOVE_FROM_IGNORED: 'unsetIgnored',
         USER.COPY_TO_CLIPBOARD: 'copyToClipboard',
         USER.SET_MUTED: 'setMuted',
         USER.UNSET_MUTED: 'unsetMuted',
         USER.CREATE_SQUAD: 'createSquad',
         USER.INVITE: 'invite',
         USER.REQUEST_FRIENDSHIP: 'requestFriendship'}

    def _initFlashValues(self, ctx):
        self.databaseID = long(ctx.dbID)
        self.userName = ctx.userName
        self.wasInBattle = getattr(ctx, 'wasInBattle', True)

    def _clearFlashValues(self):
        self.databaseID = None
        self.userName = None
        self.wasInBattle = None
        return

    def _getUseCmInfo(self):
        return UserContextMenuInfo(self.databaseID, self.userName)

    def _generateOptions(self, ctx = None):
        userCMInfo = self._getUseCmInfo()
        if ctx is not None and not userCMInfo.hasClan:
            try:
                clanAbbrev = ctx.clanAbbrev
                userCMInfo.hasClan = bool(clanAbbrev)
            except:
                LOG_DEBUG('ctx has no property "clanAbbrev"')

        options = [self._makeItem(USER.INFO, MENU.contextmenu(USER.INFO))]
        options = self._addClanProfileInfo(options, userCMInfo)
        options = self._addFriendshipInfo(options, userCMInfo)
        options = self._addChannelInfo(options, userCMInfo)
        options.append(self._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)))
        options = self._addSquadInfo(options, userCMInfo.isIgnored)
        options = self._addPrebattleInfo(options, userCMInfo)
        options = self._addClubInfo(options, userCMInfo)
        options = self._addContactsNoteInfo(options, userCMInfo)
        options = self._addAppealInfo(options)
        options = self._addIgnoreInfo(options, userCMInfo)
        options = self._addMutedInfo(options, userCMInfo)
        options = self._addRejectFriendshipInfo(options, userCMInfo)
        options = self._addRemoveFromGroupInfo(options, userCMInfo)
        options = self._addRemoveFriendInfo(options, userCMInfo)
        options = self._addInviteClanInfo(options, userCMInfo)
        return options

    def _addIgnoreInfo(self, options, userCMInfo):
        ignoring = USER.REMOVE_FROM_IGNORED if userCMInfo.isIgnored else USER.ADD_TO_IGNORED
        options.append(self._makeItem(ignoring, MENU.contextmenu(ignoring), optInitData={'enabled': userCMInfo.isSameRealm}))
        return options

    def _addFriendshipInfo(self, options, userCMInfo):
        if not userCMInfo.isFriend:
            options.append(self._makeItem(USER.ADD_TO_FRIENDS, MENU.contextmenu(USER.ADD_TO_FRIENDS), optInitData={'enabled': userCMInfo.isSameRealm}))
        elif self.proto.contacts.isBidiFriendshipSupported():
            if USER_TAG.SUB_NONE in userCMInfo.getTags():
                options.append(self._makeItem(USER.REQUEST_FRIENDSHIP, MENU.contextmenu(USER.ADD_TO_FRIENDS_AGAIN), optInitData={'enabled': userCMInfo.isSameRealm}))
        return options

    def _addChannelInfo(self, options, userCMInfo):
        if not userCMInfo.isIgnored:
            options.append(self._makeItem(USER.CREATE_PRIVATE_CHANNEL, MENU.contextmenu(USER.CREATE_PRIVATE_CHANNEL), optInitData={'enabled': userCMInfo.canCreateChannel}))
        return options

    def _addSquadInfo(self, options, isIgnored):
        if not isIgnored and not self.isSquadCreator():
            canCreate = self.prbDispatcher.getFunctionalCollection().canCreateSquad()
            options.append(self._makeItem(USER.CREATE_SQUAD, MENU.contextmenu(USER.CREATE_SQUAD), optInitData={'enabled': canCreate}))
        return options

    def _addPrebattleInfo(self, options, userCMInfo):
        if not userCMInfo.isIgnored and self.canInvite():
            options.append(self._makeItem(USER.INVITE, MENU.contextmenu(USER.INVITE)))
        return options

    def _addRemoveFriendInfo(self, options, userCMInfo):
        if userCMInfo.isFriend:
            options.append(self._makeItem(USER.REMOVE_FROM_FRIENDS, MENU.contextmenu(USER.REMOVE_FROM_FRIENDS), optInitData={'enabled': userCMInfo.isSameRealm}))
        return options

    def _addContactsNoteInfo(self, options, userCMInfo):
        return options

    def _addAppealInfo(self, options):
        return options

    def _addMutedInfo(self, options, userCMInfo):
        return options

    def _addRemoveFromGroupInfo(self, options, isIgnored):
        return options

    def _addRejectFriendshipInfo(self, options, userCMInfo):
        return options

    def _addClubInfo(self, options, userCMInfo):
        return options

    def _addClanProfileInfo(self, options, userCMInfo):
        if g_lobbyContext.getServerSettings().clanProfile.isEnabled() and userCMInfo.hasClan:
            options.append(self._makeItem(USER.CLAN_INFO, MENU.contextmenu(USER.CLAN_INFO), optInitData={'enabled': g_clanCtrl.isAvailable()}))
        return options

    def _addInviteClanInfo(self, options, userCMInfo):
        if g_lobbyContext.getServerSettings().clanProfile.isEnabled() and not userCMInfo.hasClan:
            profile = g_clanCtrl.getAccountProfile()
            if profile.isInClan() and profile.getMyClanPermissions().canHandleClanInvites():
                options.append(self._makeItem(USER.SEND_CLAN_INVITE, MENU.contextmenu(USER.SEND_CLAN_INVITE), optInitData={'enabled': g_clanCtrl.isAvailable()}))
        return options

    @classmethod
    def __showInviteMessage(cls, user):
        if user:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
        else:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)


class AppealCMHandler(BaseUserCMHandler):

    def appealOffend(self):
        self._makeAppeal(constants.DENUNCIATION.OFFEND)

    def appealFlood(self):
        self._makeAppeal(constants.DENUNCIATION.FLOOD)

    def appealBlackmail(self):
        self._makeAppeal(constants.DENUNCIATION.BLACKMAIL)

    def appealSwindle(self):
        self._makeAppeal(constants.DENUNCIATION.SWINDLE)

    def appealNotFairPlay(self):
        self._makeAppeal(constants.DENUNCIATION.NOT_FAIR_PLAY)

    def appealForbiddenNick(self):
        self._makeAppeal(constants.DENUNCIATION.FORBIDDEN_NICK)

    def appealBot(self):
        self._makeAppeal(constants.DENUNCIATION.BOT)

    def _getHandlers(self):
        handlers = super(AppealCMHandler, self)._getHandlers()
        handlers.update({DENUICATIONS.OFFEND: 'appealOffend',
         DENUICATIONS.FLOOD: 'appealFlood',
         DENUICATIONS.BLACKMAIL: 'appealBlackmail',
         DENUICATIONS.SWINDLE: 'appealSwindle',
         DENUICATIONS.NOT_FAIR_PLAY: 'appealNotFairPlay',
         DENUICATIONS.FORBIDDEN_NICK: 'appealForbiddenNick',
         DENUICATIONS.BOT: 'appealBot'})
        return handlers

    def _addAppealInfo(self, options):
        if self.wasInBattle:
            options.append(self._createSubMenuItem())
        return options

    def _getSubmenuData(self):
        return [self._makeItem(DENUICATIONS.OFFEND, MENU.contextmenu(DENUICATIONS.OFFEND)),
         self._makeItem(DENUICATIONS.FLOOD, MENU.contextmenu(DENUICATIONS.FLOOD)),
         self._makeItem(DENUICATIONS.BLACKMAIL, MENU.contextmenu(DENUICATIONS.BLACKMAIL)),
         self._makeItem(DENUICATIONS.SWINDLE, MENU.contextmenu(DENUICATIONS.SWINDLE)),
         self._makeItem(DENUICATIONS.NOT_FAIR_PLAY, MENU.contextmenu(DENUICATIONS.NOT_FAIR_PLAY)),
         self._makeItem(DENUICATIONS.FORBIDDEN_NICK, MENU.contextmenu(DENUICATIONS.FORBIDDEN_NICK)),
         self._makeItem(DENUICATIONS.BOT, MENU.contextmenu(DENUICATIONS.BOT))]

    def _createSubMenuItem(self):
        labelStr = i18n.makeString(MENU.CONTEXTMENU_APPEAL) + ' (' + str(self._getDenunciationsLeft()) + ')'
        return self._makeItem(DENUICATIONS.APPEAL, labelStr, optInitData={'enabled': self._isAppealsEnabled()}, optSubMenu=self._getSubmenuData())

    def _isAppealsEnabled(self):
        return self._getDenunciationsLeft() > 0

    def _getDenunciationsLeft(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def _makeAppeal(self, appealID):
        BigWorld.player().makeDenunciation(self.databaseID, appealID, constants.VIOLATOR_KIND.UNKNOWN)
        topicStr = i18n.makeString(MENU.denunciation(appealID))
        sysMsg = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_SUCCESS) % {'name': self.userName,
         'topic': topicStr}
        SystemMessages.pushMessage(sysMsg, type=SystemMessages.SM_TYPE.Information)


class UserContextMenuInfo(object):

    def __init__(self, databaseID, userName):
        self.user = self.usersStorage.getUser(databaseID)
        self.databaseID = databaseID
        self.canAddToIgnore = True
        self.canDoDenunciations = True
        self.isFriend = False
        self.isIgnored = False
        self.isMuted = False
        self.hasClan = False
        self.displayName = userName
        self.isOnline = False
        self.isCurrentPlayer = False
        if self.user is not None:
            self.isFriend = self.user.isFriend()
            self.isIgnored = self.user.isIgnored()
            self.isMuted = self.user.isMuted()
            self.displayName = self.user.getFullName()
            self.isOnline = self.user.isOnline()
            self.isCurrentPlayer = self.user.isCurrentPlayer()
            self.hasClan = self.user.getClanInfo().isInClan()
        super(UserContextMenuInfo, self).__init__()
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def isSameRealm(self):
        return g_lobbyContext.getServerSettings().roaming.isSameRealm(self.databaseID)

    @property
    def canCreateChannel(self):
        roaming = g_lobbyContext.getServerSettings().roaming
        if g_settings.server.XMPP.isEnabled():
            canCreate = roaming.isSameRealm(self.databaseID)
        else:
            canCreate = not roaming.isInRoaming() and not roaming.isPlayerInRoaming(self.databaseID) and self.isOnline
        return canCreate

    def getTags(self):
        if self.user is not None:
            return self.user.getTags()
        else:
            return set()

    def getNote(self):
        if self.user is not None:
            return self.user.getNote()
        else:
            return ''
