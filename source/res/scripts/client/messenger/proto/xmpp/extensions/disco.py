# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/disco.py
from collections import namedtuple
from messenger.proto.xmpp.extensions import PyQuery, PyExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.shared_handlers import IQHandler
from messenger.proto.xmpp.extensions.wg_items import WgSharedExtension
from messenger.proto.xmpp.gloox_constants import IQ_TYPE
Identity = namedtuple('Identity', ('name', 'category', 'type'))

class IdentityElement(PyExtension):

    def __init__(self):
        super(IdentityElement, self).__init__(_TAG.IDENTITY)

    @classmethod
    def getDefaultData(cls):
        return None

    def parseTag(self, pyGlooxTag):
        return Identity(pyGlooxTag.findAttribute('name'), pyGlooxTag.findAttribute('category'), pyGlooxTag.findAttribute('type'))


class FeatureElement(PyExtension):

    def __init__(self):
        super(FeatureElement, self).__init__(_TAG.FEATURE)

    @classmethod
    def getDefaultData(cls):
        return None

    def parseTag(self, pyGlooxTag):
        super(FeatureElement, self).parseTag(pyGlooxTag)


class CreatedByElement(PyExtension):

    def __init__(self):
        super(CreatedByElement, self).__init__(_TAG.CREATED_BY)
        self.setXmlNs(_NS.WG_DISCO_ITEMS)
        self.setChild(WgSharedExtension())

    @classmethod
    def getDefaultData(cls):
        return WgSharedExtension.getDefaultData()

    def parseTag(self, pyGlooxTag):
        info = self._getChildData(pyGlooxTag, 0, WgSharedExtension.getDefaultData())
        return info


class DiscoInfoExtension(PyExtension):

    def __init__(self):
        super(DiscoInfoExtension, self).__init__(_TAG.QUERY)
        self.setXmlNs(_NS.DISCO_INFO)
        self.setChild(IdentityElement())
        self.setChild(FeatureElement())
        self.setChild(CreatedByElement())

    @classmethod
    def getDefaultData(cls):
        return (None, ())

    def parseTag(self, pyGlooxTag):
        identity = self._getChildData(pyGlooxTag, 0, None)
        features = []
        child = self.getChild(1)
        for tag in self._getChildTags(pyGlooxTag, 1):
            feature = child.parseTag(tag)
            if feature is not None:
                features.append(feature)

        created_by = self._getChildData(pyGlooxTag, 2, CreatedByElement.getDefaultData())
        return (identity, features, created_by)

    def _makeChildrenString(self):
        pass


class DiscoInfoQuery(PyQuery):

    def __init__(self, jid):
        super(DiscoInfoQuery, self).__init__(IQ_TYPE.GET, DiscoInfoExtension(), jid)


class DiscoInfoHandler(IQHandler):

    def __init__(self):
        super(DiscoInfoHandler, self).__init__(DiscoInfoExtension())
