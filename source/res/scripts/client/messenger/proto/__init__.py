# Embedded file name: scripts/client/messenger/proto/__init__.py
from constants import JD_CUTOUT
from messenger.ext.ROPropertyMeta import ROPropertyMeta
from messenger.m_constants import PROTO_TYPE, PROTO_TYPE_NAMES
from messenger.proto.bw import BWProtoPlugin
from messenger.proto.bw.BWServerSettings import BWServerSettings
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.xmpp import XmppPlugin
from messenger.proto.xmpp.XmppServerSettings import XmppServerSettings
__all__ = ('BWProtoPlugin', 'XmppPlugin')
SUPPORTED_PROTO_PLUGINS = {PROTO_TYPE_NAMES[PROTO_TYPE.BW]: BWProtoPlugin(),
 PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]: XmppPlugin()}
SUPPORTED_PROTO_SETTINGS = {PROTO_TYPE_NAMES[PROTO_TYPE.BW]: BWServerSettings(),
 PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]: XmppServerSettings()}

class proto_getter(object):

    def __init__(self, protoType):
        super(proto_getter, self).__init__()
        self.__attr = PROTO_TYPE_NAMES[protoType]

    def __call__(self, _):
        return SUPPORTED_PROTO_PLUGINS[self.__attr]


class ProtoPluginsDecorator(IProtoPlugin):
    __metaclass__ = ROPropertyMeta
    __readonly__ = SUPPORTED_PROTO_PLUGINS

    def __repr__(self):
        return 'ProtoPluginsDecorator(id=0x{0:08X}, ro={1!r:s})'.format(id(self), self.__readonly__.keys())

    def connect(self, scope):
        self._invoke('connect', scope)

    def disconnect(self):
        self._invoke('disconnect')

    def view(self, scope):
        self._invoke('view', scope)

    def clear(self):
        self._invoke('clear')

    def _invoke(self, method, *args):
        settings = SUPPORTED_PROTO_SETTINGS
        for protoName, plugin in self.__readonly__.iteritems():
            if protoName in settings and settings[protoName].isEnabled():
                getattr(plugin, method)(*args)


class ServerSettings(object):
    __metaclass__ = ROPropertyMeta
    __readonly__ = SUPPORTED_PROTO_SETTINGS

    def __init__(self):
        super(ServerSettings, self).__init__()
        self.__jdCutout = JD_CUTOUT.OFF

    def __repr__(self):
        return 'ServerSettings(id=0x{0:08X}, ro={1!r:s})'.format(id(self), self.__readonly__.keys())

    def update(self, data):
        if 'jdCutouts' in data:
            self.__jdCutout = int(data['jdCutouts'])
        else:
            self.__jdCutout = JD_CUTOUT.OFF
        for settings in self.__readonly__.itervalues():
            settings.update(data)

    def clear(self):
        for settings in self.__readonly__.itervalues():
            settings.clear()

    def useToShowOnline(self, protoType):
        result = False
        xmppName = PROTO_TYPE_NAMES[PROTO_TYPE.XMPP]
        if xmppName in self.__readonly__:
            isXMPPEnabled = self.__readonly__[xmppName].isEnabled()
        else:
            isXMPPEnabled = False
        if protoType is PROTO_TYPE.BW:
            result = not isXMPPEnabled or self.__jdCutout == JD_CUTOUT.OFF
        elif protoType is PROTO_TYPE.XMPP:
            result = isXMPPEnabled and self.__jdCutout == JD_CUTOUT.ON
        return result
