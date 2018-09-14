# Embedded file name: scripts/client/messenger/proto/xmpp/wrappers.py
from collections import namedtuple
import time
from constants import IGR_TYPE, ARENA_GUI_TYPE_LABEL
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from messenger.proto.entities import ClanInfo
from messenger.proto.xmpp.gloox_constants import CHAT_STATE
from messenger.proto.xmpp.xmpp_constants import XMPP_BAN_COMPONENT
from messenger.proto.xmpp.xmpp_constants import ANY_ITEM_LITERAL
XMPPChannelData = namedtuple('XMPPChannelData', ('name', 'msgType'))

class ChatMessage(object):
    __slots__ = ('uuid', 'accountDBID', 'accountName', 'body', 'state', 'sentAt', 'requestID', 'isFinalInHistory')

    def __init__(self, dbID = 0L, name = '', body = '', sentAt = 0):
        super(ChatMessage, self).__init__()
        self.uuid = ''
        self.accountDBID = dbID
        self.accountName = name
        self.body = body
        self.state = CHAT_STATE.UNDEFINED
        self.sentAt = sentAt
        self.requestID = ''
        self.isFinalInHistory = False

    def isHistory(self):
        return len(self.requestID)


ClientInfo = namedtuple('ClientInfo', ('igrID', 'igrRoomID', 'gameHost', 'arenaLabel'))
_BanInfoItem = namedtuple('_BanInfoItem', ('source', 'setter', 'expiresAt', 'reason', 'components', 'game'))

@ReprInjector.simple(('_items', 'items'))

class BanInfo(object):
    __slots__ = ('_items',)

    def __init__(self, items):
        super(BanInfo, self).__init__()
        self._items = items

    def getFirstActiveItem(self, game = None, components = None):
        now = time.time()
        for item in sorted(self._items, key=lambda item: item.expiresAt):
            if game is not None and item.game not in (game, ANY_ITEM_LITERAL):
                continue
            if components is not None and components & item.components == 0:
                continue
            if not item.expiresAt or item.expiresAt > now:
                return item

        return

    def isBanned(self, game = None, components = None):
        return self.getFirstActiveItem(game=game, components=components) is not None


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
        if len(item) < 6:
            continue
        source, setter, expiresAt, reason, components, game = item[:6]
        if source.isdigit():
            source = int(source)
        else:
            source = 0
        if expiresAt.isdigit():
            expiresAt = time_utils.getTimestampFromUTC(time_utils.getTimeStructInUTC(float(expiresAt)))
        else:
            expiresAt = 0
        items.append(_BanInfoItem(source, setter, expiresAt, reason, XMPP_BAN_COMPONENT.fromString(components), game))

    if items:
        info = BanInfo(items)
    else:
        info = None
    return info
