# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BobAnnouncementWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BobAnnouncementWidgetMeta(BaseDAAPIComponent):

    def onClick(self):
        self._printOverrideError('onClick')

    def playSound(self, soundName):
        self._printOverrideError('playSound')

    def as_setEnabledS(self, isEnabled):
        return self.flashObject.as_setEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setEventTitleS(self, title):
        return self.flashObject.as_setEventTitle(title) if self._isDAAPIInited() else None

    def as_setCurrentRealmS(self, realm):
        return self.flashObject.as_setCurrentRealm(realm) if self._isDAAPIInited() else None

    def as_showAnnouncementS(self, header, description, isLocked, hasTimer):
        return self.flashObject.as_showAnnouncement(header, description, isLocked, hasTimer) if self._isDAAPIInited() else None
