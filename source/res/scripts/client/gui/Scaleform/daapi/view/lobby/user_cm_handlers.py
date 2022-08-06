# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_cm_handlers.py
import math
from Event import Event
from adisp import process
from constants import DENUNCIATIONS_PER_DAY, ARENA_GUI_TYPE, IS_CHINA, PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages, DialogsInterface
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.clans.clan_helpers import showClanInviteSystemMsg
from gui.prb_control import prbDispatcherProperty, prbEntityProperty
from gui.prb_control.entities.base.ctx import PrbAction, SendInvitesCtx
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import event_dispatcher as shared_events, events, g_eventBus, utils
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.ClanCache import ClanInfo
from gui.shared.denunciator import LobbyDenunciator, DENUNCIATIONS, DENUNCIATIONS_MAP
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import showSentInviteMessage
from gui.wgcg.clan.contexts import CreateInviteCtx
from helpers import i18n, dependency
from helpers.i18n import makeString
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE, USER_TAG, UserEntityScope
from messenger.proto import proto_getter
from messenger.proto.entities import SharedUserEntity
from messenger.proto.entities import ClanInfo as UserClanInfo
from messenger.storage import storage_getter
from nation_change_helpers.client_nation_change_helper import getValidVehicleCDForNationChange
from skeletons.gui.game_control import IVehicleComparisonBasket, IBattleRoyaleController, IMapboxController, IEventBattlesController, IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController

class _EXTENDED_OPT_IDS(object):
    VEHICLE_COMPARE = 'userVehicleCompare'


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
    CREATE_EVENT_SQUAD = 'createEventSquad'
    CREATE_BATTLE_ROYALE_SQUAD = 'createBattleRoyaleSquad'
    INVITE = 'invite'
    REQUEST_FRIENDSHIP = 'requestFriendship'
    VEHICLE_INFO = 'vehicleInfoEx'
    VEHICLE_PREVIEW = 'vehiclePreview'
    END_REFERRAL_COMPANY = 'endReferralCompany'
    CREATE_MAPBOX_SQUAD = 'createMapboxSquad'


_CM_ICONS = {USER.END_REFERRAL_COMPANY: 'endReferralCompany'}

class BaseUserCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    clanCtrl = dependency.descriptor(IWebController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, cmProxy, ctx=None):
        super(BaseUserCMHandler, self).__init__(cmProxy, ctx, handlers=self._getHandlers())

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @prbEntityProperty
    def prbEntity(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def canInvite(self):
        if self.prbEntity is not None:
            if hasattr(self.prbEntity, 'getFlags'):
                flags = self.prbEntity.getFlags()
                if flags.isInSearch():
                    return False
            return self.prbEntity.getPermissions().canSendInvite()
        else:
            return False

    def isSquadCreator(self):
        return False

    def showUserInfo(self):

        def onDossierReceived(databaseID, userName):
            shared_events.showProfileWindow(databaseID, userName)

        shared_events.requestProfile(self.databaseID, self.userName, successCallback=onDossierReceived)

    def showClanInfo(self):
        if not self.lobbyContext.getServerSettings().clanProfile.isEnabled():
            SystemMessages.pushMessage(makeString(SYSTEM_MESSAGES.CLANS_ISCLANPROFILEDISABLED), type=SystemMessages.SM_TYPE.Error)
            return

        def onDossierReceived(databaseID, _):
            clanID, clanInfo = self.itemsCache.items.getClanInfo(databaseID)
            if clanID != 0:
                clanInfo = ClanInfo(*clanInfo)
                shared_events.showClanProfileWindow(clanID, clanInfo.getClanAbbrev())
            else:
                DialogsInterface.showI18nInfoDialog('clan_data_not_available', lambda result: None)

        shared_events.requestProfile(self.databaseID, self.userName, successCallback=onDossierReceived)

    @process
    def sendClanInvite(self):
        profile = self.clanCtrl.getAccountProfile()
        userName = self.userName
        context = CreateInviteCtx(profile.getClanDbID(), [self.databaseID])
        result = yield self.clanCtrl.sendRequest(context, allowDelay=True)
        showClanInviteSystemMsg(userName, result.isSuccess(), result.getCode(), result.data)

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
        self._doSelect(PREBATTLE_ACTION_NAME.SQUAD, (self.databaseID,))

    def createEventSquad(self):
        self._doSelect(PREBATTLE_ACTION_NAME.EVENT_SQUAD, (self.databaseID,))

    def createBattleRoyaleSquad(self):
        self._doSelect(PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, (self.databaseID,))

    def createMapboxSquad(self):
        self._doSelect(PREBATTLE_ACTION_NAME.MAPBOX_SQUAD, (self.databaseID,))

    def invite(self):
        user = self.usersStorage.getUser(self.databaseID)
        if self.prbEntity.getPermissions().canSendInvite():
            self.prbEntity.request(SendInvitesCtx([self.databaseID], ''))
            showSentInviteMessage(user)

    def getOptions(self, ctx=None):
        return self._generateOptions(ctx) if not self._getUseCmInfo().isCurrentPlayer else None

    def _getHandlers(self):
        handlers = {USER.INFO: 'showUserInfo',
         USER.CLAN_INFO: 'showClanInfo',
         USER.SEND_CLAN_INVITE: 'sendClanInvite',
         USER.CREATE_PRIVATE_CHANNEL: 'createPrivateChannel',
         USER.ADD_TO_FRIENDS: 'addFriend',
         USER.REMOVE_FROM_FRIENDS: 'removeFriend',
         USER.ADD_TO_IGNORED: 'setIgnored',
         USER.REMOVE_FROM_IGNORED: 'unsetIgnored',
         USER.COPY_TO_CLIPBOARD: 'copyToClipboard',
         USER.CREATE_SQUAD: 'createSquad',
         USER.CREATE_EVENT_SQUAD: 'createEventSquad',
         USER.CREATE_BATTLE_ROYALE_SQUAD: 'createBattleRoyaleSquad',
         USER.INVITE: 'invite',
         USER.REQUEST_FRIENDSHIP: 'requestFriendship',
         USER.CREATE_MAPBOX_SQUAD: 'createMapboxSquad'}
        if not IS_CHINA:
            handlers.update({USER.SET_MUTED: 'setMuted',
             USER.UNSET_MUTED: 'unsetMuted'})
        return handlers

    def _initFlashValues(self, ctx):
        self.databaseID = long(ctx.dbID)
        self.userName = ctx.userName
        self.wasInBattle = getattr(ctx, 'wasInBattle', True)
        self.showClanProfile = getattr(ctx, 'showClanProfile', True)
        self.clanAbbrev = getattr(ctx, 'clanAbbrev', None)
        return

    def _clearFlashValues(self):
        self.databaseID = None
        self.userName = None
        self.wasInBattle = None
        return

    def _getUseCmInfo(self):
        return UserContextMenuInfo(self.databaseID, self.userName, self.clanAbbrev)

    def _generateOptions(self, ctx=None):
        userCMInfo = self._getUseCmInfo()
        if ctx is not None and not userCMInfo.hasClan:
            try:
                clanAbbrev = ctx.clanAbbrev
                userCMInfo.hasClan = bool(clanAbbrev)
            except Exception:
                LOG_DEBUG('ctx has no property "clanAbbrev"')

        if userCMInfo.isBot:
            return self._makeAIBotOptions()
        else:
            options = [self._makeItem(USER.INFO, MENU.contextmenu(USER.INFO))]
            options = self._addVehicleInfo(options)
            options = self._addClanProfileInfo(options, userCMInfo)
            options = self._addFriendshipInfo(options, userCMInfo)
            options = self._addChannelInfo(options, userCMInfo)
            options.append(self._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)))
            options = self._addSquadInfo(options, userCMInfo.isIgnored)
            options = self._addPrebattleInfo(options, userCMInfo)
            options = self._addContactsNoteInfo(options, userCMInfo)
            options = self._addAppealInfo(options)
            options = self._addIgnoreInfo(options, userCMInfo)
            if not IS_CHINA:
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
        if not isIgnored and not self.isSquadCreator() and self.prbDispatcher is not None:
            canCreate = self.prbEntity.getPermissions().canCreateSquad()
            if not (self.__isSquadAlreadyCreated(PREBATTLE_TYPE.SQUAD) or self.__isSquadAlreadyCreated(PREBATTLE_TYPE.EPIC)):
                options.append(self._makeItem(USER.CREATE_SQUAD, MENU.contextmenu(USER.CREATE_SQUAD), optInitData={'enabled': canCreate}))
            if self.__eventBattlesCtrl.isEnabled() and not self.__isSquadAlreadyCreated(PREBATTLE_TYPE.EVENT):
                options.append(self._makeItem(USER.CREATE_EVENT_SQUAD, MENU.contextmenu(USER.CREATE_EVENT_SQUAD), optInitData={'enabled': canCreate,
                 'textColor': 13347959}))
            if self.__battleRoyale.isEnabled() and not self.__isSquadAlreadyCreated(PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT) and not self.__isSquadAlreadyCreated(PREBATTLE_TYPE.BATTLE_ROYALE):
                primeTimeStatus, _, _ = self.__battleRoyale.getPrimeTimeStatus()
                options.append(self._makeItem(USER.CREATE_BATTLE_ROYALE_SQUAD, MENU.contextmenu(USER.CREATE_BATTLE_ROYALE_SQUAD), optInitData={'enabled': canCreate and primeTimeStatus == PrimeTimeStatus.AVAILABLE,
                 'textColor': 13347959}))
            if self.__mapboxCtrl.isEnabled() and not self.__isSquadAlreadyCreated(PREBATTLE_TYPE.MAPBOX):
                isOptionEnabled = canCreate and self.__mapboxCtrl.isActive() and self.__mapboxCtrl.isInPrimeTime()
                options.append(self._makeItem(USER.CREATE_MAPBOX_SQUAD, backport.text(R.strings.menu.contextMenu.createMapboxSquad()), optInitData={'enabled': isOptionEnabled,
                 'textColor': 13347959}))
        return options

    def _addPrebattleInfo(self, options, userCMInfo):
        if not userCMInfo.isIgnored and self.canInvite():
            options.append(self._makeItem(USER.INVITE, MENU.contextmenu(USER.INVITE)))
        return options

    def _addRemoveFriendInfo(self, options, userCMInfo):
        if userCMInfo.isFriend:
            options.append(self._makeItem(USER.REMOVE_FROM_FRIENDS, MENU.contextmenu(USER.REMOVE_FROM_FRIENDS), optInitData={'enabled': userCMInfo.isSameRealm}))
        return options

    def _addVehicleInfo(self, options):
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

    def _addClanProfileInfo(self, options, userCMInfo):
        if self.lobbyContext.getServerSettings().clanProfile.isEnabled() and userCMInfo.hasClan and self.showClanProfile:
            options.append(self._makeItem(USER.CLAN_INFO, MENU.contextmenu(USER.CLAN_INFO), optInitData={'enabled': self.clanCtrl.isAvailable()}))
        return options

    def _addInviteClanInfo(self, options, userCMInfo):
        if self.lobbyContext.getServerSettings().clanProfile.isEnabled() and userCMInfo.user is not None and not userCMInfo.hasClan:
            profile = self.clanCtrl.getAccountProfile()
            canHandleClanInvites = profile.getMyClanPermissions().canHandleClanInvites()
            if profile.isInClan() and canHandleClanInvites:
                isEnabled = self.clanCtrl.isAvailable()
                canHandleClanInvites = profile.getMyClanPermissions().canHandleClanInvites()
                if isEnabled:
                    profile = self.clanCtrl.getAccountProfile()
                    dossier = profile.getClanDossier()
                    isEnabled = canHandleClanInvites and not dossier.isClanInviteSent(userCMInfo.databaseID) and not dossier.hasClanApplication(userCMInfo.databaseID)
                options.append(self._makeItem(USER.SEND_CLAN_INVITE, MENU.contextmenu(USER.SEND_CLAN_INVITE), optInitData={'enabled': isEnabled}))
        return options

    def _makeAIBotOptions(self):
        return [self._makeItem(USER.VEHICLE_INFO, MENU.contextmenu(USER.VEHICLE_INFO)), self._makeItem(USER.VEHICLE_PREVIEW, MENU.contextmenu(USER.VEHICLE_PREVIEW), optInitData={'enabled': not self.prbDispatcher.getFunctionalState().isNavigationDisabled()})]

    def _doSelect(self, prebattleActionName, accountsToInvite=None):
        action = PrbAction(prebattleActionName, accountsToInvite=accountsToInvite)
        event = events.PrbActionEvent(action, events.PrbActionEvent.SELECT)
        g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)

    def __isSquadAlreadyCreated(self, prbType):
        return self.__platoonCtrl.isInPlatoon() and self.__platoonCtrl.getPrbEntityType() == prbType


class AppealCMHandler(BaseUserCMHandler):

    def __init__(self, cmProxy, ctx=None):
        super(AppealCMHandler, self).__init__(cmProxy, ctx)
        self._denunciator = LobbyDenunciator()

    def fini(self):
        self._denunciator = None
        super(AppealCMHandler, self).fini()
        return

    def appealIncorrectBehavior(self):
        self._denunciator.makeAppeal(self.databaseID, self.userName, DENUNCIATIONS.INCORRECT_BEHAVIOR, self._arenaUniqueID)

    def appealNotFairPlay(self):
        self._denunciator.makeAppeal(self.databaseID, self.userName, DENUNCIATIONS.NOT_FAIR_PLAY, self._arenaUniqueID)

    def appealForbiddenNick(self):
        self._denunciator.makeAppeal(self.databaseID, self.userName, DENUNCIATIONS.FORBIDDEN_NICK, self._arenaUniqueID)

    def appealBot(self):
        self._denunciator.makeAppeal(self.databaseID, self.userName, DENUNCIATIONS.BOT, self._arenaUniqueID)

    def showVehicleInfo(self):
        vehicleCD = getValidVehicleCDForNationChange(self._vehicleCD)
        shared_events.showVehicleInfo(vehicleCD)

    def showVehiclePreview(self):
        vehicleCD = getValidVehicleCDForNationChange(self._vehicleCD)
        shared_events.showVehiclePreview(vehicleCD)
        shared_events.hideBattleResults()

    def _initFlashValues(self, ctx):
        self._vehicleCD = None
        vehicleCD = getattr(ctx, 'vehicleCD', None)
        if vehicleCD is not None and not math.isnan(vehicleCD):
            self._vehicleCD = int(vehicleCD)
        clientArenaIdx = getattr(ctx, 'clientArenaIdx', 0)
        self._arenaUniqueID = self.lobbyContext.getArenaUniqueIDByClientID(clientArenaIdx)
        self._arenaGuiType = getattr(ctx, 'arenaType', ARENA_GUI_TYPE.UNKNOWN)
        self._isAlly = getattr(ctx, 'isAlly', False)
        super(AppealCMHandler, self)._initFlashValues(ctx)
        return

    def _clearFlashValues(self):
        super(AppealCMHandler, self)._clearFlashValues()
        self._vehicleCD = None
        self._arenaGuiType = None
        self._isAlly = None
        return

    def _getHandlers(self):
        handlers = super(AppealCMHandler, self)._getHandlers()
        handlers.update({DENUNCIATIONS.INCORRECT_BEHAVIOR: 'appealIncorrectBehavior',
         DENUNCIATIONS.NOT_FAIR_PLAY: 'appealNotFairPlay',
         DENUNCIATIONS.FORBIDDEN_NICK: 'appealForbiddenNick',
         DENUNCIATIONS.BOT: 'appealBot',
         USER.VEHICLE_INFO: 'showVehicleInfo',
         USER.VEHICLE_PREVIEW: 'showVehiclePreview'})
        return handlers

    def _addAppealInfo(self, options):
        if self.wasInBattle:
            options.append(self._createSubMenuItem())
        return options

    def _addVehicleInfo(self, options):
        if self._vehicleCD > 0:
            vehicle = self.itemsCache.items.getItemByCD(self._vehicleCD)
            if not vehicle.isSecret:
                isEnabled = True
                if vehicle.isPreviewAllowed():
                    isEnabled = not self.prbDispatcher.getFunctionalState().isNavigationDisabled()
                    action = USER.VEHICLE_PREVIEW
                    label = MENU.contextmenu(USER.VEHICLE_PREVIEW)
                else:
                    action = USER.VEHICLE_INFO
                    label = MENU.contextmenu(USER.VEHICLE_INFO)
                options.append(self._makeItem(action, label, optInitData={'enabled': isEnabled}))
        return options

    def _isAppealsForTopicEnabled(self, topic):
        topicID = DENUNCIATIONS_MAP[topic]
        return self._denunciator.isAppealsForTopicEnabled(self.databaseID, topicID, self._arenaUniqueID)

    def _getSubmenuData(self):
        if self._isAlly or self._arenaGuiType in (ARENA_GUI_TYPE.UNKNOWN, ARENA_GUI_TYPE.TRAINING):
            order = DENUNCIATIONS.ORDER
        else:
            order = DENUNCIATIONS.ENEMY_ORDER
        make = self._makeItem
        return [ make(denunciation, MENU.contextmenu(denunciation), optInitData={'enabled': self._isAppealsForTopicEnabled(denunciation)}) for denunciation in order ]

    def _createSubMenuItem(self):
        labelStr = u'{} {}/{}'.format(i18n.makeString(MENU.CONTEXTMENU_APPEAL), self._denunciator.getDenunciationsLeft(), DENUNCIATIONS_PER_DAY)
        return self._makeItem(DENUNCIATIONS.APPEAL, labelStr, optInitData={'enabled': self._denunciator.isAppealsEnabled()}, optSubMenu=self._getSubmenuData())


class UserVehicleCMHandler(AppealCMHandler):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def compareVehicle(self):
        vehicleCD = getValidVehicleCDForNationChange(self._vehicleCD)
        self.comparisonBasket.addVehicle(vehicleCD)

    def _getHandlers(self):
        handlers = super(UserVehicleCMHandler, self)._getHandlers()
        handlers.update({_EXTENDED_OPT_IDS.VEHICLE_COMPARE: 'compareVehicle'})
        return handlers

    def _generateOptions(self, ctx=None):
        options = super(AppealCMHandler, self)._generateOptions(ctx)
        self._manageVehCompareOptions(options)
        return options

    def _manageVehCompareOptions(self, options):
        if self.comparisonBasket.isEnabled():
            options.insert(2, self._makeItem(_EXTENDED_OPT_IDS.VEHICLE_COMPARE, MENU.contextmenu(_EXTENDED_OPT_IDS.VEHICLE_COMPARE), {'enabled': self.comparisonBasket.isReadyToAdd(self.itemsCache.items.getItemByCD(self._vehicleCD))}))


class CustomUserCMHandler(BaseUserCMHandler):

    def __init__(self, cmProxy, ctx=None):
        super(CustomUserCMHandler, self).__init__(cmProxy, ctx=ctx)
        self.__customOptions = ctx.customItems
        self.__excludedOptions = ctx.excludedItems
        self.__customOptionsAfterEnd = ctx.customItemsAfterEnd
        self.__optionSelected = False
        self.onSelected = Event(self._eManager)

    def fini(self):
        if not self.__optionSelected:
            self.onSelected(None)
        super(CustomUserCMHandler, self).fini()
        return

    def onOptionSelect(self, optionId):
        self.__optionSelected = True
        self.onSelected(optionId)
        if optionId not in self.__customOptions and optionId not in self.__customOptionsAfterEnd:
            super(CustomUserCMHandler, self).onOptionSelect(optionId=optionId)

    def _generateOptions(self, ctx=None):
        options = super(CustomUserCMHandler, self)._generateOptions(ctx)
        options = self._addCustomInfo(options)
        options = self._excludeOptions(options)
        return options

    def _addCustomInfo(self, options):
        customOptions = []
        if self.__customOptions:
            for optID, label, enabled in self.__customOptions:
                customOptions.append(self._makeItem(optID, label, optInitData={'enabled': enabled}, iconType=_CM_ICONS.get(optID, '')))

            customOptions.append(self._makeSeparator())
            options = customOptions + options
        if self.__customOptionsAfterEnd:
            options.append(self._makeSeparator())
            for optID, label, enabled in self.__customOptionsAfterEnd:
                options.append(self._makeItem(optID, label, optInitData={'enabled': enabled}, iconType=_CM_ICONS.get(optID, '')))

        return options

    def _excludeOptions(self, options):
        excludedOptions = self.__excludedOptions
        options = [ opt for opt in options if opt['id'] not in excludedOptions ]
        return options


class UserContextMenuInfo(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, databaseID, userName, clanAbbrev):
        self.user = self.__getUser(databaseID, userName, clanAbbrev)
        self.databaseID = databaseID
        self.isBot = databaseID <= 0
        self.canAddToIgnore = True
        self.canDoDenunciations = True
        self.isFriend = False
        self.isIgnored = False
        self.isTemporaryIgnored = False
        self.isMuted = False
        self.hasClan = False
        self.userName = userName
        self.displayName = userName
        self.isOnline = False
        self.isCurrentPlayer = False
        if self.user is not None:
            self.isFriend = self.user.isFriend()
            self.isIgnored = self.user.isIgnored()
            self.isTemporaryIgnored = self.user.isTemporaryIgnored()
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
        return self.lobbyContext.getServerSettings().roaming.isSameRealm(self.databaseID)

    @property
    def canCreateChannel(self):
        roaming = self.lobbyContext.getServerSettings().roaming
        if g_settings.server.XMPP.isEnabled():
            canCreate = roaming.isSameRealm(self.databaseID)
        else:
            canCreate = not roaming.isInRoaming() and not roaming.isPlayerInRoaming(self.databaseID) and self.isOnline
        return canCreate

    def getTags(self):
        return self.user.getTags() if self.user is not None else set()

    def getNote(self):
        return self.user.getNote() if self.user is not None else ''

    def __getUser(self, dbId, username, clanAbbrev):
        user = self.usersStorage.getUser(dbId)
        if user is None:
            user = SharedUserEntity(dbId, name=username, clanInfo=UserClanInfo(abbrev=clanAbbrev), scope=UserEntityScope.LOBBY, tags={USER_TAG.SEARCH, USER_TAG.TEMP})
            self.usersStorage.addUser(user)
        return user
