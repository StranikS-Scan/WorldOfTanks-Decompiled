# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/chat.py
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from web_client_api import W2CSchema, Field, w2c
from web_client_api.common import SPA_ID_TYPES

class _OpenChatSchema(W2CSchema):
    user_id = Field(required=True, type=SPA_ID_TYPES)
    user_name = Field(required=True, type=basestring)


class ChatWebApiMixin(object):

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @w2c(_OpenChatSchema, 'chat_window')
    def openChat(self, cmd):
        receiver = self.usersStorage.getUser(cmd.user_id)
        if receiver and not receiver.isIgnored():
            self.proto.contacts.createPrivateChannel(cmd.user_id, cmd.user_name.encode('utf-8'))
