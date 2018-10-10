# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/ContactsSettingsView.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from account_helpers.AccountSettings import AccountSettings, CONTACTS
from helpers import dependency
from messenger.gui.Scaleform.meta.ContactsSettingsViewMeta import ContactsSettingsViewMeta
from skeletons.account_helpers.settings_core import ISettingsCore

class ContactsSettingsView(ContactsSettingsViewMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ContactsSettingsView, self).__init__()
        self.__startData = None
        self.__currentData = None
        self.__isOperationAvailable = True
        return

    def onOk(self, data):
        self.settingsCore.serverSettings.setSectionSettings(CONTACTS, self.__currentData)
        self.as_closeViewS()

    def showOfflineUsers(self, value):
        self.__currentData['showOfflineUsers'] = value
        self.__checkIsDataChanged()

    def showOthers(self, value):
        self.__currentData['showOthersCategory'] = value
        self.__checkIsDataChanged()

    def messagesNotFromContacts(self, value):
        self.__checkIsDataChanged()

    def _populate(self):
        super(ContactsSettingsView, self)._populate()
        self.__checkIsDataChanged()

    def _getInitDataObject(self):
        defaults = AccountSettings.getFilterDefault(CONTACTS)
        startData = self.settingsCore.serverSettings.getSection(CONTACTS, defaults)
        self.__startData = {'showOfflineUsers': bool(startData['showOfflineUsers']),
         'showOthersCategory': bool(startData['showOthersCategory'])}
        self.__currentData = self.__startData.copy()
        baseData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_SETTINGS_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_SETTINGS_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_SETTINGS_BTNCANCEL_LABEL, MESSENGER.CONTACTS_SETTINGSVIEW_TOOLTIPS_BTNS_APPLY, MESSENGER.CONTACTS_SETTINGSVIEW_TOOLTIPS_BTNS_CLOSE)
        baseData['mainData'] = self.__startData
        return baseData

    def __checkIsDataChanged(self):
        newAvailableVal = False
        for key in self.__startData.iterkeys():
            if self.__startData[key] != self.__currentData[key]:
                newAvailableVal = True
                break

        if newAvailableVal != self.__isOperationAvailable:
            self.__isOperationAvailable = newAvailableVal
            self.as_setOkBtnEnabledS(self.__isOperationAvailable)
