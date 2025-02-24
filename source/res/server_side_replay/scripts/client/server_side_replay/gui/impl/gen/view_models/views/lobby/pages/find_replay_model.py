# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/pages/find_replay_model.py
from server_side_replay.gui.impl.gen.view_models.views.lobby.table_base_model import TableBaseModel

class FindReplayModel(TableBaseModel):
    __slots__ = ('onFind',)

    def __init__(self, properties=7, commands=5):
        super(FindReplayModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FindReplayModel, self)._initialize()
        self.onFind = self._addCommand('onFind')
