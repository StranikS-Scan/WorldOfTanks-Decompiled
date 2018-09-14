# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMessengerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleMessengerMeta(BaseDAAPIComponent):

    def sendMessageToChannel(self, cid, message):
        self._printOverrideError('sendMessageToChannel')

    def focusReceived(self):
        self._printOverrideError('focusReceived')

    def focusLost(self):
        self._printOverrideError('focusLost')

    def getToxicStatus(self, messageID):
        self._printOverrideError('getToxicStatus')

    def onToxicButtonClicked(self, messageID, actionID):
        self._printOverrideError('onToxicButtonClicked')

    def onToxicPanelClosed(self, messageID):
        self._printOverrideError('onToxicPanelClosed')

    def as_enableToxicPanelS(self):
        return self.flashObject.as_enableToxicPanel() if self._isDAAPIInited() else None

    def as_updateMessagesS(self, messageID, value):
        return self.flashObject.as_updateMessages(messageID, value) if self._isDAAPIInited() else None

    def as_showGreenMessageS(self, message, messageID):
        return self.flashObject.as_showGreenMessage(message, messageID) if self._isDAAPIInited() else None

    def as_showRedMessageS(self, message, messageID):
        return self.flashObject.as_showRedMessage(message, messageID) if self._isDAAPIInited() else None

    def as_showBlackMessageS(self, message, messageID):
        return self.flashObject.as_showBlackMessage(message, messageID) if self._isDAAPIInited() else None

    def as_showSelfMessageS(self, message, messageID):
        return self.flashObject.as_showSelfMessage(message, messageID) if self._isDAAPIInited() else None

    def as_setupListS(self, data):
        """
        :param data: Represented by BattleMessengerSettingsVO (AS)
        """
        return self.flashObject.as_setupList(data) if self._isDAAPIInited() else None

    def as_setReceiverS(self, data, isResetReceivers):
        """
        :param data: Represented by BattleMessengerReceiverVO (AS)
        """
        return self.flashObject.as_setReceiver(data, isResetReceivers) if self._isDAAPIInited() else None

    def as_changeReceiverS(self, receiver):
        return self.flashObject.as_changeReceiver(receiver) if self._isDAAPIInited() else None

    def as_setActiveS(self, isActive):
        return self.flashObject.as_setActive(isActive) if self._isDAAPIInited() else None

    def as_setFocusS(self):
        return self.flashObject.as_setFocus() if self._isDAAPIInited() else None

    def as_unSetFocusS(self):
        return self.flashObject.as_unSetFocus() if self._isDAAPIInited() else None

    def as_setUserPreferencesS(self, tooltipStr):
        return self.flashObject.as_setUserPreferences(tooltipStr) if self._isDAAPIInited() else None

    def as_setReceiversS(self, receivers):
        """
        :param receivers: Represented by Vector.<BattleMessengerReceiverVO> (AS)
        """
        return self.flashObject.as_setReceivers(receivers) if self._isDAAPIInited() else None

    def as_enableToSendMessageS(self):
        return self.flashObject.as_enableToSendMessage() if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None

    def as_enterPressedS(self, index):
        return self.flashObject.as_enterPressed(index) if self._isDAAPIInited() else None

    def as_updateToxicPanelS(self, messageID, value):
        return self.flashObject.as_updateToxicPanel(messageID, value) if self._isDAAPIInited() else None

    def as_restoreMessagesS(self, messageID):
        return self.flashObject.as_restoreMessages(messageID) if self._isDAAPIInited() else None
