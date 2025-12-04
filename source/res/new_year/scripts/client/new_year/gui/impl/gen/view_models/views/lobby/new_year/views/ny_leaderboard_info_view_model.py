# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/ny_leaderboard_info_view_model.py
from frameworks.wulf import ViewModel

class NyLeaderboardInfoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(NyLeaderboardInfoViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NyLeaderboardInfoViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
