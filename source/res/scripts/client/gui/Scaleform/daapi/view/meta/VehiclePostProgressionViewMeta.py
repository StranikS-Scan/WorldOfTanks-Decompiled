# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePostProgressionViewMeta.py
from gui.Scaleform.framework.entities.View import View

class VehiclePostProgressionViewMeta(View):

    def onGoBackClick(self):
        self._printOverrideError('onGoBackClick')

    def goToVehicleView(self):
        self._printOverrideError('goToVehicleView')

    def compareVehicle(self):
        self._printOverrideError('compareVehicle')

    def demountAllPairs(self):
        self._printOverrideError('demountAllPairs')

    def onAboutClick(self):
        self._printOverrideError('onAboutClick')

    def as_setVehicleTitleS(self, vo):
        return self.flashObject.as_setVehicleTitle(vo) if self._isDAAPIInited() else None

    def as_setDataS(self, vo):
        return self.flashObject.as_setData(vo) if self._isDAAPIInited() else None

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None
