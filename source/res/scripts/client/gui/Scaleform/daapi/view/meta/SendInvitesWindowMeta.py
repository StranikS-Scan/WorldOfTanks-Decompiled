# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SendInvitesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SendInvitesWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def showError(self, value):
        self._printOverrideError('showError')

    def setOnlineFlag(self, value):
        self._printOverrideError('setOnlineFlag')

    def sendInvites(self, accountsToInvite, comment):
        self._printOverrideError('sendInvites')

    def getAllAvailableContacts(self):
        self._printOverrideError('getAllAvailableContacts')

    def as_onReceiveSendInvitesCooldownS(self, value):
        return self.flashObject.as_onReceiveSendInvitesCooldown(value) if self._isDAAPIInited() else None

    def as_setDefaultOnlineFlagS(self, onlineFlag):
        return self.flashObject.as_setDefaultOnlineFlag(onlineFlag) if self._isDAAPIInited() else None

    def as_setInvalidUserTagsS(self, tags):
        return self.flashObject.as_setInvalidUserTags(tags) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_onContactUpdatedS(self, contact):
        return self.flashObject.as_onContactUpdated(contact) if self._isDAAPIInited() else None

    def as_onListStateChangedS(self, isEmpty):
        return self.flashObject.as_onListStateChanged(isEmpty) if self._isDAAPIInited() else None

    def as_enableDescriptionS(self, isEnabled):
        return self.flashObject.as_enableDescription(isEnabled) if self._isDAAPIInited() else None

    def as_enableMassSendS(self, isEnabled, addAllTooltip):
        return self.flashObject.as_enableMassSend(isEnabled, addAllTooltip) if self._isDAAPIInited() else None
