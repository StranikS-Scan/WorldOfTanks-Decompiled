# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreview20Meta.py
from gui.Scaleform.framework.entities.View import View

class VehiclePreview20Meta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onOpenInfoTab(self, index):
        self._printOverrideError('onOpenInfoTab')

    def onCompareClick(self):
        self._printOverrideError('onCompareClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTabsDataS(self, tabs):
        return self.flashObject.as_setTabsData(tabs) if self._isDAAPIInited() else None

    def as_show3DSceneTooltipS(self, id, args):
        return self.flashObject.as_show3DSceneTooltip(id, args) if self._isDAAPIInited() else None

    def as_hide3DSceneTooltipS(self):
        return self.flashObject.as_hide3DSceneTooltip() if self._isDAAPIInited() else None

    def as_setBottomPanelS(self, linkage):
        return self.flashObject.as_setBottomPanel(linkage) if self._isDAAPIInited() else None
