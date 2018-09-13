# Embedded file name: scripts/client/messenger/proto/bw/BWServerSettings.py
from messenger.proto.interfaces import IProtoSettings

class BWServerSettings(IProtoSettings):

    def __init__(self):
        super(BWServerSettings, self).__init__()

    def isEnabled(self):
        return True
