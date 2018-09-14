# Embedded file name: scripts/client/messenger/proto/migration/MigrationServerSettings.py
from messenger.proto.interfaces import IProtoSettings

class MigrationServerSettings(IProtoSettings):

    def __init__(self):
        super(MigrationServerSettings, self).__init__()

    def isEnabled(self):
        return True
