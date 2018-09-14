# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactsListPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class ContactsListPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    """

    def addToFriends(self, uid, name):
        self._printOverrideError('addToFriends')

    def addToIgnored(self, uid, name):
        self._printOverrideError('addToIgnored')

    def isEnabledInRoaming(self, uid):
        self._printOverrideError('isEnabledInRoaming')

    def changeGroup(self, dbId, contactName, groupData):
        self._printOverrideError('changeGroup')

    def copyIntoGroup(self, contactDbId, groupData):
        self._printOverrideError('copyIntoGroup')

    def as_setInitInfoS(self, data):
        """
        :param data: Represented by ContactsWindowInitVO (AS)
        """
        return self.flashObject.as_setInitInfo(data) if self._isDAAPIInited() else None

    def as_editGroupS(self, targetGroupName):
        return self.flashObject.as_editGroup(targetGroupName) if self._isDAAPIInited() else None

    def as_removeGroupS(self, targetGroupName):
        return self.flashObject.as_removeGroup(targetGroupName) if self._isDAAPIInited() else None

    def as_createContactNoteS(self, userName, databaseID):
        return self.flashObject.as_createContactNote(userName, databaseID) if self._isDAAPIInited() else None

    def as_editContactNoteS(self, userName, databaseID):
        return self.flashObject.as_editContactNote(userName, databaseID) if self._isDAAPIInited() else None
