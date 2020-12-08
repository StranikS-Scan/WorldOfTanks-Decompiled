# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYSelectVehiclePopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NYSelectVehiclePopoverMeta(SmartPopOverView):

    def onSelectVehicle(self, index):
        self._printOverrideError('onSelectVehicle')

    def applyFilters(self, nation, vehicleType, level):
        self._printOverrideError('applyFilters')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None
