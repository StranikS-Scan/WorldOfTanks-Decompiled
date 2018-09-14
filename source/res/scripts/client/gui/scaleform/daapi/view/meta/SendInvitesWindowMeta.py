# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SendInvitesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SendInvitesWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def showError(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('showError')

    def setOnlineFlag(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('setOnlineFlag')

    def sendInvites(self, accountsToInvite, comment):
        """
        :param accountsToInvite:
        :param comment:
        :return :
        """
        self._printOverrideError('sendInvites')

    def getAllAvailableContacts(self):
        """
        :return Array:
        """
        self._printOverrideError('getAllAvailableContacts')

    def as_onReceiveSendInvitesCooldownS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_onReceiveSendInvitesCooldown(value) if self._isDAAPIInited() else None

    def as_setDefaultOnlineFlagS(self, onlineFlag):
        """
        :param onlineFlag:
        :return :
        """
        return self.flashObject.as_setDefaultOnlineFlag(onlineFlag) if self._isDAAPIInited() else None

    def as_setInvalidUserTagsS(self, tags):
        """
        :param tags:
        :return :
        """
        return self.flashObject.as_setInvalidUserTags(tags) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_onContactUpdatedS(self, contact):
        """
        :param contact:
        :return :
        """
        return self.flashObject.as_onContactUpdated(contact) if self._isDAAPIInited() else None

    def as_onListStateChangedS(self, isEmpty):
        """
        :param isEmpty:
        :return :
        """
        return self.flashObject.as_onListStateChanged(isEmpty) if self._isDAAPIInited() else None

    def as_enableDescriptionS(self, isEnabled):
        """
        :param isEnabled:
        :return :
        """
        return self.flashObject.as_enableDescription(isEnabled) if self._isDAAPIInited() else None

    def as_enableMassSendS(self, isEnabled, addAllTooltip):
        """
        :param isEnabled:
        :param addAllTooltip:
        :return :
        """
        return self.flashObject.as_enableMassSend(isEnabled, addAllTooltip) if self._isDAAPIInited() else None
