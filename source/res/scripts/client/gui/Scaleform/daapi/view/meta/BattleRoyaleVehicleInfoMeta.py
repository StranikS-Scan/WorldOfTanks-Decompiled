# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleVehicleInfoMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleRoyaleVehicleInfoMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onShowIntro(self):
        self._printOverrideError('onShowIntro')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTabsDataS(self, tabsData):
        return self.flashObject.as_setTabsData(tabsData) if self._isDAAPIInited() else None
