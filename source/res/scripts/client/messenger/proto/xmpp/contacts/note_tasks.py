# Embedded file name: scripts/client/messenger/proto/xmpp/contacts/note_tasks.py
from messenger.m_constants import USER_ACTION_ID, CLIENT_ACTION_ID, USER_TAG
from messenger.proto.entities import SharedUserEntity
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import errors
from messenger.proto.xmpp.contacts.tasks import TASK_RESULT, ContactTask, SeqTask
from messenger.proto.xmpp.extensions import contact_note
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT

def canNoteAutoDelete(contact):
    return contact.getNote() and not USER_TAG.filterSharedTags(contact.getTags())


class NotesListTask(SeqTask):
    __slots__ = ('_offset',)

    def __init__(self):
        super(NotesListTask, self).__init__()
        self._offset = 0

    def isRequired(self):
        return False

    def result(self, pyGlooxTag):
        handler = contact_note.NotesListHandler()
        notes, (count, _, last) = handler.handleTag(pyGlooxTag)
        getter = self.usersStorage.getUser
        setter = self.usersStorage.setUser
        for dbID, note in notes:
            contact = getter(dbID)
            if contact:
                contact.update(note=note)
            else:
                setter(SharedUserEntity(dbID, note=note))

        self._offset += len(notes)
        if self._offset < count:
            self._iqID = self.client().sendIQ(contact_note.NotesListQuery(CONTACT_LIMIT.NOTES_PER_PAGE, last))
        else:
            g_messengerEvents.users.onNotesListReceived()
            self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(contact_note.NotesListQuery(CONTACT_LIMIT.NOTES_PER_PAGE))


class _NoteTask(ContactTask):

    def sync(self, name, groups, sub = None, clanInfo = None):
        return self._result

    def _update(self, note):
        user = self._getUser(protoType=None)
        if user:
            user.update(note=note)
            self._doNotify(USER_ACTION_ID.NOTE_CHANGED, user, False)
        elif note:
            user = SharedUserEntity(self._jid.getDatabaseID(), note=note)
            self.usersStorage.setUser(user)
            self._doNotify(USER_ACTION_ID.NOTE_CHANGED, user, False)
        return


class SetNoteTask(_NoteTask):
    __slots__ = ('_text',)

    def __init__(self, jid, text):
        super(SetNoteTask, self).__init__(jid)
        self._text = text

    def result(self, pyGlooxTag):
        self._update(self._text)
        self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(contact_note.SetNoteQuery(self._jid.getDatabaseID(), self._text))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.SET_NOTE, pyGlooxTag)


class RemoveNoteTask(_NoteTask):

    def result(self, pyGlooxTag):
        self._update('')
        self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(contact_note.RemoveNoteQuery(self._jid.getDatabaseID()))

    def _getError(self, pyGlooxTag):
        return errors.createServerActionError(CLIENT_ACTION_ID.REMOVE_NOTE, pyGlooxTag)


class RemoveNotesTask(SeqTask):

    def __init__(self, seq):
        super(RemoveNotesTask, self).__init__()
        self._ids = seq

    def result(self, pyGlooxTag):
        getter = self.usersStorage.getUser
        updated = False
        for dbID in self._ids:
            contact = getter(dbID)
            if contact:
                contact.update(note='')
                updated = True

        if updated:
            g_messengerEvents.users.onNotesListReceived()
        self._result = TASK_RESULT.REMOVE

    def _doRun(self, client):
        self._iqID = client.sendIQ(contact_note.RemoveNotesQuery(self._ids))
