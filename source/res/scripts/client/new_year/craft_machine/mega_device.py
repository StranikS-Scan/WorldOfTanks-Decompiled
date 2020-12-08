# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/mega_device.py
from .data_nodes import ViewModelDataNode
from .shared_stuff import MegaDeviceState

class MegaDevice(ViewModelDataNode):

    def __init__(self, viewModel):
        super(MegaDevice, self).__init__(viewModel)
        self.__outputState = MegaDeviceState.INACTIVE

    def getState(self):
        return self.__outputState

    def updateData(self):
        with self._viewModel.transaction() as tx:
            uniqueMegaToysCount = self._nodesHolder.megaToysStorage.getUniqueMegaToysCount()
            tx.setCollectedToys(uniqueMegaToysCount)
            self.__outputState = self._craftCtrl.getDesiredMegaDeviceState(tx.getEnabled())

    def _onInit(self):
        super(MegaDevice, self)._onInit()
        self._viewModel.onToggleChanged += self.__onToggleChanged

    def _onDestroy(self):
        self._viewModel.onToggleChanged -= self.__onToggleChanged
        super(MegaDevice, self)._onDestroy()

    def _initData(self, ctrl):
        self._viewModel.setEnabled(ctrl.isMegaDeviceTurnedOn)

    def _saveData(self, ctrl):
        ctrl.isMegaDeviceTurnedOn = self._viewModel.getEnabled()

    def __onToggleChanged(self, args):
        isTumblerTurnedOn = args.get('selected', False)
        self._viewModel.setEnabled(isTumblerTurnedOn)
        prevOutputState = self.__outputState
        self.updateData()
        if prevOutputState != self.__outputState:
            self._raiseOnDataChanged()
