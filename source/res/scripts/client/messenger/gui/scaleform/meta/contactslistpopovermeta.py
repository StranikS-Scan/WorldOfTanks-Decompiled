# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactsListPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class ContactsListPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def addToFriends(self, uid, name):
        """
        :param uid:
        :param name:
        :return :
        """
        self._printOverrideError('addToFriends')

    def addToIgnored(self, uid, name):
        """
        :param uid:
        :param name:
        :return :
        """
        self._printOverrideError('addToIgnored')

    def isEnabledInRoaming(self, uid):
        """
        :param uid:
        :return Boolean:
        """
        self._printOverrideError('isEnabledInRoaming')

    def changeGroup(self, dbId, contactName, groupData):
        """
        :param dbId:
        :param contactName:
        :param groupData:
        :return :
        """
        self._printOverrideError('changeGroup')

    def copyIntoGroup(self, contactDbId, groupData):
        """
        :param contactDbId:
        :param groupData:
        :return :
        """
        self._printOverrideError('copyIntoGroup')

    def as_setInitInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitInfo(data) if self._isDAAPIInited() else None

    def as_editGroupS(self, targetGroupName):
        """
        :param targetGroupName:
        :return :
        """
        return self.flashObject.as_editGroup(targetGroupName) if self._isDAAPIInited() else None

    def as_removeGroupS(self, targetGroupName):
        """
        :param targetGroupName:
        :return :
        """
        return self.flashObject.as_removeGroup(targetGroupName) if self._isDAAPIInited() else None

    def as_createContactNoteS(self, userName, databaseID):
        """
        :param userName:
        :param databaseID:
        :return :
        """
        return self.flashObject.as_createContactNote(userName, databaseID) if self._isDAAPIInited() else None

    def as_editContactNoteS(self, userName, databaseID):
        """
        :param userName:
        :param databaseID:
        :return :
        """
        return self.flashObject.as_editContactNote(userName, databaseID) if self._isDAAPIInited() else None
