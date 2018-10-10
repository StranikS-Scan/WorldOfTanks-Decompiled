# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/search.py
from collections import namedtuple
from messenger.proto.xmpp.extensions import PyQuery, PyExtension
from messenger.proto.xmpp.extensions.disco import CreatedByElement
from messenger.proto.xmpp.extensions.shared_handlers import IQChildHandler
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG, XML_NAME_SPACE as _NS
from messenger.proto.xmpp.entities import XMPPMucChannelEntity
from messenger.proto.xmpp.extensions.spa_resolver import SpaResolverItem
from messenger.proto.xmpp.extensions.wg_items import WgSharedExtension
from messenger.proto.xmpp.gloox_constants import IQ_TYPE
XmppUserSearchInfo = namedtuple('XmppUserSearchInfo', 'dbId, nickname, clanInfo')

class _SimpleCriterionExtension(PyExtension):

    def __init__(self, name, value):
        super(_SimpleCriterionExtension, self).__init__(_TAG.CRITERION)
        self.setAttribute('name', name)
        self.setAttribute('value', value)


class ChannelSearchQuery(PyQuery):

    def __init__(self, token, to='', count=50):
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
        self.setChild(CreatedByElement())

    def parseTag(self, pyGlooxTag):
        jid = pyGlooxTag.findAttribute('jid')
        name = pyGlooxTag.findAttribute('name')
        return XMPPMucChannelEntity(jid, name)


class UsersSearchQuery(PyQuery):

    def __init__(self, token, to=''):
        super(UsersSearchQuery, self).__init__(IQ_TYPE.GET, to=to)
        self._nickname = token
        self._ext = self.__initExtension()

    def __initExtension(self):
        filterExtension = PyExtension(_TAG.ITEM).setXmlNs(_NS.WG_SPA_RESOLVER).setAttribute('nickname', self._nickname)
        return PyExtension(_TAG.QUERY).setXmlNs(_NS.WG_SPA_RESOLVER).setChild(filterExtension)


class UserSearchHandler(IQChildHandler):

    def __init__(self):
        super(UserSearchHandler, self).__init__(PyExtension(_TAG.QUERY).setXmlNs(_NS.WG_SPA_RESOLVER).setChild(UserSearchItemExtension()))


class NicknamePrefixSearchQuery(PyQuery):

    def __init__(self, token, limit=50, to=''):
        super(NicknamePrefixSearchQuery, self).__init__(IQ_TYPE.GET, to=to)
        self._prefix = token
        self._limit = limit
        self._ext = self.__initExtension()

    def __initExtension(self):
        return PyExtension(_TAG.WG_NICKNAME_PREFIX_SEARCH).setXmlNs(_NS.WG_SPA_RESOLVER).setAttribute('prefix', self._prefix).setAttribute('limit', self._limit)


class NicknamePrefixSearchHandler(IQChildHandler):

    def __init__(self):
        super(NicknamePrefixSearchHandler, self).__init__(PyExtension(_TAG.WG_NICKNAME_PREFIX_SEARCH).setXmlNs(_NS.WG_SPA_RESOLVER).setChild(UserSearchItemExtension()))


class UserSearchItemExtension(SpaResolverItem):

    def __init__(self):
        super(UserSearchItemExtension, self).__init__(_TAG.ITEM)
        self.setChild(WgSharedExtension())

    @classmethod
    def getDefaultData(cls):
        return (SpaResolverItem.getDefaultData(), WgSharedExtension.getDefaultData())

    def parseTag(self, pyGlooxTag):
        dbId, nickname, _ = super(UserSearchItemExtension, self).parseTag(pyGlooxTag)
        info = self._getChildData(pyGlooxTag, 1, WgSharedExtension.getDefaultData())
        if 'clanInfo' in info:
            clanInfo = info['clanInfo']
        else:
            clanInfo = None
        return XmppUserSearchInfo(dbId, nickname, clanInfo)
