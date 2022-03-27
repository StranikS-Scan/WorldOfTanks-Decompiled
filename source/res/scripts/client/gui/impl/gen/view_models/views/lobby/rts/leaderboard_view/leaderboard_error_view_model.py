# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/leaderboard_view/leaderboard_error_view_model.py
from frameworks.wulf import ViewModel

class LeaderboardErrorViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LeaderboardErrorViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getShowReloadButton(self):
        return self._getBool(2)

    def setShowReloadButton(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(LeaderboardErrorViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('showReloadButton', False)
