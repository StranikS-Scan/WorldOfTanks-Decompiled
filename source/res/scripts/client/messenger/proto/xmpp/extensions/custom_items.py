# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/custom_items.py
from debug_utils import LOG_CURRENT_EXCEPTION
from shared_utils import findFirst
from messenger.proto.xmpp.extensions import PyExtension, SimpleExtension, PyHandler
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.wrappers import makeClanInfo, makeClientInfo, makeBanInfo, ExtsInfo

class SharedExtension(PyExtension):

    def __init__(self, includeNS=True):
        super(SharedExtension, self).__init__(_TAG.EXTENSION)
        if includeNS:
            self.setXmlNs(_NS.EXTENSION)

    @classmethod
    def getDefaultData(cls):
        return {}

    def getTag(self):
        tag = ''
        if self._children:
            tag = super(SharedExtension, self).getTag()
        return tag

    def parseTag(self, pyGlooxTag):
        info = self.getDefaultData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='nickname')))
        if tag:
            info['name'] = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='userid')))
        if tag:
            info['dbID'] = long(tag.getCData())
        clanDBID, clanAbbrev = (0, '')
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='clanid')))
        if tag:
            clanDBID = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='clantag')))
        if tag:
            clanAbbrev = tag.getCData()
        if clanDBID and clanAbbrev:
            info['clanInfo'] = makeClanInfo(clanDBID, clanAbbrev)
        return info


class ClientExtension(PyExtension):

    def __init__(self):
        super(ClientExtension, self).__init__(_TAG.EXT_CLIENT)
        self.setXmlNs(_NS.EXT_CLIENT)

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
            tag = super(ClientExtension, self).getTag()
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


class ExtClientHandler(PyHandler):

    def __init__(self):
        super(ExtClientHandler, self).__init__(ClientExtension())

    def getFilterString(self):
        return self._ext.getXPath()


def makeExtInfoFromPresence(info):
    if 'userId' in info:
        try:
            dbID = long(info['userId'])
        except TypeError:
            LOG_CURRENT_EXCEPTION()
            dbID = 0

    else:
        dbID = 0
    if 'nickname' in info:
        nickname = info['nickname']
    else:
        nickname = ''
    if 'extsClientTag' in info:
        clientInfo = ExtClientHandler().handleTag(info['extsClientTag'])
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
    return ExtsInfo(dbID, nickname, clientInfo, clanInfo, banInfo)
