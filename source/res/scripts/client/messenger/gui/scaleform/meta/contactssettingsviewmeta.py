# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactsSettingsViewMeta.py
from messenger.gui.Scaleform.view.BaseContactView import BaseContactView

class ContactsSettingsViewMeta(BaseContactView):

    def showOfflineUsers(self, value):
        self._printOverrideError('showOfflineUsers')

    def showOthers(self, value):
        self._printOverrideError('showOthers')

    def messagesNotFromContacts(self, value):
        self._printOverrideError('messagesNotFromContacts')
