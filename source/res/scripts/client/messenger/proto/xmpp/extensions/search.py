# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/search.py
from messenger.proto.xmpp.extensions import PyQuery, PyExtension
from messenger.proto.xmpp.extensions.shared_handlers import IQChildHandler
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG, XML_NAME_SPACE as _NS
from messenger.proto.xmpp.entities import XMPPMucChannelEntity
from messenger.proto.xmpp.gloox_constants import IQ_TYPE

class _SimpleCriterionExtension(PyExtension):

    def __init__(self, name, value):
        super(_SimpleCriterionExtension, self).__init__(_TAG.CRITERION)
        self.setAttribute('name', name)
        self.setAttribute('value', value)


class ChannelSearchQuery(PyQuery):

    def __init__(self, token, to = '', count = 50):
        super(ChannelSearchQuery, self).__init__(IQ_TYPE.GET, to=to)
        self._token = token
        self._results_count = count
        self._ext = self.__initExtension()

    def __initExtension(self):
        filterExtension = PyExtension(_TAG.FILTER).setXmlNs(_NS.WG_MUC_ROOMS).setAttribute('roomname-prefix', self._token).setAttribute('max-entries', self._results_count)
        filterExtension.setChild(_SimpleCriterionExtension('muc#roomconfig_membersonly', 0))
        return PyExtension(_TAG.QUERY).setXmlNs(_NS.DISCO_ITEMS).setChild(filterExtension)


class ChannelsListHandler(IQChildHandler):

    def __init__(self):
        super(ChannelsListHandler, self).__init__(PyExtension(_TAG.QUERY).setXmlNs(_NS.DISCO_ITEMS).setChild(ChannelItemExtension()))


class ChannelItemExtension(PyExtension):

    def __init__(self):
        super(ChannelItemExtension, self).__init__(_TAG.ITEM)

    def parseTag(self, pyGlooxTag):
        jid = pyGlooxTag.findAttribute('jid')
        name = pyGlooxTag.findAttribute('name')
        return XMPPMucChannelEntity(jid, name)
