# Embedded file name: scripts/client/messenger/proto/bw_chat2/wrappers.py
from collections import namedtuple
import types
import cPickle
from gui.shared.utils import transport
from helpers.time_utils import makeLocalServerTime
from messenger.proto.entities import SharedUserEntity, ClanInfo
from messenger_common_chat2 import messageArgs

class _MessageVO(object):
    __slots__ = ('accountDBID', 'text', 'sentAt')

    def __init__(self, floatArg1 = 0, int32Arg1 = False, int64Arg1 = 0L, strArg1 = '', **kwargs):
        super(_MessageVO, self).__init__()
        self.accountDBID = int64Arg1
        if type(strArg1) is types.UnicodeType:
            self.text = strArg1
        else:
            self.text = unicode(strArg1, 'utf-8', errors='ignore')
        if floatArg1 > 0:
            self.sentAt = makeLocalServerTime(floatArg1)
        else:
            self.sentAt = 0


class ArenaMessageVO(_MessageVO):
    __slots__ = ('isCommonChannel', 'accountName')

    def __init__(self, floatArg1 = 0, int32Arg1 = False, int64Arg1 = 0L, strArg1 = '', **kwargs):
        super(ArenaMessageVO, self).__init__(floatArg1=floatArg1, int64Arg1=int64Arg1, strArg1=strArg1, **kwargs)
        self.isCommonChannel = int32Arg1
        self.accountName = None
        return


class UnitMessageVO(_MessageVO):
    __slots__ = ('accountName',)

    def __init__(self, floatArg1 = 0, int64Arg1 = 0L, strArg1 = '', strArg2 = '', **kwargs):
        super(UnitMessageVO, self).__init__(floatArg1=floatArg1, int64Arg1=int64Arg1, strArg1=strArg1, **kwargs)
        if type(strArg2) is types.UnicodeType:
            self.accountName = strArg2
        else:
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
    for sendAt, isCommonChannel, accountDBID, messageText in history:
        yield ArenaMessageVO(sendAt, isCommonChannel, accountDBID, messageText)


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
    CLUB = 3


ChannelProtoData = namedtuple('ChannelProtoData', ('chatType', 'settings'))

def _SetMembersListIterator(members):
    from messenger.proto.bw_chat2.entities import BWMemberEntity
    for dbID, nickName in members:
        yield BWMemberEntity(dbID, nickName)


def _RemoveMembersListIterator(members):
    for dbID, _ in members:
        yield dbID


def getMembersListDelta(value):
    value = dict(value)
    if 'int32Arg1' in value:
        flag = value['int32Arg1']
    else:
        flag = 0
    if 'strArg1' in value:
        members = cPickle.loads(value['strArg1'])
    else:
        members = []
    if flag in (0, 1):
        iterator = _SetMembersListIterator(members)
    else:
        iterator = _RemoveMembersListIterator(members)
    return (flag, iterator)
