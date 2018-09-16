# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ContactsTreeComponentMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ContactsTreeComponentMeta(BaseDAAPIComponent):

    def onGroupSelected(self, mainGroup, groupData):
        self._printOverrideError('onGroupSelected')

    def searchLocalContact(self, flt):
        self._printOverrideError('searchLocalContact')

    def hasDisplayingContacts(self):
        self._printOverrideError('hasDisplayingContacts')

    def as_updateInfoMessageS(self, enableSearchInput, title, message, warn):
        return self.flashObject.as_updateInfoMessage(enableSearchInput, title, message, warn) if self._isDAAPIInited() else None

    def as_getMainDPS(self):
        return self.flashObject.as_getMainDP() if self._isDAAPIInited() else None

    def as_setInitDataS(self, val):
        return self.flashObject.as_setInitData(val) if self._isDAAPIInited() else None
