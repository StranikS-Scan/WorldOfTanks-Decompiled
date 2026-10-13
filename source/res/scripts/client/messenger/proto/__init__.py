# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/__init__.py
from __future__ import absolute_import
import weakref
from future.utils import viewitems, viewvalues
from helpers.ro_property import ROPropertyMeta
from messenger.m_constants import PROTO_TYPE, PROTO_TYPE_NAMES
from messenger.proto.bw import BWProtoPlugin
from messenger.proto.bw_chat2 import BWProtoPlugin as BWProtoPlugin_chat2
from messenger.proto.bw.BWServerSettings import BWServerSettings
from messenger.proto.bw_chat2.BWServerSettings import BWServerSettings as BWServerSettings_chat2
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.migration import MigrationPlugin
from messenger.proto.migration.MigrationServerSettings import MigrationServerSettings
from messenger.proto.xmpp import XmppPlugin, XmppServerSettings
from messenger.proto.xmpp.xmpp_constants import XMPP_MUC_CHANNEL_TYPE
from py2to3.patched_future import with_metaclass
__all__ = ('BWProtoPlugin', 'BWProtoPlugin_chat2', 'XmppPlugin', 'MigrationPlugin')
_SUPPORTED_PROTO_PLUGINS = {PROTO_TYPE.BW: BWProtoPlugin(),
 PROTO_TYPE.BW_CHAT2: BWProtoPlugin_chat2(),
 PROTO_TYPE.XMPP: XmppPlugin()}
_SUPPORTED_PROTO_PLUGINS[PROTO_TYPE.MIGRATION] = MigrationPlugin(_SUPPORTED_PROTO_PLUGINS)
_SUPPORTED_PROTO_SETTINGS = {PROTO_TYPE.BW: BWServerSettings(),
 PROTO_TYPE.BW_CHAT2: BWServerSettings_chat2(),
 PROTO_TYPE.XMPP: XmppServerSettings(),
 PROTO_TYPE.MIGRATION: MigrationServerSettings()}

class ProtoPluginsDecorator(with_metaclass(ROPropertyMeta, IProtoPlugin)):
    __readonly__ = {PROTO_TYPE_NAMES[k]:v for k, v in viewitems(_SUPPORTED_PROTO_PLUGINS)}

    def __repr__(self):
        return 'ProtoPluginsDecorator(id=0x{0:08X}, ro={1!r:s})'.format(id(self), self.__readonly__.keys())

    def connect(self, scope):
        self._invoke('connect', scope)

    def disconnect(self):
        self._invoke('disconnect')

    def view(self, scope):
        self._invoke('view', scope)

    def goToReplay(self):
        self._invoke('goToReplay')

    def setFilters(self, msgFilterChain):
        self._invoke('setFilters', weakref.proxy(msgFilterChain))

    def init(self):
        for plugin in viewvalues(self.__readonly__):
            plugin.init()

    def clear(self):
        for plugin in viewvalues(self.__readonly__):
            plugin.clear()

    def _invoke(self, method, *args):
        settings = ServerSettings.__readonly__
        for protoName, plugin in viewitems(self.__readonly__):
            if protoName in settings and settings[protoName].isEnabled():
                getattr(plugin, method)(*args)


class ServerSettings(with_metaclass(ROPropertyMeta, object)):
    __readonly__ = {PROTO_TYPE_NAMES[k]:v for k, v in viewitems(_SUPPORTED_PROTO_SETTINGS)}

    def __repr__(self):
        return 'ServerSettings(id=0x{0:08X}, ro={1!r:s})'.format(id(self), self.__readonly__.keys())

    def update(self, data):
        for settings in viewvalues(self.__readonly__):
            settings.update(data)

    def clear(self):
        for settings in viewvalues(self.__readonly__):
            settings.clear()

    def useToShowContacts(self, protoType):
        result = False
        if protoType is PROTO_TYPE.BW:
            result = not self._isXmppEnabled()
        elif protoType is PROTO_TYPE.XMPP:
            result = self._isXmppEnabled()
        return result

    def isUserRoomsEnabled(self, protoType):
        result = False
        if protoType is PROTO_TYPE.BW:
            result = not self._isXmppUserRoomsEnabled()
        elif protoType is PROTO_TYPE.XMPP:
            result = self._isXmppUserRoomsEnabled()
        return result

    def getSystemChannels(self, protoType):
        return self._getSystemChannels() if protoType is PROTO_TYPE.XMPP else None

    def isXmppClansEnabled(self):
        return self._isXmppMucChannelEnabled(XMPP_MUC_CHANNEL_TYPE.CLANS)

    def _isXmppEnabled(self):
        xmppName = PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]
        if xmppName in self.__readonly__:
            result = self.__readonly__[xmppName].isEnabled()
        else:
            result = False
        return result

    def _isXmppMucChannelEnabled(self, channelType):
        xmppName = PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]
        if xmppName in self.__readonly__:
            result = self.__readonly__[xmppName].isMucServiceAllowed(channelType)
        else:
            result = False
        return result

    def _isXmppUserRoomsEnabled(self):
        return self._isXmppMucChannelEnabled(XMPP_MUC_CHANNEL_TYPE.USERS)

    def _getSystemChannels(self):
        xmppName = PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]
        if xmppName in self.__readonly__:
            result = self.__readonly__[xmppName].getSystemChannels()
        else:
            result = None
        return result


class _proto_type_getter(object):

    def __init__(self, protoType):
        super(_proto_type_getter, self).__init__()
        self._type = protoType

    def get(self):
        raise NotImplementedError

    def __call__(self, _):
        return self.get()


class proto_getter(_proto_type_getter):

    def get(self):
        return _SUPPORTED_PROTO_PLUGINS[self._type]


class settings_getter(_proto_type_getter):

    def get(self):
        return _SUPPORTED_PROTO_SETTINGS[self._type]
