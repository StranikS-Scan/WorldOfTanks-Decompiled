# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/antiduplicator.py
import typing
from items.components.ny_constants import FillerState
from .data_nodes import ViewModelDataNode
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_antiduplicator_model import NyCraftAntiduplicatorModel

class Antiduplicator(ViewModelDataNode):

    def __init__(self, viewModel):
        super(Antiduplicator, self).__init__(viewModel)
        self.__fillerState = FillerState.INACTIVE
        self.__isCrafting = False

    def getAntiDuplicatorState(self):
        return self.__fillerState

    def updateData(self):
        if self.__isCrafting:
            return
        with self._viewModel.transaction() as tx:
            fillersCount = self._nodesHolder.fillersStorage.getFillersCount()
            tx.setFillersCount(fillersCount)
            tx.setShardsCount(self._nodesHolder.shardsStorage.getShardsCount())
            if self.__fillerState.value == FillerState.USE_CHARGES.value and fillersCount <= 0:
                self.__fillerState = FillerState.INACTIVE
            tx.setAntiDuplicatorState(self.__fillerState.value)

    def updateCrafting(self, isInProgress=False):
        self.__isCrafting = isInProgress

    def _onInit(self):
        super(Antiduplicator, self)._onInit()
        self._viewModel.onTumblerStateChanged += self.__onTumblerStateChanged
        self._viewModel.onFillerHidingStart += self.__onFillerHidingStart

    def _onDestroy(self):
        self.__isCrafting = False
        self._viewModel.onFillerHidingStart -= self.__onFillerHidingStart
        self._viewModel.onTumblerStateChanged -= self.__onTumblerStateChanged
        super(Antiduplicator, self)._onDestroy()

    def _initData(self, ctrl):
        self.__fillerState = FillerState.INACTIVE

    def _saveData(self, ctrl):
        ctrl.fillerState = FillerState.INACTIVE

    def __onFillerHidingStart(self):
        self.__onTumblerStateChanged({'state': FillerState.INACTIVE.value})
        self.__isInCrafting = False

    def __onTumblerStateChanged(self, args):
        prevState = self.__fillerState.value
        self.__fillerState = FillerState(args.get('state', FillerState.ERROR.value))
        self.updateData()
        if self.__fillerState.value != prevState:
            self._raiseOnDataChanged()
