# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ChannelsManagementWindow.py
from debug_utils import LOG_ERROR
from external_strings_utils import unicode_from_utf8
from gui import SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from helpers import i18n
from messenger.gui.Scaleform.data.search_data_providers import SearchChannelsDataProvider
from messenger.gui.Scaleform.meta.ChannelsManagementWindowMeta import ChannelsManagementWindowMeta
from messenger.m_constants import PROTO_TYPE, CHANNEL_NAME_MIN_LENGTH
from messenger.m_constants import CHANNEL_NAME_MAX_LENGTH
from messenger.m_constants import CHANNEL_PWD_MAX_LENGTH, CHANNEL_PWD_MIN_LENGTH
from messenger.proto import proto_getter
from messenger.proto.bw.ChannelsManager import CREATE_CHANNEL_RESULT
from messenger.proto.interfaces import ISearchHandler

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHAT_MANAGEMENT)

class ChannelsManagementWindow(ChannelsManagementWindowMeta, ISearchHandler):

    def __init__(self, ctx = None):
        super(ChannelsManagementWindow, self).__init__()
        self._searchDP = SearchChannelsDataProvider()

    def destroy(self):
        super(ChannelsManagementWindow, self).destroy()

    def _populate(self):
        super(ChannelsManagementWindow, self)._populate()
        self._searchDP.init(self.as_getDataProviderS(), [self])

    def _dispose(self):
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        super(ChannelsManagementWindow, self)._dispose()
        return

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def getSearchLimitLabel(self):
        return i18n.makeString(MESSENGER.DIALOGS_SEARCHCHANNEL_LABELS_RESULT, self._searchDP.processor.getSearchResultLimit())

    def searchToken(self, token):
        self.as_freezSearchButtonS(True)
        self._searchDP.find(token.strip())

    def joinToChannel(self, index):
        item = self._searchDP.requestItemAtHandler(int(index))
        if item is not None:
            self.proto.channels.joinToChannel(item['id'])
        else:
            LOG_ERROR('Channel data not found', int(index))
        return

    def createChannel(self, name, userPassword, password, retype):
        name = name.strip()
        if name is None or len(unicode_from_utf8(name)[0]) not in xrange(CHANNEL_NAME_MIN_LENGTH, CHANNEL_NAME_MAX_LENGTH + 1):
            SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_INVALIDNAME_MESSAGE, CHANNEL_NAME_MIN_LENGTH, CHANNEL_NAME_MAX_LENGTH, type=SystemMessages.SM_TYPE.Error)
            return
        else:
            if userPassword:
                pwdRange = xrange(CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH + 1)
                if password is None or len(unicode_from_utf8(password)[0]) not in pwdRange:
                    SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_INVALIDPASSWORD_MESSAGE, CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH, type=SystemMessages.SM_TYPE.Error)
                    return
                if retype is None or len(unicode_from_utf8(retype)[0]) not in pwdRange:
                    SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_INVALIDRETYPEPASSWORD_MESSAGE, CHANNEL_PWD_MIN_LENGTH, CHANNEL_PWD_MAX_LENGTH, type=SystemMessages.SM_TYPE.Error)
                    return
                if password != retype:
                    SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_NOTEQUALSPASSWORDS_MESSAGE, type=SystemMessages.SM_TYPE.Error)
                    return
            else:
                password = None
            result = self.proto.channels.createChannel(name, password)
            if result == CREATE_CHANNEL_RESULT.activeChannelLimitReached:
                SystemMessages.pushI18nMessage(MESSENGER.DIALOGS_CREATECHANNEL_ERRORS_ACTIVECHANNELLIMITREACHED_MESSAGE, type=SystemMessages.SM_TYPE.Error)
            self.destroy()
            return

    def onSearchComplete(self, _):
        self.as_freezSearchButtonS(False)

    def onSearchFailed(self, _):
        self.as_freezSearchButtonS(False)
