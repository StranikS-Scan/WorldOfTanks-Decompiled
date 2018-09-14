# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/blocking_cmd.py
from messenger.proto.xmpp.extensions import PyExtension, PyQuery
from messenger.proto.xmpp.extensions.contact_item import ContactItemExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.shared_handlers import IQChildHandler
from messenger.proto.xmpp.gloox_constants import IQ_TYPE

def _createBlockListExt():
    return PyExtension(_TAG.BLOCK_LIST).setXmlNs(_NS.BLOCKING_CMD)


def _createBlockItemExt(jid = None):
    return PyExtension(_TAG.BLOCK_ITEM).setXmlNs(_NS.BLOCKING_CMD).setChild(ContactItemExtension(jid))


def _createUnblockItemExt(jid = None):
    return PyExtension(_TAG.UNBLOCK_ITEM).setXmlNs(_NS.BLOCKING_CMD).setChild(ContactItemExtension(jid))


class BlockListQuery(PyQuery):

    def __init__(self):
        super(BlockListQuery, self).__init__(IQ_TYPE.GET, _createBlockListExt())


class BlockListHandler(IQChildHandler):

    def __init__(self):
        super(BlockListHandler, self).__init__(_createBlockListExt().setChild(ContactItemExtension()))


class BlockItemQuery(PyQuery):

    def __init__(self, jid):
        super(BlockItemQuery, self).__init__(IQ_TYPE.SET, _createBlockItemExt(jid))


class BlockItemHandler(IQChildHandler):

    def __init__(self):
        super(BlockItemHandler, self).__init__(_createBlockItemExt())


class UnblockItemQuery(PyQuery):

    def __init__(self, jid):
        super(UnblockItemQuery, self).__init__(IQ_TYPE.SET, _createUnblockItemExt(jid))


class UnblockItemHandler(IQChildHandler):

    def __init__(self):
        super(UnblockItemHandler, self).__init__(_createUnblockItemExt())
