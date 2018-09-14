# Embedded file name: scripts/client/messenger/gui/Scaleform/view/GroupDeleteView.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.gui.Scaleform.meta.GroupDeleteViewMeta import GroupDeleteViewMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter

class GroupDeleteView(GroupDeleteViewMeta):

    def __init__(self):
        super(GroupDeleteView, self).__init__()

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def onOk(self, data):
        self.proto.contacts.removeGroup(data.groupName, data.deleteWithMembers)
        self.as_closeViewS()

    def _getInitDataObject(self):
        initData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_DELETEGROUP_MAINLABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_DELETEGROUP_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_MANAGEGROUP_DELETEGROUP_BTNCANCEL_LABEL, MESSENGER.CONTACTS_GROUPDELETEVIEW_TOOLTIPS_BTNS_APPLY, MESSENGER.CONTACTS_GROUPDELETEVIEW_TOOLTIPS_BTNS_CLOSE)
        return initData
