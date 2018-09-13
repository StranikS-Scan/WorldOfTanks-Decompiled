# Embedded file name: scripts/client/messenger/proto/bw/limits.py
from constants import CHAT_MESSAGE_MAX_LENGTH, CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE
from messenger.m_constants import MESSAGES_HISTORY_MAX_LEN
from messenger.proto.interfaces import IProtoLimits

class BattleLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return CHAT_MESSAGE_MAX_LENGTH_IN_BATTLE

    def getHistoryMaxLength(self):
        return MESSAGES_HISTORY_MAX_LEN


class LobbyLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return CHAT_MESSAGE_MAX_LENGTH

    def getHistoryMaxLength(self):
        return MESSAGES_HISTORY_MAX_LEN
