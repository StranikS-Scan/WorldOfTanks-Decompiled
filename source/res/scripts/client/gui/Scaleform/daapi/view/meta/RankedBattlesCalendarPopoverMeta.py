# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesCalendarPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class RankedBattlesCalendarPopoverMeta(SmartPopOverView):

    def onDaySelect(self, date):
        self._printOverrideError('onDaySelect')

    def as_setDataS(self, data):
        """
        :param data: Represented by RankedBattlesCalendarVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setDayDataS(self, data):
        """
        :param data: Represented by RankedBattlesCalendarDayVO (AS)
        """
        return self.flashObject.as_setDayData(data) if self._isDAAPIInited() else None
