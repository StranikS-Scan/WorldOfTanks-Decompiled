# Embedded file name: scripts/client/messenger/proto/bw_chat2/limits.py
from messenger.proto.interfaces import IProtoLimits
from messenger_common_chat2 import MESSENGER_LIMITS

class ArenaLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return MESSENGER_LIMITS.BATTLE_CHANNEL_MESSAGE_MAX_SIZE

    def getBroadcastCoolDown(self):
        return MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC

    def getHistoryMaxLength(self):
        return MESSENGER_LIMITS.BATTLE_CHAT_HISTORY_ON_SERVER_MAX_LEN


class UnitLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return MESSENGER_LIMITS.UNIT_CHANNEL_MESSAGE_MAX_SIZE

    def getBroadcastCoolDown(self):
        return MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC

    def getHistoryMaxLength(self):
        return MESSENGER_LIMITS.UNIT_CHAT_HISTORY_ON_SERVER_MAX_LEN


class FindUserLimits(IProtoLimits):

    def getMaxResultSize(self):
        return MESSENGER_LIMITS.FIND_USERS_BY_NAME_MAX_RESULT_SIZE

    def getRequestCooldown(self):
        return MESSENGER_LIMITS.FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC
