# Embedded file name: scripts/client/messenger/proto/xmpp/wrappers.py
from collections import namedtuple
import time
from constants import IGR_TYPE, ARENA_GUI_TYPE_LABEL
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from messenger.proto.entities import ClanInfo
XMPPChannelData = namedtuple('XMPPChannelData', ('name', 'msgType'))
XMPPMessageData = namedtuple('XMPPChannelData', ('accountDBID', 'accountName', 'text', 'sentAt'))
ClientInfo = namedtuple('ClientInfo', ('igrID', 'igrRoomID', 'gameHost', 'arenaLabel'))
_BanInfoItem = namedtuple('_BanInfoItem', ('source', 'setter', 'expiresAt', 'reason'))

@ReprInjector.simple(('_items', 'items'))

class BanInfo(object):
    __slots__ = ('_items',)

    def __init__(self, items):
        super(BanInfo, self).__init__()
        self._items = items

    def isChatBan(self):
        now = time.time()
        for item in self._items:
            if not item.expiresAt or item.expiresAt > now:
                return True

        return False

    def getFirstActiveItem(self):
        now = time.time()
        for item in self._items:
            if not item.expiresAt or item.expiresAt > now:
                return item

        return None


WGExtsInfo = namedtuple('WGExtsInfo', ('client', 'clan', 'ban'))

def makeClientInfo(*args):
    if len(args) < 4:
        return None
    else:
        igrID, igrRoomID, gameHost, arenaLabel = args[:4]
        if igrID and igrID.isdigit():
            igrID = int(igrID)
        else:
            igrID = IGR_TYPE.NONE
        if igrRoomID and igrRoomID.isdigit():
            igrRoomID = long(igrRoomID)
        else:
            igrRoomID = 0
        if arenaLabel and arenaLabel not in ARENA_GUI_TYPE_LABEL.LABELS.values():
            arenaLabel = ''
        return ClientInfo(igrID, igrRoomID, gameHost, arenaLabel)


def makeClanInfo(*args):
    if len(args) < 2:
        return
    else:
        dbID, abbrev = args[:2]
        if dbID and dbID.isdigit():
            dbID = long(dbID)
        else:
            dbID = 0
        info = None
        if dbID and abbrev:
            info = ClanInfo(dbID, abbrev, 0)
        return info


def makeBanInfo(*args):
    items = []
    for item in args:
        if len(item) < 4:
            continue
        source, setter, expiresAt, reason = item[:4]
        if source.isdigit():
            source = int(source)
        else:
            source = 0
        if expiresAt.isdigit():
            expiresAt = time_utils.getTimestampFromUTC(time_utils.getTimeStructInUTC(float(expiresAt)))
        else:
            expiresAt = 0
        items.append(_BanInfoItem(source, setter, expiresAt, reason))

    if items:
        info = BanInfo(items)
    else:
        info = None
    return info
