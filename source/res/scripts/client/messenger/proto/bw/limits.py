# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw/limits.py
from constants import CHAT_MESSAGE_MAX_LENGTH, CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from messenger.m_constants import MESSAGES_HISTORY_MAX_LEN
from messenger.proto.interfaces import IProtoLimits
from soft_exception import SoftException

class BattleLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE

    def getHistoryMaxLength(self):
        return MESSAGES_HISTORY_MAX_LEN

    def getBroadcastCoolDown(self):
        raise SoftException('This method should not be reached in this context')


class LobbyLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return CHAT_MESSAGE_MAX_LENGTH

    def getHistoryMaxLength(self):
        return MESSAGES_HISTORY_MAX_LEN

    def getBroadcastCoolDown(self):
        raise SoftException('This method should not be reached in this context')


class CHANNEL_LIMIT(object):
    NAME_MIN_LENGTH = 3
    NAME_MAX_LENGTH = 32
    PWD_MIN_LENGTH = 3
    PWD_MAX_LENGTH = 12
