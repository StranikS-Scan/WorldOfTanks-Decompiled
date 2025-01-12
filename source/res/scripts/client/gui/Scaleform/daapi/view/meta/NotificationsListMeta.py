# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationsListMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NotificationsListMeta(SmartPopOverView):

    def onClickAction(self, typeID, entityID, action):
        self._printOverrideError('onClickAction')

    def getMessageActualTime(self, msTime):
        self._printOverrideError('getMessageActualTime')

    def onGroupChange(self, groupIdx):
        self._printOverrideError('onGroupChange')

    def onCheckNewsClick(self):
        self._printOverrideError('onCheckNewsClick')

    def as_setInitDataS(self, value):
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setMessagesListS(self, value):
        return self.flashObject.as_setMessagesList(value) if self._isDAAPIInited() else None

    def as_appendMessageS(self, messageData):
        return self.flashObject.as_appendMessage(messageData) if self._isDAAPIInited() else None

    def as_updateMessageS(self, messageData):
        return self.flashObject.as_updateMessage(messageData) if self._isDAAPIInited() else None

    def as_updateCountersS(self, counts):
        return self.flashObject.as_updateCounters(counts) if self._isDAAPIInited() else None

    def as_setProgressiveRewardEnabledS(self, isEnabled):
        return self.flashObject.as_setProgressiveRewardEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setIsNewsBlockEnabledS(self, isEnabled):
        return self.flashObject.as_setIsNewsBlockEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setCheckNewsBtnEnabledS(self, isEnabled):
        return self.flashObject.as_setCheckNewsBtnEnabled(isEnabled) if self._isDAAPIInited() else None
