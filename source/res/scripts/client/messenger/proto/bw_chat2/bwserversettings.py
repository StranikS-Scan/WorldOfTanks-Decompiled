# Embedded file name: scripts/client/messenger/proto/bw_chat2/BWServerSettings.py
from messenger.proto.interfaces import IProtoSettings

class BWServerSettings(IProtoSettings):
    __slots__ = ('_isEnabled',)

    def __init__(self):
        super(BWServerSettings, self).__init__()
        self._isEnabled = False

    def update(self, data):
        if 'isChat2Enabled' in data:
            self._isEnabled = data['isChat2Enabled']
        else:
            self._isEnabled = False

    def isEnabled(self):
        return self._isEnabled
