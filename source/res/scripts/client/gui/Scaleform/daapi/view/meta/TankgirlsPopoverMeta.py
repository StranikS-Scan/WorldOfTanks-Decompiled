# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankgirlsPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class TankgirlsPopoverMeta(SmartPopOverView):

    def onRecruitClick(self, idx):
        self._printOverrideError('onRecruitClick')

    def as_setListDataProviderS(self, data):
        """
        :param data: Represented by DataProvider.<TankgirlVO> (AS)
        """
        return self.flashObject.as_setListDataProvider(data) if self._isDAAPIInited() else None
