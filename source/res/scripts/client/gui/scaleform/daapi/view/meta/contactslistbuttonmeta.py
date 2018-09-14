# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ContactsListButtonMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ContactsListButtonMeta(BaseDAAPIComponent):

    def as_setContactsCountS(self, num):
        if self._isDAAPIInited():
            return self.flashObject.as_setContactsCount(num)
