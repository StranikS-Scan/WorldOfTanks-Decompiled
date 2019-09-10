# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ResearchViewMeta(View):

    def request4Buy(self, itemCD):
        self._printOverrideError('request4Buy')

    def request4Info(self, itemCD, rootCD):
        self._printOverrideError('request4Info')

    def request4Restore(self, itemCD):
        self._printOverrideError('request4Restore')

    def showSystemMessage(self, typeString, message):
        self._printOverrideError('showSystemMessage')

    def goToBlueprintView(self, itemCD):
        self._printOverrideError('goToBlueprintView')

    def goToNationChangeView(self, itemCD):
        self._printOverrideError('goToNationChangeView')

    def as_setNodesStatesS(self, primary, data):
        return self.flashObject.as_setNodesStates(primary, data) if self._isDAAPIInited() else None

    def as_setNext2UnlockS(self, data):
        return self.flashObject.as_setNext2Unlock(data) if self._isDAAPIInited() else None

    def as_setVehicleTypeXPS(self, xps):
        return self.flashObject.as_setVehicleTypeXP(xps) if self._isDAAPIInited() else None

    def as_setInventoryItemsS(self, data):
        return self.flashObject.as_setInventoryItems(data) if self._isDAAPIInited() else None

    def as_setNodeVehCompareDataS(self, data):
        return self.flashObject.as_setNodeVehCompareData(data) if self._isDAAPIInited() else None
