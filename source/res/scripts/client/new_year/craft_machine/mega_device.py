# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/mega_device.py
from items.components.ny_constants import ToyTypes
from .data_nodes import ViewModelDataNode
from .shared_stuff import MegaDeviceState, CraftSettingsNames

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
            isTumblerTurnedOn = tx.getEnabled()
            if isTumblerTurnedOn:
                if uniqueMegaToysCount < len(ToyTypes.MEGA):
                    self.__outputState = MegaDeviceState.ACTIVE
                else:
                    self.__outputState = MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR
            else:
                self.__outputState = MegaDeviceState.INACTIVE

    def _onInit(self):
        super(MegaDevice, self)._onInit()
        self._viewModel.onToggleChanged += self.__onToggleChanged

    def _onDestroy(self):
        self._viewModel.onToggleChanged -= self.__onToggleChanged
        super(MegaDevice, self)._onDestroy()

    def _loadFrom(self, settings):
        isTumblerTurnedOn = settings.getValue(CraftSettingsNames.MEGA_DEVICE_TURNED_ON, False)
        self._viewModel.setEnabled(isTumblerTurnedOn)

    def _saveTo(self, settings):
        isTumblerTurnedOn = self._viewModel.getEnabled()
        settings.setValue(CraftSettingsNames.MEGA_DEVICE_TURNED_ON, isTumblerTurnedOn)

    def __onToggleChanged(self, args):
        isTumblerTurnedOn = args.get('selected', False)
        self._viewModel.setEnabled(isTumblerTurnedOn)
        prevOutputState = self.__outputState
        self.updateData()
        if prevOutputState != self.__outputState:
            self._raiseOnDataChanged()
