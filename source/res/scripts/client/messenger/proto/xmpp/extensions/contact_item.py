# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/contact_item.py
from messenger.proto.xmpp.extensions import PyExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.custom_items import SharedExtension
from messenger.proto.xmpp.jid import ContactJID

class ContactItemExtension(PyExtension):

    def __init__(self, jid=None):
        super(ContactItemExtension, self).__init__(_TAG.ITEM)
        if jid:
            self.setAttribute('jid', str(jid))
        self.setChild(SharedExtension())

    @classmethod
    def getDefaultData(cls):
        return (None, SharedExtension.getDefaultData())

    def parseTag(self, pyGlooxTag):
        jid = pyGlooxTag.findAttribute('jid')
        if jid:
            jid = ContactJID(jid)
        else:
            jid = None
        info = self._getChildData(pyGlooxTag, 0, SharedExtension.getDefaultData())
        return (jid, info)
