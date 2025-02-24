# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/root_view_model.py
from server_side_replay.gui.impl.gen.view_models.views.lobby.enums import ReplaysViews
from frameworks.wulf import ViewModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.pages.best_replays_model import BestReplaysModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.pages.find_replay_model import FindReplayModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.pages.my_replays_model import MyReplaysModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.sidebar_model import SidebarModel

class RootViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=5, commands=1):
        super(RootViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def sidebar(self):
        return self._getViewModel(0)

    @staticmethod
    def getSidebarType():
        return SidebarModel

    @property
    def bestReplays(self):
        return self._getViewModel(1)

    @staticmethod
    def getBestReplaysType():
        return BestReplaysModel

    @property
    def myReplays(self):
        return self._getViewModel(2)

    @staticmethod
    def getMyReplaysType():
        return MyReplaysModel

    @property
    def findReplay(self):
        return self._getViewModel(3)

    @staticmethod
    def getFindReplayType():
        return FindReplayModel

    def getPageViewId(self):
        return ReplaysViews(self._getNumber(4))

    def setPageViewId(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(RootViewModel, self)._initialize()
        self._addViewModelProperty('sidebar', SidebarModel())
        self._addViewModelProperty('bestReplays', BestReplaysModel())
        self._addViewModelProperty('myReplays', MyReplaysModel())
        self._addViewModelProperty('findReplay', FindReplayModel())
        self._addNumberProperty('pageViewId')
        self.onClose = self._addCommand('onClose')
