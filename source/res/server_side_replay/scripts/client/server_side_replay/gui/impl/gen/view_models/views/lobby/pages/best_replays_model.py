# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/pages/best_replays_model.py
from frameworks.wulf import Array
from server_side_replay.gui.impl.gen.view_models.views.lobby.table_base_model import TableBaseModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.top_replay_model import TopReplayModel

class BestReplaysModel(TableBaseModel):
    __slots__ = ('onLike', 'onTopReplaysWatch')

    def __init__(self, properties=8, commands=6):
        super(BestReplaysModel, self).__init__(properties=properties, commands=commands)

    def getTopReplays(self):
        return self._getArray(7)

    def setTopReplays(self, value):
        self._setArray(7, value)

    @staticmethod
    def getTopReplaysType():
        return TopReplayModel

    def _initialize(self):
        super(BestReplaysModel, self)._initialize()
        self._addArrayProperty('topReplays', Array())
        self.onLike = self._addCommand('onLike')
        self.onTopReplaysWatch = self._addCommand('onTopReplaysWatch')
