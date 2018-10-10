# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/rsm.py
from shared_utils import findFirst
from messenger.proto.xmpp.extensions import PyExtension, SimpleExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS

class ResultSet(PyExtension):
    __slots__ = ('_converter',)

    def __init__(self, converter=int):
        super(ResultSet, self).__init__(_TAG.SET)
        self.setXmlNs(_NS.RESULT_SET_MANAGEMENT)
        self._converter = converter

    @classmethod
    def getDefaultData(cls):
        return (0, None, None)

    def clear(self):
        self._converter = None
        super(ResultSet, self).clear()
        return

    def parseTag(self, pyGlooxTag):
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='count')))
        if tag:
            count = int(tag.getCData())
        else:
            count = 0
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='first')))
        if tag and tag.getCData():
            first = self._converter(tag.getCData())
        else:
            first = None
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='last')))
        if tag and tag.getCData():
            last = self._converter(tag.getCData())
        else:
            last = None
        return (count, first, last)


class RqResultSet(ResultSet):
    __slots__ = ()

    def __init__(self, max=0, after=None, before=None):
        super(RqResultSet, self).__init__()
        if max:
            self.setChild(SimpleExtension('max', max))
            if after:
                self.setChild(SimpleExtension('after', after))
            if before:
                self.setChild(SimpleExtension('before', before))

    def getTag(self):
        tag = ''
        if self._children:
            tag = super(RqResultSet, self).getTag()
        return tag
