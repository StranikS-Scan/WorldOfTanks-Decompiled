# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/MessengerLobbyInterface.py
# Compiled at: 2011-11-29 13:57:51
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.utils import dossiers_utils
from messenger import g_settings, LAZY_CHANNELS, MESSAGE_MAX_LENGTH, MESSENGER_I18N_FILE
from messenger import isBroadcatInCooldown, BROADCAST_COOL_DOWN_MESSAGE
from messenger.ChannelsManager import CREATE_CHANNEL_RESULT
from messenger.gui.interfaces import MessengerWindowInterface
from messenger.gui.Scalefrom.FAQInterface import FAQInterface
from messenger.gui.Scalefrom import C_COMMANDS, CHMS_COMMANDS, WP_COMMANDS
from messenger.gui.Scalefrom import lobby_page_interfaces as pages
from messenger.gui.Scalefrom.InvitesInterface import InvitesInterface
from messenger.gui.Scalefrom.JoinedChannelsInterface import JoinedChannelsInterface
from messenger.gui.Scalefrom.search_interfaces import SearchChannelsInterface, SearchUsersInterface
from messenger.gui.Scalefrom.ServiceChannelInterface import ServiceChannelInterface
from messenger.gui.Scalefrom.users_interfaces import UsersRosterInterface
import weakref, BigWorld
from adisp import process

class MessengerLobbyInterface(MessengerWindowInterface):
    __channelsWindow = {}
    __managementWindow = {}

    def __init__(self):
        self.__active = False
        self.__initCallbacks = False
        self.__movieViewHandler = None
        self.__channelPages = {}
        self.__joinedChannels = JoinedChannelsInterface()
        self.__searchChannels = SearchChannelsInterface()
        self.__searchUsers = SearchUsersInterface()
        self.__usersRoster = UsersRosterInterface()
        self.__serviceChannel = ServiceChannelInterface()
        self.__invitesInterface = InvitesInterface()
        self.__faq = FAQInterface()
        return

    def populateUI(self, handler):
        self.show()
        persistens = g_settings.userPreferences['windowsPersistens']
        self.__channelsWindow = persistens['channels']
        self.__managementWindow = persistens['management']
        proxy = weakref.proxy(handler)
        self.__movieViewHandler = proxy
        self.__initCallbacks = True
        self.__joinedChannels.populateUI(proxy)
        for page in self.__channelPages.values():
            page.populateUI(self.__movieViewHandler)

        channelsInfo = filter(lambda item: item.cid not in self.__channelPages.keys(), self.channels.getChannelList())
        for info in channelsInfo:
            self.__createChannelPage(info)

        self.__searchChannels.populateUI(proxy)
        self.__searchUsers.populateUI(proxy)
        self.__usersRoster.populateUI(proxy)
        self.__serviceChannel.populateUI(proxy)
        self.__invitesInterface.populateUI(proxy)
        self.__faq.populateUI(proxy)
        self.__onReceiveLazyChannels(self.channels.getLazyChannelList())
        self.channels.onConnectingToSecureChannel += self.__onConnectingToSecureChannel
        self.channels.onReceiveLazyChannels += self.__onReceiveLazyChannels
        self.users.onUsersRosterUpdate += self.__onUsersRosterUpdate
        self.users.onDenunciationReceived += self.__onDenunciationReceived
        self.users.onAccountDossierRequest += self.onAccountDossierRequest
        self.users.onVehicleDossierRequest += self.onVehicleDossierRequest
        g_settings.onApplyUserPreferences += self.__onApplyUserPreferences
        self.__movieViewHandler.addExternalCallbacks({C_COMMANDS.PopulateUI(): self.onPopulateUI,
         C_COMMANDS.JoinToChannel(): self.onJoinToChannel,
         CHMS_COMMANDS.CheckCooldownPeriod(): self.onCheckCooldownPeriod,
         C_COMMANDS.CreateChannel(): self.onCreateChannel,
         C_COMMANDS.CreateChannelClientError(): self.onCreateChannelClientError,
         WP_COMMANDS.RequestChannelsPersistents(): self.onRequestChannelsPersistents,
         WP_COMMANDS.SetChannelPersistent(): self.onSetChannelPersistent,
         WP_COMMANDS.RequestManagementPersistents(): self.onRequestManagementPersistents,
         WP_COMMANDS.SetManagementPersistent(): self.onSetManagementPersistent,
         'userInfo.close': self.onUserInfoClose})
        self.__movieViewHandler.call(C_COMMANDS.RefreshUI(), [MESSAGE_MAX_LENGTH])

    def dispossessUI(self):
        self.close()
        self.__storeWindowsPersistent()
        self.channels.onConnectingToSecureChannel -= self.__onConnectingToSecureChannel
        self.channels.onReceiveLazyChannels -= self.__onReceiveLazyChannels
        self.users.onAccountDossierRequest -= self.onAccountDossierRequest
        self.users.onVehicleDossierRequest -= self.onVehicleDossierRequest
        self.users.onDenunciationReceived -= self.__onDenunciationReceived
        self.users.onUsersRosterUpdate -= self.__onUsersRosterUpdate
        g_settings.onApplyUserPreferences -= self.__onApplyUserPreferences
        self.__movieViewHandler.removeExternalCallbacks(C_COMMANDS.PopulateUI(), C_COMMANDS.CreateChannel(), C_COMMANDS.CreateChannelClientError(), C_COMMANDS.JoinToChannel(), CHMS_COMMANDS.CheckCooldownPeriod(), WP_COMMANDS.RequestChannelsPersistents(), WP_COMMANDS.SetChannelPersistent(), WP_COMMANDS.RequestManagementPersistents(), WP_COMMANDS.SetManagementPersistent(), 'userInfo.close')
        self.__movieViewHandler = None
        for page in self.__channelPages.values():
            page.dispossessUI()

        self.__joinedChannels.dispossessUI()
        self.__searchChannels.dispossessUI()
        self.__searchUsers.dispossessUI()
        self.__usersRoster.dispossessUI()
        self.__serviceChannel.dispossessUI()
        self.__invitesInterface.dispossessUI()
        self.__faq.dispossessUI()
        return

    def show(self):
        self.__active = True

    def close(self):
        self.__active = False

    def clear(self):
        for _, page in self.__channelPages.iteritems():
            page.clear()

        self.__channelPages.clear()
        self.__joinedChannels.clear()
        self.channels.onConnectingToSecureChannel -= self.__onConnectingToSecureChannel
        self.channels.onReceiveLazyChannels -= self.__onReceiveLazyChannels
        self.users.onAccountDossierRequest -= self.onAccountDossierRequest
        self.users.onVehicleDossierRequest -= self.onVehicleDossierRequest
        self.users.onDenunciationReceived -= self.__onDenunciationReceived
        self.users.onUsersRosterUpdate -= self.__onUsersRosterUpdate

    def getChannelPage(self, cid):
        return self.__channelPages.get(cid)

    def addChannelMessage(self, message):
        cid = message.channel
        page = self.getChannelPage(cid)
        messageText = None
        if page:
            messageText = page.addMessage(message, format=True)
            if not self.channels.isLazyChannel(cid) and not self.__active:
                self.__joinedChannels.waiting(cid)
        return messageText

    def addSystemMessage(self, message):
        page = self.getChannelPage(message.channel)
        if page:
            page.addMessage(message, format=False, system=True)

    def addChannel(self, channel):
        if self.__initCallbacks:
            self.__joinedChannels.refresh()
        self.__createChannelPage(channel)
        return True

    def removeChannel(self, cid):
        page = self.getChannelPage(cid)
        if page:
            page.clear()
            self.__channelPages.pop(cid)
        if self.__initCallbacks:
            self.__joinedChannels.remove(cid)

    def __createChannelPage(self, channel):
        cid = channel.cid
        if not self.getChannelPage(cid):
            clazz = pages.CommonPageInterface
            if channel.isClan:
                clazz = pages.ClanPageInterface
            elif channel.isSquad:
                clazz = pages.SquadPageInterface
            elif channel.isCompany:
                clazz = pages.CompanyPageInterface
            elif channel.isBattleSession:
                clazz = pages.BattleSessionPageInterface
            self.__channelPages[cid] = clazz(cid)
            if self.__initCallbacks and self.__movieViewHandler:
                self.__channelPages[cid].populateUI(self.__movieViewHandler)

    def __createLazyChannelPage(self, channel):
        cid = channel.cid
        if not self.getChannelPage(cid):
            clazz = pages.LazyPageInterface
            if channel.lazy == LAZY_CHANNELS.COMPANIES[0]:
                clazz = pages.CompaniesPageInterface
            elif channel.lazy == LAZY_CHANNELS.SPECIAL_BATTLES[0]:
                clazz = pages.BattleSessionsPageInterface
            self.__channelPages[cid] = clazz(cid)
            if self.__movieViewHandler:
                self.__channelPages[cid].populateUI(self.__movieViewHandler)
        self.__channelPages[cid].setJoined(channel.joined)

    def showActionFailureMessage(self, message, title=None, modal=False):
        if modal and self.__movieViewHandler:
            self.__movieViewHandler.call(C_COMMANDS.AlertReceived(), ['error', title, message])
        else:
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)

    def setJoinedToLazyChannel(self, cid, joined):
        page = self.getChannelPage(cid)
        if page is not None:
            page.setJoined(joined)
        return

    def refreshChannelList(self):
        self.__joinedChannels.refresh()

    @process
    def onAccountDossierRequest(self, user):
        r = dossiers_utils.getUserDossier(user.userName)
        dossier = yield r.getAccountDossier()
        if dossier is None:
            if r.isHidden:
                self.__movieViewHandler.call(C_COMMANDS.ReceivedUserInfoFailed(), [i18n.makeString('#dialogs:messenger/userInfoHidden/message') % user.userName])
            else:
                self.__movieViewHandler.call('common.showMessageDialog', ['messenger/userInfoNotAvailable',
                 True,
                 False,
                 i18n.makeString('#dialogs:messenger/userInfoNotAvailable/message') % user.userName])
            return
        else:
            clanDBID, clanInfo = yield r.getClanInfo()
            title = i18n.makeString('#%s:dialogs/userInfo/title' % MESSENGER_I18N_FILE, user.displayName)
            userInfo = user.list()
            userInfo = [title, int(userInfo[0])] + userInfo[1:]
            vehList = dossiers_utils.getDossierVehicleList(dossier)
            userInfo.extend([dossier['creationTime'], dossier['lastBattleTime'], len(vehList)])
            userInfo.extend(vehList)
            achievList = dossiers_utils.getDossierMedals(dossier)
            userInfo.extend([len(achievList)])
            userInfo.extend(achievList)
            statsList = dossiers_utils.getDossierTotalBlocks(dossier)
            userInfo.extend([len(statsList)])
            userInfo.extend(statsList)
            userInfo.extend(dossiers_utils.getCommonInfo(user.userName, dossier, clanInfo, None))
            self.__movieViewHandler.call(C_COMMANDS.ReceivedUserInfo(), userInfo)
            if clanDBID is not None and clanDBID != 0:
                tID = 'userInfoForm' + BigWorld.player().name
                success = yield dossiers_utils.getClanEmblemTextureID(clanDBID, True, tID)
                if success:
                    self.__movieViewHandler.call(C_COMMANDS.ReceivedClanEmblem() + user.userName, [tID])
            return

    @process
    def onVehicleDossierRequest(self, user, vehicleID):
        r = dossiers_utils.getUserDossier(user.userName)
        if vehicleID == 'ALL':
            dossier = yield r.getAccountDossier()
            data = dossiers_utils.getDossierTotalBlocks(dossier)
        else:
            dossier = yield r.getVehicleDossier(int(float(vehicleID)))
            data = dossiers_utils.getDossierVehicleBlocks(dossier, int(float(vehicleID)))
        self.__movieViewHandler.call(C_COMMANDS.ReceivedVehicleStat() + user.userName, data)
        self.__movieViewHandler.call(C_COMMANDS.ReceivedAchievementsStat() + user.userName, dossiers_utils.getDossierMedals(dossier))

    def onUserInfoClose(self, cid, userName):
        LOG_DEBUG('Close user dossier cache: %s' % str(userName))
        dossiers_utils.closeUserDossier(userName)

    def onPopulateUI(self, *args):
        settings = g_settings.lobbySettings
        userPrefs = g_settings.userPreferences
        parser = CommandArgsParser(self.onPopulateUI.__name__)
        parser.parse(*args)
        parser.addArg(MESSAGE_MAX_LENGTH)
        parser.addArgs([settings['popUpMessageLifeTime'], settings['popUpMessageAlphaSpeed'], settings['popUpMessageStackLength']])
        parser.addArgs([userPrefs['enableStoreMws'], userPrefs['enableStoreCws']])
        self.__movieViewHandler.respond(parser.args())

    def onCheckCooldownPeriod(self, *args):
        parser = CommandArgsParser(self.onCheckCooldownPeriod.__name__, 1)
        cid = parser.parse(*args)
        flag = isBroadcatInCooldown()
        parser.addArg(not flag)
        self.__movieViewHandler.respond(parser.args())
        if flag:
            self.__movieViewHandler.call(CHMS_COMMANDS.RecieveMessage(), [cid, BROADCAST_COOL_DOWN_MESSAGE, False])

    def onCreateChannelClientError(self, *args):
        parser = CommandArgsParser(self.onCreateChannelClientError.__name__, 1, [str])
        messageKey = parser.parse(*args)
        SystemMessages.pushI18nMessage(messageKey, type=SystemMessages.SM_TYPE.Error)

    def onCreateChannel(self, *args):
        parser = CommandArgsParser(self.onCreateChannel.__name__, 2, [str, str])
        channelName, password = parser.parse(*args)
        channelName = ' '.join(filter(lambda word: len(word), channelName.split(' ')))
        result = self.channels.createChannel(channelName, password)
        if result == CREATE_CHANNEL_RESULT.activeChannelLimitReached:
            key = '#%s:dialogs/createChannel/errors/activeChannelLimitReached/message' % MESSENGER_I18N_FILE
            SystemMessages.pushI18nMessage(key, type=SystemMessages.SM_TYPE.Error)

    def onJoinToChannel(self, *args):
        parser = CommandArgsParser(self.onJoinToChannel.__name__, 2, [long, str])
        cid, password = parser.parse(*args)
        self.channels.joinToChannel(cid, password)

    def onRequestChannelsPersistents(self, *args):
        """
        Return the list of channels windows persistent, saved from previous sessions
        """
        parser = CommandArgsParser(self.onRequestChannelsPersistents.__name__)
        parser.parse(*args)
        for channelId, persistent in self.__channelsWindow.iteritems():
            parser.addArg(channelId, int)
            parser.addArgs(persistent)

        self.__movieViewHandler.respond(parser.args())

    def onSetChannelPersistent(self, *args):
        """
        When you close the channel window if the size and position of the window
        is different from the default, than save
        """
        parser = CommandArgsParser(self.onSetChannelPersistent.__name__, 5, [int,
         float,
         float,
         float,
         float])
        channelId, x, y, width, height = parser.parse(*args)
        self.__channelsWindow[channelId] = (x,
         y,
         width,
         height)

    def onRequestManagementPersistents(self, *args):
        """
        Return the list of management windows persistent, saved from previous sessions
        """
        parser = CommandArgsParser(self.onRequestManagementPersistents.__name__)
        parser.parse(*args)
        for windowName, persistent in self.__managementWindow.iteritems():
            parser.addArg(windowName, str)
            parser.addArgs(persistent)

        self.__movieViewHandler.respond(parser.args())

    def onSetManagementPersistent(self, *args):
        """
        When you close the management window if the size and position of the window
        is different from the default, than save
        """
        parser = CommandArgsParser(self.onSetManagementPersistent.__name__, 5, [str,
         float,
         float,
         float,
         float])
        windowName, x, y, width, height = parser.parse(*args)
        self.__managementWindow[windowName] = (x,
         y,
         width,
         height)

    def __filterChannelWindowsPersistents(self):
        """
        Filtered list of windows persistent.
        Only returns the window channels, which are joined.
        """
        joinedChannels = self.channels.getChannelList(joined=True, isBattle=False)
        filtered = {}
        if len(self.__channelsWindow):
            for channel in joinedChannels:
                cid = channel.cid
                if self.__channelsWindow.has_key(cid):
                    filtered[cid] = self.__channelsWindow[cid]

        else:
            filtered = self.__channelsWindow
        return filtered

    def __storeWindowsPersistent(self):
        try:
            path = '_root._level0.lobbyMessengerLoader.flushManagementWindows'
            managementStr = self.__movieViewHandler.movie.invoke((path,))
            args = managementStr.split(',')
            for step in range(len(args) / 4):
                idx = step * 5
                self.__managementWindow[str(args[idx])] = (float(args[idx + 1]),
                 float(args[idx + 2]),
                 float(args[idx + 3]),
                 float(args[idx + 4]))

        except AttributeError:
            LOG_ERROR('Error when flushing opened management windows in chat')

        try:
            path = '_root._level0.lobbyMessengerLoader.flushChannelsWindows'
            channelsStr = self.__movieViewHandler.movie.invoke((path,))
            args = channelsStr.split(',')
            for step in range(len(args) / 4):
                idx = step * 5
                self.__channelsWindow[long(args[idx])] = (float(args[idx + 1]),
                 float(args[idx + 2]),
                 float(args[idx + 3]),
                 float(args[idx + 4]))

        except AttributeError:
            LOG_ERROR('Error when flushing opened channels windows in chat')

        g_settings.applyWindowPersistens(self.__managementWindow, self.__filterChannelWindowsPersistents())

    def __onReceiveLazyChannels(self, channels):
        for channel in channels:
            if channel.lazy:
                self.__createLazyChannelPage(channel)

        self.__joinedChannels.refresh()

    def __onConnectingToSecureChannel(self, channel):
        channelInfo = i18n.convert(i18n.makeString('#%s:dialogs/connectingToSecureChannel/labels/info' % MESSENGER_I18N_FILE, channel.channelName))
        self.__movieViewHandler.call(C_COMMANDS.ConnectToSecureChannel(), [channel.cid, channelInfo])

    def __onDenunciationReceived(self, userName, topicID):
        topicStr = i18n.makeString('#menu:denunciation/type%d' % topicID)
        SystemMessages.pushMessage(i18n.makeString('#system_messages:denunciation/success') % (userName, topicStr), type=SystemMessages.SM_TYPE.Information)

    def __onUsersRosterUpdate(self, action, user):
        for _, page in self.__channelPages.iteritems():
            page.refreshMemberList()

    def __onApplyUserPreferences(self):
        userPreferences = g_settings.userPreferences
        persistens = userPreferences['windowsPersistens']
        enableStoreMws = userPreferences['enableStoreMws']
        enableStoreCws = userPreferences['enableStoreCws']
        self.__channelsWindow = persistens['channels']
        self.__managementWindow = persistens['management']
        self.__movieViewHandler.call(WP_COMMANDS.SetEnableStorePersistents(), [enableStoreMws, enableStoreCws])
