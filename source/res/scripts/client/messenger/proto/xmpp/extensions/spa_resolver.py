# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/spa_resolver.py
from messenger.proto.xmpp.extensions import PyExtension, PyQuery
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.shared_handlers import IQChildHandler
from messenger.proto.xmpp.gloox_constants import IQ_TYPE

class SpaResolverError(PyExtension):

    def __init__(self):
        super(SpaResolverError, self).__init__(_TAG.ERROR)

    @classmethod
    def getDefaultData(cls):
        return ''

    def getTag(self):
        return ''

    def parseTag(self, pyGlooxTag):
        return pyGlooxTag.getCData()


class SpaResolverItem(PyExtension):

    def __init__(self, dbID = 0L, nickname = ''):
        super(SpaResolverItem, self).__init__(_TAG.ITEM)
        if dbID:
            self.setAttribute('id', dbID)
        if nickname:
            self.setAttribute('nickname', nickname)
        self.setChild(SpaResolverError())

    @classmethod
    def getDefaultData(cls):
        return (0L, '', SpaResolverError.getDefaultData())

    def parseTag(self, pyGlooxTag):
        dbID = pyGlooxTag.findAttribute('id')
        if dbID:
            dbID = long(dbID)
        else:
            dbID = 0L
        nickname = pyGlooxTag.findAttribute('nickname')
        error = self._getChildData(pyGlooxTag, 0, SpaResolverError.getDefaultData())
        return (dbID, nickname, error)


class SpaResolverQuery(PyExtension):

    def __init__(self, items = None):
        super(SpaResolverQuery, self).__init__(_TAG.QUERY)
        self.setXmlNs(_NS.WG_SPA_RESOLVER)
        items = items or tuple()
        for item in items:
            self.setChild(item)

    @classmethod
    def getDefaultData(cls):
        return []


class SpaResolverByIDsQuery(PyQuery):

    def __init__(self, dbIDs):
        super(SpaResolverByIDsQuery, self).__init__(IQ_TYPE.GET, SpaResolverQuery(items=map(lambda dbID: SpaResolverItem(dbID, ''), dbIDs)))


class SpaResolverHandler(IQChildHandler):

    def __init__(self):
        super(SpaResolverHandler, self).__init__(SpaResolverQuery((SpaResolverItem(),)))
