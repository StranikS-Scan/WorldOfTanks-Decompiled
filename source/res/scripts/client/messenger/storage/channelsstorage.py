# Embedded file name: scripts/client/messenger/storage/ChannelsStorage.py
from debug_utils import LOG_ERROR
from messenger.ext.channel_num_gen import genClientID4Channel

class ChannelsStorage(object):
    __slots__ = ('__channels',)

    def __init__(self):
        super(ChannelsStorage, self).__init__()
        self.__channels = []

    def __repr__(self):
        return 'ChannelsStorage(id=0x{0:08X}, len={1:n})'.format(id(self), len(self.__channels))

    def clear(self):
        while len(self.__channels):
            self.__channels.pop().clear()

    def all(self):
        return self.__channels[:]

    def getChannel(self, channel):
        result = None
        if channel in self.__channels:
            index = self.__channels.index(channel)
            result = self.__channels[index]
        return result

    def getChannelsByCriteria(self, criteria):
        return filter(criteria.filter, self.__channels)

    def getChannelByCriteria(self, criteria):
        channels = self.getChannelsByCriteria(criteria)
        if len(channels):
            return channels[0]
        else:
            return None

    def addChannel(self, channel):
        result = True
        if channel not in self.__channels:
            channel.setClientID(genClientID4Channel(channel))
            self.__channels.append(channel)
        else:
            LOG_ERROR('Channel already exists in storage', channel)
            result = False
        return result

    def removeChannel(self, channel, clear = True):
        result = True
        if channel in self.__channels:
            index = self.__channels.index(channel)
            stored = self.__channels.pop(index)
            if clear:
                stored.clear()
        else:
            LOG_ERROR('Channel is not in storage', channel)
            result = False
        return result
