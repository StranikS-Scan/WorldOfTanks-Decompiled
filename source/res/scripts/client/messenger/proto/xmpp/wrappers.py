# Embedded file name: scripts/client/messenger/proto/xmpp/wrappers.py
from collections import namedtuple
import time
from constants import IGR_TYPE
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from messenger.proto.entities import ClanInfo
from messenger.proto.xmpp.xmpp_constants import BAN_SOURCE
XMPPChannelData = namedtuple('XMPPChannelData', ('name', 'msgType'))
XMPPMessageData = namedtuple('XMPPChannelData', ('accountDBID', 'accountName', 'text', 'sentAt'))
IGRInfo = namedtuple('WGExtsInfo', ('igrID', 'igrRoomID'))
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
            if item.source == BAN_SOURCE.CHAT and item.expiresAt > now:
                return True

        return False

    def getFirstActiveItem(self):
        now = time.time()
        for item in self._items:
            if item.expiresAt > now:
                return item

        return None


WGExtsInfo = namedtuple('WGExtsInfo', ('IGR', 'clan', 'ban'))

def makeIGRInfo(*args):
    if len(args) < 2:
        return None
    else:
        igrID, igrRoomID = args[:2]
        if igrID and igrID.isdigit():
            igrID = int(igrID)
        else:
            igrID = IGR_TYPE.NONE
        if igrRoomID and igrRoomID.isdigit():
            igrRoomID = long(igrRoomID)
        else:
            igrRoomID = 0
        return IGRInfo(igrID, igrRoomID)


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
        if source not in BAN_SOURCE.RANGE:
            continue
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


def makeWGInfoFromPresence(info):
    if 'igrInfo' in info:
        igr = makeIGRInfo(*info['igrInfo'])
    else:
        igr = None
    if 'clanInfo' in info:
        clanInfo = makeClanInfo(*info['clanInfo'])
    else:
        clanInfo = None
    if 'banInfo' in info:
        banInfo = makeBanInfo(*info['banInfo'])
    else:
        banInfo = None
    return WGExtsInfo(igr, clanInfo, banInfo)
