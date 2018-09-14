# Embedded file name: scripts/client/messenger/gui/Scaleform/view/contact_manage_note_views.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter
from messenger.gui.Scaleform.meta.ContactNoteManageViewMeta import ContactNoteManageViewMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.xmpp.xmpp_string_utils import validateContactNote
from messenger.storage import storage_getter
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT
from helpers import i18n
from messenger import g_settings

class ContactManageNoteView(ContactNoteManageViewMeta):

    def __init__(self):
        super(ContactManageNoteView, self).__init__()
        self._dbID = 0L

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def sendData(self, data):
        self._dbID = long(data.dbID)
        userEntity = self.usersStorage.getUser(self._dbID)
        if userEntity is None:
            userProps = {'userName': data.name}
        else:
            userProps = ContactConverter.makeBaseUserProps(userEntity)
        scheme = g_settings.getColorScheme('contacts')
        userProps['rgb'] = scheme.getColors('clanMember')[0]
        self.as_setUserPropsS(userProps)
        return

    def checkText(self, text):
        self.as_setOkBtnEnabledS(self._isTextValid(text))

    def onOk(self, text):
        success = self.proto.contacts.setNote(self._dbID, text)
        if success:
            self.as_closeViewS()

    def _isTextValid(self, text):
        _, error = validateContactNote(text)
        return error is None


class ContactEditNoteView(ContactManageNoteView):

    def __init__(self):
        super(ContactEditNoteView, self).__init__()
        self.__defaultText = None
        return

    def sendData(self, data):
        super(ContactEditNoteView, self).sendData(data)
        self.__defaultText = 'Some note of particular contact'
        self.as_setInputTextS(self.__defaultText)

    def _isTextValid(self, text):
        return super(ContactEditNoteView, self)._isTextValid(text) and self.__defaultText != text

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_EDITNOTE_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_EDITNOTE_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_EDITNOTE_BTNCANCEL_LABEL)
        defData['inputPrompt'] = i18n.makeString(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATEGROUP_SEARCHINPUTPROMPT, symbols=CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT)
        defData['groupMaxChars'] = CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT
        return defData


class ContactCreateNoteView(ContactManageNoteView):

    def __init__(self):
        super(ContactCreateNoteView, self).__init__()

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATENOTE_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATENOTE_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATENOTE_BTNCANCEL_LABEL)
        defData['inputPrompt'] = i18n.makeString(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATEGROUP_SEARCHINPUTPROMPT, symbols=CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT)
        defData['groupMaxChars'] = CONTACT_LIMIT.NOTE_MAX_CHARS_COUNT
        return defData
