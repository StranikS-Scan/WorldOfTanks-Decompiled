# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/contact_item.py
from gui.shared.utils import findFirst
from messenger.proto.xmpp.extensions import PyExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.jid import ContactJID

class ContactItemExtension(PyExtension):

    def __init__(self, jid = None):
        super(ContactItemExtension, self).__init__(_TAG.ITEM)
        if jid:
            self.setAttribute('jid', str(jid))
        self.setChild(WgContactInfoExtension())

    @classmethod
    def getDefaultData(cls):
        return (None, WgContactInfoExtension.getDefaultData())

    def parseTag(self, pyGlooxTag):
        jid = pyGlooxTag.findAttribute('jid')
        if jid:
            jid = ContactJID(jid)
        else:
            jid = None
        info = self._getChildData(pyGlooxTag, 0, WgContactInfoExtension.getDefaultData())
        return (jid, info)


class WgContactInfoExtension(PyExtension):

    def __init__(self, includeNS = True):
        super(WgContactInfoExtension, self).__init__(_TAG.WG_EXTENSION)
        if includeNS:
            self.setXmlNs(_NS.WG_EXTENSION)

    @classmethod
    def getDefaultData(cls):
        return {}

    def getTag(self):
        tag = ''
        if len(self._attributes) > 1:
            tag = super(WgContactInfoExtension, self).getTag()
        return tag

    def parseTag(self, pyGlooxTag):
        info = self.getDefaultData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='nickname')))
        if tag:
            info['name'] = tag.getCData()
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='userid')))
        if tag:
            info['dbID'] = long(tag.getCData())
        return info
