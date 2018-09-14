# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ResearchViewMeta(View):

    def request4Unlock(self, itemCD, parentID, unlockIdx, xpCost):
        self._printOverrideError('request4Unlock')

    def request4Buy(self, itemCD):
        self._printOverrideError('request4Buy')

    def request4Info(self, itemCD, rootCD):
        self._printOverrideError('request4Info')

    def request4SelectInHangar(self, itemCD):
        self._printOverrideError('request4SelectInHangar')

    def showSystemMessage(self, typeString, message):
        self._printOverrideError('showSystemMessage')

    def as_setNodesStatesS(self, primary, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setNodesStates(primary, data)

    def as_setNext2UnlockS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setNext2Unlock(data)

    def as_setVehicleTypeXPS(self, xps):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleTypeXP(xps)

    def as_setInventoryItemsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInventoryItems(data)

    def as_useXMLDumpingS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_useXMLDumping()
