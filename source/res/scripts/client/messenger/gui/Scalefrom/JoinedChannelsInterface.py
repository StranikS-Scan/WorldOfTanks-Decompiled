# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/JoinedChannelsInterface.py
# Compiled at: 2011-07-29 13:15:51
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from messenger.gui.interfaces import DispatcherProxyHolder
from messenger.gui.Scalefrom import JCH_COMMANDS
from messenger import LAZY_CHANNELS

class JoinedChannelsInterface(DispatcherProxyHolder):

    def __init__(self):
        self.__movieViewHandler = None
        self.__waitActivationChannels = []
        self.__sortedChList = []
        self.__isPopulated = False
        return

    @property
    def channelsManager(self):
        return self._dispatcherProxy.channels

    def populateUI(self, movieViewHandler):
        self.__movieViewHandler = movieViewHandler
        self.__isPopulated = True
        self.channelsManager.onChannelRefresh += self.__onChannelRefresh
        self.__buildChannelList()
        self.__movieViewHandler.addExternalCallbacks({JCH_COMMANDS.RequestLength(): self.onRequestChannelsLength,
         JCH_COMMANDS.RequestItemRange(): self.onRequestChannelsItems,
         JCH_COMMANDS.WaitActivation(): self.onWaitChannelActivation,
         JCH_COMMANDS.ChannelActivated(): self.onChannelActivated,
         JCH_COMMANDS.LeaveChannel(): self.onLeaveChannel,
         JCH_COMMANDS.RequestChannelData(): self.onRequestChannelData})

    def dispossessUI(self):
        if not self.__isPopulated:
            return
        else:
            self.clear()
            self.channelsManager.onChannelRefresh -= self.__onChannelRefresh
            self.__movieViewHandler.removeExternalCallbacks(JCH_COMMANDS.RequestLength(), JCH_COMMANDS.RequestItemRange(), JCH_COMMANDS.WaitActivation(), JCH_COMMANDS.ChannelActivated(), JCH_COMMANDS.LeaveChannel(), JCH_COMMANDS.RequestChannelData())
            self.__movieViewHandler = None
            self.__isPopulated = False
            return

    def refresh(self):
        if self.__isPopulated:
            self.__buildChannelList()
            self.__movieViewHandler.call(JCH_COMMANDS.RefreshList(), [len(self.__sortedChList)])

    def remove(self, cid):
        if self.__isPopulated:
            self.__buildChannelList()
            self.__movieViewHandler.call(JCH_COMMANDS.RemoveChannel(), [int(cid)])

    def clear(self):
        self.__sortedChList = []
        if self.__isPopulated:
            self.__movieViewHandler.call(JCH_COMMANDS.ClearList())

    def waiting(self, cid):
        if cid not in self.__waitActivationChannels:
            self.__waitActivationChannels.append(cid)

    def __comparator(self, channel, other):
        if channel.lazy | other.lazy:
            if channel.lazy != 0 and other.lazy != 0:
                result = cmp(LAZY_CHANNELS.ORDERS.get(channel.lazy, -1), LAZY_CHANNELS.ORDERS.get(other.lazy, -1))
            else:
                result = -1 if channel.lazy != 0 else 1
        elif channel.isSystem ^ other.isSystem:
            result = -1 if channel.isSystem else 1
        else:
            result = cmp(channel.joinedTime, other.joinedTime)
        return result

    def __buildChannelList(self):
        self.__sortedChList = sorted(self.channelsManager.getChannelList(lazy=True), cmp=self.__comparator)
        ids = map(lambda channel: channel.cid, self.__sortedChList)
        self.__waitActivationChannels = filter(lambda cid: cid in ids, self.__waitActivationChannels)

    def __onChannelRefresh(self, channel):
        self.__movieViewHandler.call(JCH_COMMANDS.GhangeChannelName(), [channel.cid, channel.channelName])

    def onRequestChannelsLength(self, *args):
        parser = CommandArgsParser(self.onRequestChannelsLength.__name__)
        parser.parse(*args)
        parser.addArg(len(self.__sortedChList))
        self.__movieViewHandler.respond(parser.args())

    def onRequestChannelsItems(self, *args):
        parser = CommandArgsParser(self.onRequestChannelsItems.__name__, 2, [int, int])
        startIndex, endIndex = parser.parse(*args)
        for item in self.__sortedChList[startIndex:endIndex + 1]:
            parser.addArgs(item)
            parser.addArg(True if item.cid in self.__waitActivationChannels else False)

        self.__movieViewHandler.respond(parser.args())

    def onWaitChannelActivation(self, *args):
        parser = CommandArgsParser(self.onWaitChannelActivation.__name__, 1, [long])
        cid = parser.parse(*args)
        if cid not in self.__waitActivationChannels:
            self.__waitActivationChannels.append(cid)

    def onChannelActivated(self, *args):
        parser = CommandArgsParser(self.onChannelActivated.__name__, 1, [long])
        cid = parser.parse(*args)
        if cid in self.__waitActivationChannels:
            self.__waitActivationChannels.remove(cid)

    def onLeaveChannel(self, *args):
        parser = CommandArgsParser(self.onLeaveChannel.__name__, 1, [long])
        cid = parser.parse(*args)
        self.channelsManager.exitFromChannel(cid)

    def onRequestChannelData(self, *args):
        parser = CommandArgsParser(self.onRequestChannelData.__name__, 1, [long])
        cid = parser.parse(*args)
        idx = None
        channel = None
        for idx, item in enumerate(self.__sortedChList):
            if item.cid == cid:
                channel = item
                break

        if channel is not None:
            parser.addArg(idx)
            parser.addArgs(channel)
            self.__movieViewHandler.respond(parser.args())
        return
