# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewMeta.py
from gui.Scaleform.framework.entities.View import View

class VehiclePreviewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onBuyOrResearchClick(self):
        self._printOverrideError('onBuyOrResearchClick')

    def onOpenInfoTab(self, index):
        self._printOverrideError('onOpenInfoTab')

    def onCompareClick(self):
        self._printOverrideError('onCompareClick')

    def as_setStaticDataS(self, data):
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_updateInfoDataS(self, data):
        return self.flashObject.as_updateInfoData(data) if self._isDAAPIInited() else None

    def as_updateVehicleStatusS(self, status):
        return self.flashObject.as_updateVehicleStatus(status) if self._isDAAPIInited() else None

    def as_updateBuyingPanelS(self, data):
        return self.flashObject.as_updateBuyingPanel(data) if self._isDAAPIInited() else None
