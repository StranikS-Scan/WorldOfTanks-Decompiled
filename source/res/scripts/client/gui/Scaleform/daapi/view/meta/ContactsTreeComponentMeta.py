# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ContactsTreeComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ContactsTreeComponentMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onGroupSelected(self, mainGroup, groupData):
        """
        :param mainGroup:
        :param groupData:
        :return :
        """
        self._printOverrideError('onGroupSelected')

    def searchLocalContact(self, flt):
        """
        :param flt:
        :return :
        """
        self._printOverrideError('searchLocalContact')

    def hasDisplayingContacts(self):
        """
        :return Boolean:
        """
        self._printOverrideError('hasDisplayingContacts')

    def as_updateInfoMessageS(self, enableSearchInput, title, message, warn):
        """
        :param enableSearchInput:
        :param title:
        :param message:
        :param warn:
        :return :
        """
        return self.flashObject.as_updateInfoMessage(enableSearchInput, title, message, warn) if self._isDAAPIInited() else None

    def as_getMainDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getMainDP() if self._isDAAPIInited() else None

    def as_setInitDataS(self, val):
        """
        :param val:
        :return :
        """
        return self.flashObject.as_setInitData(val) if self._isDAAPIInited() else None
