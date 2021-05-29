# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/trainings_mode_selector_item.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.prb_control.entities.training.legacy.requester import TrainingListRequester

class TrainingsModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('__requester',)

    def _onInitializing(self):
        super(TrainingsModeSelectorItem, self)._onInitializing()
        self.__requester = TrainingListRequester()
        self.__requester.start(self._onListReceived)
        self._onListReceived([])

    def _onDisposing(self):
        self.__requester.stop()

    def _onListReceived(self, prebattles):
        count = sum((1 for _ in prebattles))
        self.viewModel.setCallToAction(backport.text(R.strings.mode_selector.mode.trainingsList.call.c_1(), amount=backport.getIntegralFormat(count)))
