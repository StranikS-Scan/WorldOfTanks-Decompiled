# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortSettingsDefenceHourPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortSettingsDefenceHourPopoverMeta(SmartPopOverView):

    def onApply(self, hour):
        self._printOverrideError('onApply')

    def as_setDataS(self, data):
        """
        :param data: Represented by DefenceHourPopoverVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTextsS(self, data):
        """
        :param data: Represented by DefenceHourPopoverVO (AS)
        """
        return self.flashObject.as_setTexts(data) if self._isDAAPIInited() else None
