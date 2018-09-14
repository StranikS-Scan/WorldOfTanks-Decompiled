# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortOrderPopoverMeta(SmartPopOverView):

    def requestForCreateOrder(self):
        self._printOverrideError('requestForCreateOrder')

    def requestForUseOrder(self):
        self._printOverrideError('requestForUseOrder')

    def getLeftTime(self):
        self._printOverrideError('getLeftTime')

    def getLeftTimeStr(self):
        self._printOverrideError('getLeftTimeStr')

    def getLeftTimeTooltip(self):
        self._printOverrideError('getLeftTimeTooltip')

    def openQuest(self, questID):
        self._printOverrideError('openQuest')

    def openOrderDetailsWindow(self):
        self._printOverrideError('openOrderDetailsWindow')

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)

    def as_disableOrderS(self, daisable):
        if self._isDAAPIInited():
            return self.flashObject.as_disableOrder(daisable)
