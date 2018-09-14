# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ConnectToSecureChannelWindow.py
from external_strings_utils import unicode_from_utf8
from gui import SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.gui.Scaleform.meta.ConnectToSecureChannelWindowMeta import ConnectToSecureChannelWindowMeta
from messenger.m_constants import CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH, PROTO_TYPE
from messenger.proto import proto_getter

class ConnectToSecureChannelWindow(ConnectToSecureChannelWindowMeta):

    def __init__(self, ctx = None):
        super(ConnectToSecureChannelWindow, self).__init__()
        self._channel = ctx.get('channel')

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def sendPassword(self, value):
        pwdRange = xrange(CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH + 1)
        if value is None or len(unicode_from_utf8(value)[0]) not in pwdRange:
            SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_INVALIDPASSWORD_MESSAGE, CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH, type=SystemMessages.SM_TYPE.Error)
        else:
            self.proto.channels.joinToChannel(self._channel.getID(), password=value)
            self.destroy()
        return

    def cancelPassword(self):
        self.destroy()

    def _populate(self):
        super(ConnectToSecureChannelWindow, self)._populate()
        self.as_infoMessageS(i18n.makeString(MESSENGER.DIALOGS_CONNECTINGTOSECURECHANNEL_LABELS_INFO, i18n.encodeUtf8(self._channel.getFullName())))

    def _dispose(self):
        self._channel = None
        super(ConnectToSecureChannelWindow, self)._dispose()
        return
