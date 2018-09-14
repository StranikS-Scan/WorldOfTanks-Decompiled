# Embedded file name: scripts/client/messenger/gui/Scaleform/view/group_manage_views.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.gui.Scaleform.meta.BaseManageContactViewMeta import BaseManageContactViewMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT
from messenger.proto.xmpp.xmpp_string_utils import validateRosterItemGroup
from messenger.storage import storage_getter

class group_manage_views(BaseManageContactViewMeta):

    def __init__(self):
        super(group_manage_views, self).__init__()
        self._currentName = None
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def checkText(self, name):
        if self._currentName != name:
            self._currentName = name
            isAllowedResult, errorMsg = False, ''
            name, error = validateRosterItemGroup(self._currentName)
            if error:
                if self._currentName != '':
                    errorMsg = error.getMessage()
                else:
                    errorMsg = ''
            elif self.usersStorage.isGroupExists(name):
                errorMsg = i18n.makeString(MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_ERROR_GROUPALREADYEXIST)
            else:
                isAllowedResult = True
                self._currentName = name
            self.as_setLabelS(errorMsg)
            self.as_setOkBtnEnabledS(isAllowedResult)

    def _dispose(self):
        super(group_manage_views, self)._dispose()

    def _populate(self):
        super(group_manage_views, self)._populate()

    def _getDefaultInitData(self, mainLbl, btOkLbl, btnCancelLbl):
        defData = super(group_manage_views, self)._getDefaultInitData(mainLbl, btOkLbl, btnCancelLbl)
        defData['inputPrompt'] = i18n.makeString(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_RENAMEGROUP_SEARCHINPUTPROMPT, symbols=CONTACT_LIMIT.GROUP_MAX_LENGTH)
        defData['groupMaxChars'] = CONTACT_LIMIT.GROUP_MAX_LENGTH
        return defData


class GroupCreateView(group_manage_views):

    def onOk(self, data):
        resultSuccess = self.proto.contacts.addGroup(data.currValue)
        if resultSuccess:
            self.as_closeViewS()

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATEGROUP_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATEGROUP_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_CREATEGROUP_BTNCANCEL_LABEL)
        defData['btOkTooltip'] = MESSENGER.CONTACTS_CREATEGROUPVIEW_TOOLTIPS_BTNS_APPLY
        defData['btnCancelTooltip'] = MESSENGER.CONTACTS_CREATEGROUPVIEW_TOOLTIPS_BTNS_CLOSE
        return defData


class GroupRenameView(group_manage_views):

    def __init__(self):
        super(GroupRenameView, self).__init__()
        self.__isInited = False

    def onOk(self, data):
        successResult = self.proto.contacts.renameGroup(data.defValue, data.currValue)
        if successResult:
            self.as_closeViewS()

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_RENAMEGROUP_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_RENAMEGROUP_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_RENAMEGROUP_BTNCANCEL_LABEL)
        defData['btOkTooltip'] = MESSENGER.CONTACTS_GROUPRENAMEVIEW_TOOLTIPS_BTNS_APPLY
        defData['btnCancelTooltip'] = MESSENGER.CONTACTS_GROUPRENAMEVIEW_TOOLTIPS_BTNS_CLOSE
        return defData

    def as_setLabelS(self, msg):
        if self.__isInited == False:
            self.__isInited = True
            return None
        else:
            return super(GroupRenameView, self).as_setLabelS(msg)
