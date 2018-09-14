# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/wg_items.py
from shared_utils import findFirst
from messenger.proto.xmpp.extensions import PyExtension, SimpleExtension, PyHandler
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.wrappers import makeClanInfo, makeClientInfo, makeBanInfo, WGExtsInfo

class WgSharedExtension(PyExtension):

    def __init__(self, includeNS = True):
        super(WgSharedExtension, self).__init__(_TAG.WG_EXTENSION)
        if includeNS:
            self.setXmlNs(_NS.WG_EXTENSION)

    @classmethod
    def getDefaultData(cls):
        return {}

    def getTag(self):
        tag = ''
        if self._children:
            tag = super(WgSharedExtension, self).getTag()
        return tag

    def parseTag(self, pyGlooxTag):
        info = self.getDefaultData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='nickname')))
        if tag:
            info['name'] = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='userid')))
        if tag:
            info['dbID'] = long(tag.getCData())
        clanDBID, clanAbbrev = (0L, '')
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='clanid')))
        if tag:
            clanDBID = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='clantag')))
        if tag:
            clanAbbrev = tag.getCData()
        if clanDBID and clanAbbrev:
            info['clanInfo'] = makeClanInfo(clanDBID, clanAbbrev)
        return info


class WgClientExtension(PyExtension):

    def __init__(self):
        super(WgClientExtension, self).__init__(_TAG.WG_CLIENT)
        self.setXmlNs(_NS.WG_CLIENT)

    def setIgrID(self, igrID):
        if igrID:
            self.setChild(SimpleExtension('igr-id', igrID))

    def setIgrRoomID(self, igrRoomID):
        if igrRoomID:
            self.setChild(SimpleExtension('igr-room-id', igrRoomID))

    def setGameServerHost(self, host):
        if host:
            self.setChild(SimpleExtension('game-host', host))

    def setArenaGuiLabel(self, label):
        if label:
            self.setChild(SimpleExtension('arena-label', label))

    @classmethod
    def getDefaultData(cls):
        return None

    def getTag(self):
        tag = ''
        if self._children:
            tag = super(WgClientExtension, self).getTag()
        return tag

    def parseTag(self, pyGlooxTag):
        igrID, igrRoomID, gameHost, arenaLabel = (0, 0, '', '')
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='igr-id')))
        if tag:
            igrID = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='igr-room-id')))
        if tag:
            igrRoomID = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='game-host')))
        if tag:
            gameHost = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='arena-label')))
        if tag:
            arenaLabel = tag.getCData()
        return makeClientInfo(igrID, igrRoomID, gameHost, arenaLabel)


class WgClientHandler(PyHandler):

    def __init__(self):
        super(WgClientHandler, self).__init__(WgClientExtension())

    def getFilterString(self):
        return self._ext.getXPath()


def makeWGInfoFromPresence(info):
    if 'extsClientTag' in info:
        clientInfo = WgClientHandler().handleTag(info['extsClientTag'])
    else:
        clientInfo = None
    if 'clanInfo' in info:
        clanInfo = makeClanInfo(*info['clanInfo'])
    else:
        clanInfo = None
    if 'banInfo' in info:
        banInfo = makeBanInfo(*info['banInfo'])
    else:
        banInfo = None
    return WGExtsInfo(clientInfo, clanInfo, banInfo)
