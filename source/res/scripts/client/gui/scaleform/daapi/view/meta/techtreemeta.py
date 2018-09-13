# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechTreeMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TechTreeMeta(DAAPIModule):

    def requestNationTreeData(self):
        self._printOverrideError('requestNationTreeData')

    def getNationTreeData(self, nationName):
        self._printOverrideError('getNationTreeData')

    def goToNextVehicle(self, vehCD):
        self._printOverrideError('goToNextVehicle')

    def onCloseTechTree(self):
        self._printOverrideError('onCloseTechTree')

    def as_setAvailableNationsS(self, nations):
        if self._isDAAPIInited():
            return self.flashObject.as_setAvailableNations(nations)

    def as_setSelectedNationS(self, nationName):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedNation(nationName)

    def as_refreshNationTreeDataS(self, nationName):
        if self._isDAAPIInited():
            return self.flashObject.as_refreshNationTreeData(nationName)

    def as_setUnlockPropsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setUnlockProps(data)
