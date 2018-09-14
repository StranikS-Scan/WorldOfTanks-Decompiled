# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMessengerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleMessengerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def sendMessageToChannel(self, cid, message):
        """
        :param cid:
        :param message:
        :return Boolean:
        """
        self._printOverrideError('sendMessageToChannel')

    def focusReceived(self):
        """
        :return :
        """
        self._printOverrideError('focusReceived')

    def focusLost(self):
        """
        :return :
        """
        self._printOverrideError('focusLost')

    def as_showGreenMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_showGreenMessage(message) if self._isDAAPIInited() else None

    def as_showRedMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_showRedMessage(message) if self._isDAAPIInited() else None

    def as_showBlackMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_showBlackMessage(message) if self._isDAAPIInited() else None

    def as_showSelfMessageS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_showSelfMessage(message) if self._isDAAPIInited() else None

    def as_setupListS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setupList(data) if self._isDAAPIInited() else None

    def as_setReceiverS(self, data, isResetReceivers):
        """
        :param data:
        :param isResetReceivers:
        :return :
        """
        return self.flashObject.as_setReceiver(data, isResetReceivers) if self._isDAAPIInited() else None

    def as_changeReceiverS(self, receiver):
        """
        :param receiver:
        :return :
        """
        return self.flashObject.as_changeReceiver(receiver) if self._isDAAPIInited() else None

    def as_setActiveS(self, isActive):
        """
        :param isActive:
        :return :
        """
        return self.flashObject.as_setActive(isActive) if self._isDAAPIInited() else None

    def as_setFocusS(self):
        """
        :return :
        """
        return self.flashObject.as_setFocus() if self._isDAAPIInited() else None

    def as_unSetFocusS(self):
        """
        :return :
        """
        return self.flashObject.as_unSetFocus() if self._isDAAPIInited() else None

    def as_setUserPreferencesS(self, tooltipStr):
        """
        :param tooltipStr:
        :return :
        """
        return self.flashObject.as_setUserPreferences(tooltipStr) if self._isDAAPIInited() else None

    def as_setReceiversS(self, receivers):
        """
        :param receivers:
        :return :
        """
        return self.flashObject.as_setReceivers(receivers) if self._isDAAPIInited() else None

    def as_enableToSendMessageS(self):
        """
        :return :
        """
        return self.flashObject.as_enableToSendMessage() if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        """
        :param isCtrlPressed:
        :return :
        """
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None

    def as_enterPressedS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_enterPressed(index) if self._isDAAPIInited() else None
