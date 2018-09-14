# Embedded file name: scripts/client/messenger/proto/bw_chat2/BWServerSettings.py
from messenger.proto.interfaces import IProtoSettings

class BWServerSettings(IProtoSettings):

    def isEnabled(self):
        return True
