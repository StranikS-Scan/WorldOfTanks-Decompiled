# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/wrappers.py
from collections import namedtuple
import types
import cPickle
from gui.shared.utils import transport
from helpers.time_utils import makeLocalServerTime
from messenger.proto.entities import SharedUserEntity, ClanInfo
from messenger_common_chat2 import messageArgs

class _MessageVO(object):
    __slots__ = ('sentAt', 'accountDBID', 'avatarSessionID', 'vehicleID', 'text', 'accountName')

    def __init__(self, floatArg1=0, strArg1='', **kwargs):
        super(_MessageVO, self).__init__()
        self.accountDBID = 0
        self.avatarSessionID = ''
        self.vehicleID = 0
        self.text = strArg1
        if not isinstance(strArg1, types.UnicodeType):
            self.text = unicode(strArg1, 'utf-8', errors='ignore')
        self.sentAt = 0
        if floatArg1 > 0:
            self.sentAt = makeLocalServerTime(floatArg1)
        self.accountName = None
        return


class ArenaMessageVO(_MessageVO):
    __slots__ = ('isCommonChannel',)

    def __init__(self, floatArg1=0, int32Arg1=False, int64Arg1=0, strArg1='', **kwargs):
        super(ArenaMessageVO, self).__init__(floatArg1, strArg1, **kwargs)
        self.vehicleID = int64Arg1
        self.isCommonChannel = bool(int32Arg1)


class UnitMessageVO(_MessageVO):

    def __init__(self, floatArg1=0, int64Arg1=0, strArg1='', strArg2='', **kwargs):
        super(UnitMessageVO, self).__init__(floatArg1, strArg1, **kwargs)
        self.accountDBID = int64Arg1
        self.accountName = strArg2
        if not isinstance(strArg2, types.UnicodeType):
            self.accountName = unicode(strArg2, 'utf-8', errors='ignore')


def UnitHistoryIterator(value):
    value = dict(value)
    if 'strArg1' in value:
        history = transport.z_loads(value['strArg1'])
    else:
        history = []
    for sendAt, accountDBID, accountName, messageText in history:
        yield UnitMessageVO(sendAt, accountDBID, messageText, accountName)


def ArenaHistoryIterator(value):
    value = dict(value)
    if 'strArg1' in value:
        history = transport.z_loads(value['strArg1'])
    else:
        history = []
    for sendAt, isCommonChannel, vehicleID, messageText in history:
        yield ArenaMessageVO(sendAt, isCommonChannel, vehicleID, messageText)


def SearchResultIterator(value):
    value = dict(value)
    if 'strArg1' in value:
        result = cPickle.loads(value['strArg1'])
    else:
        result = []
    for name, dbID, clanAbbrev in result:
        if not name:
            continue
        yield SharedUserEntity(long(dbID), name=name, clanInfo=ClanInfo(abbrev=clanAbbrev))


class IDataFactory(object):

    def broadcastArgs(self, text, *args):
        raise NotImplementedError

    def historyIter(self, args):
        raise NotImplementedError

    def messageVO(self, args):
        raise NotImplementedError


class ArenaDataFactory(IDataFactory):

    def broadcastArgs(self, text, *args):
        return messageArgs(strArg1=text, int32Arg1=args[0] if args else 0)

    def historyIter(self, args):
        return ArenaHistoryIterator(args)

    def messageVO(self, args):
        return ArenaMessageVO(**args)


class UnitDataFactory(IDataFactory):

    def broadcastArgs(self, text, *args):
        return messageArgs(strArg1=text)

    def historyIter(self, args):
        return UnitHistoryIterator(args)

    def messageVO(self, args):
        return UnitMessageVO(**args)


class CHAT_TYPE(object):
    UNIT = 1
    ARENA = 2


ChannelProtoData = namedtuple('ChannelProtoData', ('chatType', 'settings'))
