# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/antiduplicator.py
from .data_nodes import ViewModelDataNode
from .shared_stuff import AntiduplicatorState, MegaDeviceState

class Antiduplicator(ViewModelDataNode):

    def __init__(self, viewModel):
        super(Antiduplicator, self).__init__(viewModel)
        self.__outputState = AntiduplicatorState.INACTIVE

    def getState(self):
        return self.__outputState

    def updateData(self):
        with self._viewModel.transaction() as tx:
            fillerCount = self._nodesHolder.fillersStorage.getFillerCount()
            tx.setCountFillers(fillerCount)
            megaDeviceState = self._nodesHolder.megaDevice.getState()
            if megaDeviceState in MegaDeviceState.ACTIVATED:
                tx.setEnabled(False)
                self.__outputState = AntiduplicatorState.INACTIVE
                return
            tx.setEnabled(True)
            isTumblerTurnedOn = tx.getTumblerTurnOn()
            if isTumblerTurnedOn:
                if fillerCount > 0:
                    self.__outputState = AntiduplicatorState.ACTIVE
                else:
                    self.__outputState = AntiduplicatorState.ERROR
            else:
                self.__outputState = AntiduplicatorState.INACTIVE
            self.__updateFillerStateVisibility(tx)

    def _onInit(self):
        super(Antiduplicator, self)._onInit()
        self._viewModel.onTumblerToggleChanged += self.__onAntidupTumblerToggleChanged
        self._viewModel.onHidingUsingFillerStart += self.__onHidingUsingFillerStart

    def _onDestroy(self):
        self._viewModel.onTumblerToggleChanged -= self.__onAntidupTumblerToggleChanged
        self._viewModel.onHidingUsingFillerStart -= self.__onHidingUsingFillerStart
        super(Antiduplicator, self)._onDestroy()

    def _initData(self, ctrl):
        self._viewModel.setTumblerTurnOn(False)

    def __onHidingUsingFillerStart(self):
        self._viewModel.onTumblerToggleChanged({'selected': False})

    def __onAntidupTumblerToggleChanged(self, args):
        tumblerTurnedOn = args.get('selected', False)
        self._viewModel.setTumblerTurnOn(tumblerTurnedOn)
        prevState = self.__outputState
        self.updateData()
        if self.__outputState != prevState:
            self._raiseOnDataChanged()

    def __updateFillerStateVisibility(self, model):
        if self.__outputState == AntiduplicatorState.ACTIVE:
            model.setFillerState(model.INSERTED)
        elif self.__outputState in (AntiduplicatorState.INACTIVE, AntiduplicatorState.ERROR):
            model.setFillerState(model.EMPTY)
