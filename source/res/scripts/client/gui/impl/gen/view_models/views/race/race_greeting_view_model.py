# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/race_greeting_view_model.py
from frameworks.wulf import ViewModel

class RaceGreetingViewModel(ViewModel):
    __slots__ = ('onUserProgressionOpen', 'onRaceInfoOpen')

    def _initialize(self):
        super(RaceGreetingViewModel, self)._initialize()
        self.onUserProgressionOpen = self._addCommand('onUserProgressionOpen')
        self.onRaceInfoOpen = self._addCommand('onRaceInfoOpen')
