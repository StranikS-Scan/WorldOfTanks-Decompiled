# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MessengerBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MessengerBarMeta(BaseDAAPIComponent):

    def channelButtonClick(self):
        self._printOverrideError('channelButtonClick')

    def contactsButtonClick(self):
        self._printOverrideError('contactsButtonClick')

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)
