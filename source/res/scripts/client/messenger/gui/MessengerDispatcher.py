# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/MessengerDispatcher.py
# Compiled at: 2011-11-23 12:32:03
import BigWorld
from chat_shared import CHAT_ACTIONS, CHAT_RESPONSES
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING, LOG_UNEXPECTED
from helpers import i18n
from helpers.time_utils import makeLocalServerTime
from messenger import g_settings, MESSENGER_I18N_FILE, getOperationInCooldownMsg
from messenger.ChannelsManager import ChannelsManager
from messenger.PrebattleInvitesManager import PrebattleInvitesManager
from messenger.ServiceChannelManager import ServiceChannelManager
from messenger.UsersManager import UsersManager
from messenger.common import MessangerSubscriber
from messenger.exeptions import ChannelNotFound
from messenger import filters
from messenger.gui.interfaces import DispatcherProxyHolder
from messenger.wrappers import ChatActionWrapper, MemberWrapper
import weakref
g_instance = None

class MessengerDispatcher(MessangerSubscriber):
    battleMessenger = property(lambda self: self.__battleWindow)
    lobbyMessenger = property(lambda self: self.__lobbyWindow)
    currentWindow = property(lambda self: self.__currentWindow)
    requestCreatePrb = None

    def __init__(self, lobbyWindowClass, battleWindowClass):
        MessangerSubscriber.__init__(self)
        self.channels = ChannelsManager()
        self.users = UsersManager()
        self.serviceChannel = ServiceChannelManager()
        self.invites = PrebattleInvitesManager(weakref.proxy(self.users))
        DispatcherProxyHolder._dispatcherProxy = weakref.proxy(self)
        g_settings.readUserPreference()
        self.__showJoinLeaveMessages = g_settings.userPreferences['showJoinLeaveMessages']
        self.__lobbyWindow = lobbyWindowClass()
        self.__lobbyWindowName = 'MessengerLobbyWindow{0:d}'.format(id(self.__lobbyWindow))
        self.__battleWindow = battleWindowClass()
        self.__battleWindowName = 'MessengerBattleWindow{0:d}'.format(id(self.__battleWindow))
        self.__windowParent = None
        self.__currentWindow = self.__lobbyWindow
        self.__currentWindowName = self.__lobbyWindowName
        self.__connected = False
        self.__battleMode = False
        self.__initI18nMessages()
        self.__prebattleChannel = None
        self.__initFilterChain()
        self.__initSupportedProtocols()
        return

    def __initFilterChain(self):
        self._filterChain = filters.FilterChain()
        if g_settings.userPreferences['enableOlFilter']:
            self._filterChain.addFilter('olFilter', filters.ObsceneLanguageFilter())
        if g_settings.userPreferences['enableSpamFilter']:
            self._filterChain.addFilter('spamFilter', filters.SpamFilter())
            self._filterChain.addFilter('floodFilter', filters.FloodFilter())

    def __initSupportedProtocols(self):
        self._protoPlugins = []
        for plugin in g_settings.supportedProtocols.itervalues():
            try:
                imported = __import__('messenger.gui.{0:>s}'.format(plugin), fromlist=[plugin])
                clazz = getattr(imported, plugin)
                if clazz is not None:
                    self._protoPlugins.append(clazz())
                else:
                    LOG_ERROR('Messenger: plugin not found, ', plugin)
            except ImportError as msg:
                LOG_ERROR('Messenger: plugin not found, ', msg)

        return

    def __initI18nMessages(self):
        self.__i18nMessages = {}
        self.__i18nMessages.setdefault('events', {})
        self.__i18nMessages['events']['enterChannel'] = i18n.makeString('#%s:events/enterChannel' % MESSENGER_I18N_FILE)
        self.__i18nMessages['events']['leaveChannel'] = i18n.makeString('#%s:events/leaveChannel' % MESSENGER_I18N_FILE)
        prefix = '#' + MESSENGER_I18N_FILE + ':server/errors/%s/%s'
        self.__i18nMessages.setdefault('serverErrors', {})
        for name in CHAT_RESPONSES:
            title = i18n.makeString(prefix % (name, 'title'))
            message = i18n.makeString(prefix % (name, 'message'))
            self.__i18nMessages['serverErrors'][name] = (title, message)

    def __hide(self):
        self.__currentWindow.close()

    def __setBattleMode(self, mode):
        if self.__battleMode ^ mode:
            self.__battleMode = mode
            self.__currentWindow.close()
            if mode:
                self.__currentWindow = self.__battleWindow
                self.__currentWindowName = self.__battleWindowName
            else:
                self.__currentWindow = self.__lobbyWindow
                self.__currentWindowName = self.__lobbyWindowName
            self.__currentWindow.show()

    def _getCurrent(self, cid):
        if self.channels.isBattle(cid):
            return self.__battleWindow
        return self.__lobbyWindow

    def editing(self):
        return self.__currentWindow.editing()

    def subscribeToPlayerEvents(self):
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountBecomeNonPlayer += self.__hide
        g_playerEvents.onAvatarBecomeNonPlayer += self.__hide
        g_playerEvents.onAccountShowGUI += self.__pe_onAccountShowGUI
        g_playerEvents.onClanMembersListChanged += self.__pe_onClanMembersListChanged
        if g_settings.lobbySettings['forseDestroyPrebattleChannel']:
            g_playerEvents.onPrebattleLeft += self.__pe_onPrebattleLeft
            g_playerEvents.onKickedFromPrebattle += self.__pe_onKickedFromPrebattle

    def unsubscribeFromPlayerEvents(self):
        from PlayerEvents import g_playerEvents
        g_playerEvents.onAccountBecomeNonPlayer -= self.__hide
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__hide
        g_playerEvents.onAccountShowGUI -= self.__pe_onAccountShowGUI
        g_playerEvents.onClanMembersListChanged -= self.__pe_onClanMembersListChanged
        if g_settings.lobbySettings['forseDestroyPrebattleChannel']:
            g_playerEvents.onPrebattleLeft -= self.__pe_onPrebattleLeft
            g_playerEvents.onKickedFromPrebattle -= self.__pe_onKickedFromPrebattle

    def subscribeToActions(self):
        self.subscribeAction(self.onSelfEnterChat, CHAT_ACTIONS.selfEnter)
        self.subscribeAction(self.onEnterChat, CHAT_ACTIONS.enter)
        self.subscribeAction(self.onBroadcast, CHAT_ACTIONS.broadcast)
        self.subscribeAction(self.onSelfLeaveChat, CHAT_ACTIONS.selfLeave)
        self.subscribeAction(self.onChannelDestroyed, CHAT_ACTIONS.channelDestroyed)
        self.subscribeAction(self.onLeaveChat, CHAT_ACTIONS.leave)
        self.subscribeAction(self.onMemberStatusUpdate, CHAT_ACTIONS.memberStatusUpdate)
        self.subscribeAction(self.onReceiveMembersCount, CHAT_ACTIONS.receiveMembersCount)
        self.subscribeAction(self.onReceiveMembersDelta, CHAT_ACTIONS.receiveMembersDelta)
        self.channels.subscribeToActions()
        self.users.subscribeToActions()
        self.serviceChannel.subscribeToActions()

    def unsubscribeFromActions(self):
        self.unsubcribeAllActions()
        self.channels.unsubcribeAllActions()
        self.users.unsubcribeAllActions()
        self.serviceChannel.unsubcribeAllActions()

    def _onConnect(self):
        if not self.__connected:
            self.__connected = True
            g_settings.onApplyUserPreferences += self.__onApplyUserPreferences
            self.subscribeToActions()
            self.subscribeToPlayerEvents()
            self.invites.init()
            for plugin in self._protoPlugins:
                plugin.connect()

    def onLobbyConnect(self):
        self.__setBattleMode(False)
        self._onConnect()
        self.users.requestUsersRoster()
        self.users.requestFriendStatus()
        self.serviceChannel.requestLastServiceMessages()

    def onBattleConnect(self):
        player = BigWorld.player()
        playerDbId = player.arena.vehicles.get(player.playerVehicleID, {}).get('accountDBID', -1L)
        self.users._cp_playerDbId = playerDbId
        self.__setBattleMode(True)
        self._onConnect()

    def onDisconnect(self):
        self.serviceChannel.clear()
        if not self.__connected:
            return
        self.__connected = False
        self.checkStates()
        g_settings.onApplyUserPreferences -= self.__onApplyUserPreferences
        self.unsubscribeFromActions()
        self.unsubscribeFromPlayerEvents()
        for plugin in self._protoPlugins:
            plugin.disconnect()

        self.__lobbyWindow.clear()
        self.__battleWindow.clear()
        self.channels.clear()
        self.users.clear()
        self.invites.clear()

    def onBroadcast(self, chatAction):
        """
        Event handler.
        When player post message to channel, adds message to this channel
        """
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        currentWindow = self._getCurrent(cid)
        self._filterChain.chainIn(wrapper)
        if len(wrapper.data) == 0:
            return
        messageText = currentWindow.addChannelMessage(wrapper)
        if messageText:
            self.channels.addChannelMessage(cid, messageText)

    def onSelfEnterChat(self, chatAction):
        """
        Event handler.
        When current player enter to channel, adds page for this channel
        """
        LOG_DEBUG('onSelfEnterChat:%s' % (dict(chatAction),))
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        uid = wrapper.originator
        channel = self.channels.getChannel(cid)
        if not channel:
            raise ChannelNotFound(cid)
        self.channels._setJoinedFlag(cid, True)
        if channel.lazy:
            self.__lobbyWindow.setJoinedToLazyChannel(cid, True)
            return
        if not self.channels.hasExistMemeber(cid, uid):
            currentWindow = self._getCurrent(cid)
            self.channels.onJoinedToChannel(channel)
            if currentWindow.addChannel(channel):
                if channel.greeting:
                    self.channels.addChannelMessage(cid, channel.greeting)
                page = currentWindow.getChannelPage(cid)
                if page:
                    self.subscribeAction(self.onRequestChannelMemebers, CHAT_ACTIONS.requestMembers, cid)
                    self.channels.requestChannelMembers(cid)

    def onRequestChannelMemebers(self, chatAction):
        """
        Event handler.
        When other players enter to channel, adds players to given channel
        """
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        members = map(lambda memberData: MemberWrapper(**dict(memberData)), wrapper.data)
        self.channels._addMembers(cid, members)
        currentWindow = self._getCurrent(cid)
        page = currentWindow.getChannelPage(cid)
        if page:
            page.addMembers(members)

    def onEnterChat(self, chatAction):
        """
        Event handler.
        When other players enter to channel, adds players to given channel
        """
        action = dict(chatAction)
        wrapper = ChatActionWrapper(**action)
        cid = wrapper.channel
        uid = wrapper.originator
        if self.channels.isLazyChannel(cid):
            return
        if not self.channels.hasExistMemeber(cid, uid):
            member = MemberWrapper(id=uid, nickName=action.get('originatorNickName'))
            self.channels._addMember(cid, member)
            currentWindow = self._getCurrent(cid)
            page = currentWindow.getChannelPage(cid)
            if page and page.addMember(member):
                if self.__showJoinLeaveMessages:
                    wrapper.data = self.__i18nMessages['events']['enterChannel'] % member.nickName.encode('utf-8')
                    currentWindow.addSystemMessage(wrapper)

    def onSelfLeaveChat(self, chatAction):
        """
        Event handler.
        When current player exit from channel, remove page for this channel
        """
        LOG_DEBUG('onSelfLeaveChat:%s' % (dict(chatAction),))
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        uid = wrapper.originator
        if self.channels.isLazyChannel(cid):
            self.channels._setJoinedFlag(cid, False)
            self.__lobbyWindow.setJoinedToLazyChannel(cid, False)
            return
        currentWindow = self._getCurrent(cid)
        if self.channels.hasExistMemeber(cid, uid):
            self.channels._removeChannel(cid, clearChannelInfo=False)
            self.unsubscribeAction(self.onRequestChannelMemebers, CHAT_ACTIONS.requestMembers, cid)
            currentWindow.removeChannel(cid)

    def onChannelDestroyed(self, chatAction):
        """
        Event handler.
        Destruction of the channel on the server
        """
        LOG_DEBUG('onChannelDestroyed:%s' % (dict(chatAction),))
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        if self.channels.isLazyChannel(cid):
            LOG_UNEXPECTED('Received "CHAT_ACTIONS.channelDestroyed" for lazy channel', dict(chatAction))
        currentWindow = self._getCurrent(cid)
        if self.channels.getChannel(cid):
            self.channels._removeChannel(cid)
            currentWindow.removeChannel(cid)

    def onLeaveChat(self, chatAction):
        """
        Event handler.
        When other players exit from channel, remove players to given channel
        """
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        uid = wrapper.originator
        if self.channels.isLazyChannel(cid):
            return
        if self.channels._removeMemeber(cid, uid):
            currentWindow = self._getCurrent(cid)
            page = currentWindow.getChannelPage(cid)
            if page and page.removeMember(uid):
                if self.__showJoinLeaveMessages:
                    wrapper.data = self.__i18nMessages['events']['leaveChannel'] % wrapper.originatorNickName.encode('utf-8')
                    currentWindow.addSystemMessage(wrapper)

    def onMemberStatusUpdate(self, chatAction):
        """
        Event handler.
        Update on status of the player: in battle or in the lobby
        @deprecated: large overhead on the server side
        """
        wrapper = ChatActionWrapper(**dict(chatAction))
        status = int(wrapper.data)
        cid = wrapper.channel
        uid = wrapper.originator
        self.channels._setMemberStatus(cid, uid, status)
        currentWindow = self._getCurrent(cid)
        page = currentWindow.getChannelPage(cid)
        if page:
            page.setMemberStatus(uid, status)

    def onReceiveMembersCount(self, chatAction):
        pass

    def onReceiveMembersDelta(self, chatAction):
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        added = []
        removed = []
        for uid, data in wrapper.data:
            if data[0] == 1:
                added.append(MemberWrapper(id=uid, nickName=data[1], status=data[2]))
            elif data[0] == 0:
                removed.append(MemberWrapper(id=uid, nickName=data[1], status=data[2]))

        currentWindow = self._getCurrent(cid)
        page = currentWindow.getChannelPage(cid)
        if len(added):
            if self.channels._addMembers(cid, added) and page:
                page.addMembers(added)
                if self.__showJoinLeaveMessages:
                    playersName = BigWorld.player().name
                    for itm in added:
                        if itm.nickName != playersName:
                            wrapper.data = self.__i18nMessages['events']['enterChannel'] % itm.nickName.encode('utf-8')
                            currentWindow.addSystemMessage(wrapper)

        if len(removed):
            if self.channels._removeMembers(cid, removed) and page:
                page.removeMembers(removed)
                if self.__showJoinLeaveMessages:
                    playersName = BigWorld.player().name
                    for itm in removed:
                        if itm.nickName != playersName:
                            wrapper.data = self.__i18nMessages['events']['leaveChannel'] % itm.nickName.encode('utf-8')
                            currentWindow.addSystemMessage(wrapper)

    def onChatActionFailure(self, chatAction):
        """
        Event handler. Failed to work with the channel.
        """
        actionResponse = CHAT_RESPONSES[chatAction['actionResponse']]
        LOG_DEBUG('onChatActionFailure', dict(chatAction))
        for name in ('channels', 'users', 'invites'):
            manager = getattr(self, name)
            if manager.handleChatActionFailureEvent(actionResponse, dict(chatAction)):
                return

        responseProcessor = self.__responseHandlers.get(actionResponse, self.__defaultResponseHandler)
        if hasattr(self, responseProcessor):
            getattr(self, responseProcessor)(chatAction)
        else:
            LOG_ERROR('onChatActionFailure: response processor for response %s(%s) not registered' % (actionResponse, actionResponse.index()))

    def handleChannelMessageInput(self, cid, message):
        message = self._filterChain.chainOut(message)
        if not len(message):
            return
        for plugin in self._protoPlugins:
            if plugin.broadcast(cid, message):
                return

        if BigWorld.player() and hasattr(BigWorld.player(), 'broadcast'):
            BigWorld.player().broadcast(cid, message)

    __responseHandlers = {CHAT_RESPONSES.channelNotExists: '_MessengerDispatcher__onChannelNotExists',
     CHAT_RESPONSES.memberBanned: '_MessengerDispatcher__onMemberBanned',
     CHAT_RESPONSES.chatBanned: '_MessengerDispatcher__onChatBanned',
     CHAT_RESPONSES.actionInCooldown: '_MessengerDispatcher__onActionInCooldown',
     CHAT_RESPONSES.commandInCooldown: '_MessengerDispatcher__onCommandInCooldown'}
    __defaultResponseHandler = '_MessengerDispatcher__onResponse'

    def __onChannelNotExists(self, chatAction):
        channelId = chatAction['channel']
        LOG_DEBUG('channelId:%s' % (channelId,))
        self.onChannelDestroyed(chatAction)

    def __onMemberBanned(self, chatAction):
        message = self.__i18nMessages['serverErrors'][CHAT_RESPONSES.memberBanned.name()]
        banInfo = chatAction['data']
        banEndTime = makeLocalServerTime(banInfo.get('banEndTime', None))
        if banEndTime is None:
            if banEndTime in banInfo:
                del banInfo['banEndTime']
            bannedMessage = i18n.makeString('#chat:errors/bannedpermanent', **banInfo)
        else:
            banInfo['banEndTime'] = BigWorld.wg_getLongDateFormat(banEndTime) + ' ' + BigWorld.wg_getShortTimeFormat(banEndTime)
            bannedMessage = i18n.makeString('#chat:errors/banned', **banInfo)
        self.__currentWindow.showActionFailureMessage(bannedMessage, title=message[0], modal=True)
        return

    def __onChatBanned(self, chatAction):
        message = self.__i18nMessages['serverErrors'][CHAT_RESPONSES.chatBanned.name()]
        banInfo = chatAction['data']
        banEndTime = makeLocalServerTime(banInfo.get('banEndTime', None))
        if banEndTime is None:
            if banEndTime in banInfo:
                del banInfo['banEndTime']
            bannedMessage = i18n.makeString('#chat:errors/chatbannedpermanent', **banInfo)
        else:
            banInfo['banEndTime'] = BigWorld.wg_getLongDateFormat(banEndTime) + ' ' + BigWorld.wg_getShortTimeFormat(banEndTime)
            bannedMessage = i18n.makeString('#chat:errors/chatbanned', **banInfo)
        self.__currentWindow.showActionFailureMessage(bannedMessage, title=message[0], modal=True)
        return

    def __onActionInCooldown(self, chatAction):
        """
        ignore actionInCooldown response
        """
        pass

    def __onCommandInCooldown(self, chatAction):
        chatActionDict = dict(chatAction)
        data = chatActionDict.get('data', {'command': None,
         'cooldownPeriod': -1})
        if data['command'] is not None:
            self.__currentWindow.showActionFailureMessage(getOperationInCooldownMsg(data['command'], data['cooldownPeriod']))
        else:
            LOG_ERROR('CommandInCooldown', chatActionDict)
        return

    def __onResponse(self, chatAction):
        actionResponse = CHAT_RESPONSES[chatAction['actionResponse']]
        if actionResponse is None:
            LOG_WARNING('__onResponse. action response index %d not found' % chatAction['actionResponse'])
            return
        else:
            message = self.__i18nMessages['serverErrors'][actionResponse.name()]
            auxInfo = chatAction['data'] if chatAction.has_key('data') else None
            if auxInfo is not None and isinstance(auxInfo, dict):
                for key, item in auxInfo.items():
                    if isinstance(item, basestring) and item.startswith('#'):
                        auxInfo[key] = i18n.makeString(item)

                try:
                    fullMessage = message[1] % auxInfo
                except TypeError:
                    LOG_WARNING('__onResponse. An exception occurred during message formating: %s %% (%s)' % (message[1], auxInfo))
                    fullMessage = message[1]

            else:
                fullMessage = message[1]
            self.__currentWindow.showActionFailureMessage(fullMessage, title=message[0], modal=True)
            return

    def __pe_onAccountShowGUI(self, ctx):
        if 'databaseID' in ctx:
            self.users._cp_playerDbId = ctx['databaseID']
        if g_settings.lobbySettings['forseDestroyPrebattleChannel'] and 'prebattleID' not in ctx:
            self.__forseRemovePrebattleChannels()

    def __pe_onPrebattleLeft(self):
        self.__forseRemovePrebattleChannels()

    def __pe_onKickedFromPrebattle(self, reasonCode):
        self.__forseRemovePrebattleChannels()

    def __pe_onClanMembersListChanged(self):
        self.users.setClanMembersList(BigWorld.player().clanMembers)

    def __forseRemovePrebattleChannels(self):
        list = self.channels.getPrebattleChannelList()
        for channel in list:
            cid = channel.cid
            channel.waitingDestroyedEvent = True
            currentWindow = self._getCurrent(cid)
            if self.channels.getChannel(cid):
                self.channels._removeChannel(cid, clearChannelInfo=False, waitingDestroyedEvent=True)
                currentWindow.removeChannel(cid)

    def checkStates(self):
        settings = g_settings.debugSettings
        if settings['dumpWaitingToDestroyChannels']:
            list = self.channels.getWaitinigToDestroyChannelList()
            if len(list) > 0:
                LOG_UNEXPECTED('Channels did not receive event CHAT_ACTIONS.channelDestroyed', list)

    def __onApplyUserPreferences(self):
        self.__showJoinLeaveMessages = g_settings.userPreferences['showJoinLeaveMessages']
        if g_settings.userPreferences['enableOlFilter']:
            if not self._filterChain.hasFilter('enableOlFilter'):
                self._filterChain.addFilter('olFilter', filters.ObsceneLanguageFilter(), removed=['coloringOlFilter'])
        elif self.users.cp_canViewColoringBadWords() and not self._filterChain.hasFilter('coloringOlFilter'):
            self._filterChain.addFilter('coloringOlFilter', filters.ColoringObsceneLanguageFilter(self.users), removed=['olFilter'])
        else:
            self._filterChain.removeFilter('olFilter')
        if g_settings.userPreferences['enableSpamFilter']:
            self._filterChain.addFilter('spamFilter', filters.SpamFilter())
            self._filterChain.addFilter('floodFilter', filters.FloodFilter())
        else:
            self._filterChain.removeFilter('spamFilter')
            self._filterChain.removeFilter('floodFilter')

    def setAccountsAttrs(self, attrs):
        if self.users._cp_accountAttrs ^ attrs:
            self.users._cp_accountAttrs = attrs
            if self.users.cp_canViewColoringBadWords():
                if not g_settings.userPreferences['enableOlFilter'] and not self._filterChain.hasFilter('coloringOlFilter'):
                    self._filterChain.addFilter('coloringOlFilter', filters.ColoringObsceneLanguageFilter(self.users), removed=['olFilter'])
            else:
                self._filterChain.removeFilter('coloringOlFilter')

    def setClanInfo(self, clanInfo):
        self.users.setClanInfo(clanInfo)
