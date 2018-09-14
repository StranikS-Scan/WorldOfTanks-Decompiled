# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/contact_note.py
import types
from helpers import html
from messenger.proto.xmpp.extensions import PyExtension, PyQuery
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.rsm import RqResultSet, ResultSet
from messenger.proto.xmpp.extensions.shared_handlers import IQHandler
from messenger.proto.xmpp.gloox_constants import IQ_TYPE

class NoteID(PyExtension):
    __slots__ = ('_dbID',)

    def __init__(self, dbID = 0):
        super(NoteID, self).__init__('key')
        self._dbID = dbID

    @classmethod
    def getDefaultData(cls):
        return 0

    def parseTag(self, pyGlooxTag):
        data = pyGlooxTag.getCData()
        if data.isdigit():
            dbID = long(data)
        else:
            dbID = self.getDefaultData()
        return dbID

    def _makeChildrenString(self):
        if self._dbID:
            return str(self._dbID)
        return ''


class NoteText(PyExtension):
    __slots__ = ('_text',)

    def __init__(self, text = ''):
        super(NoteText, self).__init__('value')
        self._text = text

    @classmethod
    def getDefaultData(cls):
        return ''

    def getTag(self):
        if self._text:
            return super(NoteText, self).getTag()
        else:
            return ''

    def parseTag(self, pyGlooxTag):
        return pyGlooxTag.getCData()

    def _makeChildrenString(self):
        return html.escape(self._text)


class NoteItem(PyExtension):

    def __init__(self, dbID = 0, text = ''):
        super(NoteItem, self).__init__(_TAG.ITEM)
        self.setChild(NoteID(dbID))
        self.setChild(NoteText(text))

    def getDefaultData(self):
        return (NoteID.getDefaultData(), NoteText.getDefaultData())

    def parseTag(self, pyGlooxTag):
        dbID = self._getChildData(pyGlooxTag, 0, NoteID.getDefaultData())
        text = self._getChildData(pyGlooxTag, 1, NoteText.getDefaultData())
        return (long(dbID), text)


class NoteList(PyExtension):

    def __init__(self, items = None, rsm = None):
        super(NoteList, self).__init__(_TAG.LIST)
        self.setAttribute('name', 'contact-notes')
        if items:
            for item in items:
                self.setChild(item)

        if rsm:
            self.setChild(rsm)

    @classmethod
    def getDefaultData(cls):
        return ([], ResultSet.getDefaultData())

    def parseTag(self, pyGlooxTag):
        items = []
        child = self.getChild(0)
        if child:
            for tag in self._getChildTags(pyGlooxTag, 0):
                items.append(child.parseTag(tag))

        padding = self._getChildData(pyGlooxTag, 1, ResultSet.getDefaultData())
        return (items, padding)

    def _getXPathAttr(self):
        return ('name', 'contact-notes')


class NoteQuery(PyExtension):

    def __init__(self, items = None, rsm = None):
        super(NoteQuery, self).__init__(_TAG.QUERY)
        self.setXmlNs(_NS.WG_STORAGE)
        self.setChild(NoteList(items, rsm))

    @classmethod
    def getDefaultData(cls):
        return NoteList.getDefaultData()

    def parseTag(self, pyGlooxTag):
        return self._getChildData(pyGlooxTag, 0, NoteList.getDefaultData())


class NotesListQuery(PyQuery):

    def __init__(self, max = 0, after = None):
        super(NotesListQuery, self).__init__(IQ_TYPE.GET, NoteQuery(rsm=RqResultSet(max, after)))


class NotesListHandler(IQHandler):

    def __init__(self):
        super(NotesListHandler, self).__init__(NoteQuery(items=(NoteItem(),), rsm=ResultSet()))


class SetNoteQuery(PyQuery):

    def __init__(self, dbID, text):
        super(SetNoteQuery, self).__init__(IQ_TYPE.SET, NoteQuery(items=(NoteItem(dbID, text),)))


class SetNotesQuery(PyQuery):

    def __init__(self, items):
        converted = []
        for item in items:
            raise len(item) == 2 or AssertionError
            dbID = item[0]
            raise type(dbID) is types.LongType or AssertionError
            text = item[1]
            raise type(text) in types.StringTypes or AssertionError
            converted.append(NoteItem(dbID, text))

        super(SetNotesQuery, self).__init__(IQ_TYPE.SET, NoteQuery(items=converted))


class RemoveNoteQuery(PyQuery):

    def __init__(self, dbID):
        super(RemoveNoteQuery, self).__init__(IQ_TYPE.SET, NoteQuery(items=(NoteItem(dbID),)))


class RemoveNotesQuery(PyQuery):

    def __init__(self, dbIDs):
        converted = []
        for dbID in dbIDs:
            raise type(dbID) is types.LongType or AssertionError
            converted.append(NoteItem(dbID))

        super(RemoveNotesQuery, self).__init__(IQ_TYPE.SET, NoteQuery(items=converted))
