# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/player_menu_handler.py
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.battle_control.arena_info.settings import INVITATION_DELIVERY_STATUS as _D_STATUS
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.denunciator import DENUNCIATIONS, BattleDenunciator, DENUNCIATIONS_MAP
from helpers import dependency
from helpers import i18n
from constants import DENUNCIATIONS_PER_DAY, IS_CHINA
from messenger.m_constants import PROTO_TYPE, UserEntityScope
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.player_satisfaction_rating.loggers import InBattleContextMenuLogger
from uilogging.player_satisfaction_rating.logging_constants import PlayerSatisfactionRatingCMActions

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
 DENUNCIATIONS.INCORRECT_BEHAVIOR: 'appealIncorrectBehavior',
 DENUNCIATIONS.NOT_FAIR_PLAY: 'appealNotFairPlay',
 DENUNCIATIONS.FORBIDDEN_NICK: 'appealForbiddenNick',
 DENUNCIATIONS.BOT: 'appealBot',
 DYN_SQUAD_OPTION_ID.SENT_INVITATION: 'sendInvitation',
 DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION: 'acceptInvitation',
 DYN_SQUAD_OPTION_ID.REJECT_INVITATION: 'rejectInvitation'}
if not IS_CHINA:
    _OPTIONS_HANDLERS.update({USER.SET_MUTED: 'setMuted',
     USER.UNSET_MUTED: 'unsetMuted'})
_OPTION_ICONS = {USER.ADD_TO_FRIENDS: 'addToFriends',
 USER.REMOVE_FROM_FRIENDS: 'removeFromFriends',
 USER.ADD_TO_IGNORED: 'addToBlacklist',
 USER.REMOVE_FROM_IGNORED: 'removeFromBlacklist',
 BATTLE_CHAT_OPTION_ID.ENABLE_COMMUNICATIONS: 'enableCommunications',
 BATTLE_CHAT_OPTION_ID.DISABLE_COMMUNICATIONS: 'disableCommunications',
 DYN_SQUAD_OPTION_ID.SENT_INVITATION: 'addToSquad',
 DYN_SQUAD_OPTION_ID.IN_SQUAD: 'inSquad',
 DYN_SQUAD_OPTION_ID.ACCEPT_INVITATION: 'acceptInvitation',
 DYN_SQUAD_OPTION_ID.REJECT_INVITATION: 'rejectInvitation'}
if not IS_CHINA:
    _OPTION_ICONS.update({USER.SET_MUTED: 'disableVoice',
     USER.UNSET_MUTED: 'enableVoice'})
_BOT_NO_ACTIONS_OPTION_ID = 'botNoActions'

class PlayerContextMenuInfo(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('avatarSessionID', 'isBot', 'isFriend', 'isIgnored', 'isTemporaryIgnored', 'isMuted', 'userName', 'isAlly', 'battleUser')

    def __init__(self, avatarSessionID, userName):
        super(PlayerContextMenuInfo, self).__init__()
        self.avatarSessionID = avatarSessionID
        self.isBot = not avatarSessionID
        self.isFriend = False
        self.isIgnored = False
        self.isTemporaryIgnored = False
        self.isMuted = False
        self.userName = userName
        self.isAlly = self.sessionProvider.getCtx().isAlly(avatarSessionID=avatarSessionID)
        self.battleUser = self.usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
        if self.battleUser is not None:
            self.isFriend = self.battleUser.isFriend()
            self.isIgnored = self.battleUser.isIgnored()
            self.isTemporaryIgnored = self.battleUser.isTemporaryIgnored()
            self.isMuted = self.battleUser.isMuted()
        return

    @storage_getter('users')
    def usersStorage(self):
        return None


class PlayerMenuHandler(AbstractContextMenuHandler):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, cmProxy, ctx=None):
        self.__denunciator = BattleDenunciator()
        self.__arenaUniqueID = BattleDenunciator.getArenaUniqueID()
        self._uiPlayerSatisfactionRatingLogger = InBattleContextMenuLogger()
        self._uiPlayerSatisfactionRatingLogger.onViewInitialize()
        g_eventBus.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(PlayerMenuHandler, self).__init__(cmProxy, ctx=ctx, handlers=_OPTIONS_HANDLERS)

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    def fini(self):
        g_eventBus.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.__denunciator = None
        self._uiPlayerSatisfactionRatingLogger.onViewFinalize()
        super(PlayerMenuHandler, self).fini()
        return

    def addFriend(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.FRIEND_ACTION)
        self.sessionProvider.shared.anonymizerFakesCtrl.addBattleFriend(self.__userInfo.avatarSessionID)

    def removeFriend(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.FRIEND_ACTION)
        self.sessionProvider.shared.anonymizerFakesCtrl.removeBattleFriend(self.__userInfo.avatarSessionID)

    def setIgnored(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.BLACKLIST)
        self.sessionProvider.shared.anonymizerFakesCtrl.addBattleIgnored(self.__userInfo.avatarSessionID)

    def unsetIgnored(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.BLACKLIST)
        self.sessionProvider.shared.anonymizerFakesCtrl.removeBattleIgnored(self.__userInfo.avatarSessionID)

    def disableCommunications(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.BLACKLIST)
        self.sessionProvider.shared.anonymizerFakesCtrl.addTmpIgnored(self.__userInfo.avatarSessionID, self.__userInfo.userName)

    def enableCommunications(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.BLACKLIST)
        self.sessionProvider.shared.anonymizerFakesCtrl.removeTmpIgnored(self.__userInfo.avatarSessionID)

    def setMuted(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.VOICE_MESSAGES)
        self.sessionProvider.shared.anonymizerFakesCtrl.mute(self.__userInfo.avatarSessionID, self.__userInfo.userName)

    def unsetMuted(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.VOICE_MESSAGES)
        self.sessionProvider.shared.anonymizerFakesCtrl.unmute(self.__userInfo.avatarSessionID)

    def appealIncorrectBehavior(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.COMPLAIN)
        self.__denunciator.makeAppeal(self.__vInfo.vehicleID, self.__userInfo.userName, DENUNCIATIONS.INCORRECT_BEHAVIOR, self.__arenaUniqueID)

    def appealNotFairPlay(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.COMPLAIN)
        self.__denunciator.makeAppeal(self.__vInfo.vehicleID, self.__userInfo.userName, DENUNCIATIONS.NOT_FAIR_PLAY, self.__arenaUniqueID)

    def appealForbiddenNick(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.COMPLAIN)
        self.__denunciator.makeAppeal(self.__vInfo.vehicleID, self.__userInfo.userName, DENUNCIATIONS.FORBIDDEN_NICK, self.__arenaUniqueID)

    def appealBot(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.COMPLAIN)
        self.__denunciator.makeAppeal(self.__vInfo.vehicleID, self.__userInfo.userName, DENUNCIATIONS.BOT, self.__arenaUniqueID)

    def sendInvitation(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.CREATE_PLATOON)
        self.sessionProvider.invitations.send(self.__userInfo.avatarSessionID)

    def acceptInvitation(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.UNTRACKED_ACTION)
        self.sessionProvider.invitations.accept(self.__userInfo.avatarSessionID)

    def rejectInvitation(self):
        self._uiPlayerSatisfactionRatingLogger.setContextMenuAction(PlayerSatisfactionRatingCMActions.UNTRACKED_ACTION)
        self.sessionProvider.invitations.reject(self.__userInfo.avatarSessionID)

    def _initFlashValues(self, ctx):
        self.__vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(ctx.vehicleID)
        player = self.__vInfo.player
        self.__userInfo = PlayerContextMenuInfo(player.avatarSessionID, player.name)

    def _clearFlashValues(self):
        self.__userInfo = None
        self.__vInfo = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        if self.sessionProvider.isReplayPlaying:
            return options
        if not self.__userInfo.isBot:
            options = self.__addDynSquadInfo(options)
            options = self.__addFriendshipInfo(options)
            options = self.__addIgnoreInfo(options)
            options = self.__addCommunicationInfo(options)
            if not IS_CHINA:
                options = self.__addMutedInfo(options)
            options = self.__addDenunciationsInfo(options)
        else:
            options = self.__addBotInfo(options)
        return options

    @classmethod
    def _getOptionIcon(cls, optionID):
        return _OPTION_ICONS.get(optionID, '')

    @classmethod
    def _getOptionInitData(cls, optionID, isEnabled=True):
        return {'enabled': isEnabled,
         'iconType': cls._getOptionIcon(optionID)}

    def __addDynSquadInfo(self, options):
        make = self._makeItem
        ctx = self.sessionProvider.getCtx()
        if not self.arenaVisitor.hasDynSquads():
            return options
        elif not ctx.isInvitationEnabled() or ctx.hasSquadRestrictions():
            return options
        elif not self.__userInfo.isAlly:
            return options
        else:
            isIgnored = self.__userInfo.isIgnored
            status = self.__vInfo.invitationDeliveryStatus
            if status & _D_STATUS.FORBIDDEN_BY_RECEIVER > 0 or status & _D_STATUS.RECEIVED_FROM > 0 and not status & _D_STATUS.RECEIVED_INACTIVE or status & _D_STATUS.SENT_TO > 0 and not status & _D_STATUS.SENT_INACTIVE:
                optionID = DYN_SQUAD_OPTION_ID.SENT_INVITATION
                isEnabled = False
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
        isEnabled = True
        if self.__userInfo.isFriend:
            optionID = USER.REMOVE_FROM_FRIENDS
        else:
            optionID = USER.ADD_TO_FRIENDS
        options.append(self._makeItem(optionID, MENU.contextmenu(optionID), optInitData=self._getOptionInitData(optionID, isEnabled)))
        return options

    def __addIgnoreInfo(self, options):
        isEnabled = True
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
        isForbiddenBattleType = self.arenaVisitor.gui.isTrainingBattle()
        if self.__userInfo.isAlly and not isForbiddenBattleType:
            isEnabled = True
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
        isVisible = self.bwProto.voipController.isVOIPEnabled() and (self.__userInfo.isAlly or self.arenaVisitor.gui.isTrainingBattle())
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
        return self.__denunciator.isAppealsForTopicEnabled(self.__vInfo.vehicleID, topicID, self.__arenaUniqueID)

    def __addDenunciationsInfo(self, options):
        make = self._makeItem
        if self.__userInfo.isAlly or self.arenaVisitor.gui.isTrainingBattle():
            order = DENUNCIATIONS.ORDER
        else:
            order = DENUNCIATIONS.ENEMY_ORDER
        sub = [ make(denunciation, MENU.contextmenu(denunciation), optInitData={'enabled': self.__isAppealsForTopicEnabled(denunciation)}) for denunciation in order ]
        label = '{} {}/{}'.format(i18n.makeString(MENU.CONTEXTMENU_APPEAL), self.__denunciator.getDenunciationsLeft(), DENUNCIATIONS_PER_DAY)
        options.append(make(DENUNCIATIONS.APPEAL, label, optInitData={'enabled': self.__denunciator.isAppealsEnabled()}, optSubMenu=sub))
        return options

    def __addBotInfo(self, options):
        options.append(self._makeItem(_BOT_NO_ACTIONS_OPTION_ID, MENU.contextmenu(_BOT_NO_ACTIONS_OPTION_ID), optInitData=self._getOptionInitData(_BOT_NO_ACTIONS_OPTION_ID, False)))
        return options

    def __handleHideCursor(self, _):
        self.onContextMenuHide()
