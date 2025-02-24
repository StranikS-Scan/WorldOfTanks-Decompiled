# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/pages/find_replay_page.py
import logging
from typing import TYPE_CHECKING
import BigWorld
from BattleReplay import BattleReplay
from adisp import adisp_process
from server_side_replay.gui.impl.gen.view_models.views.lobby.pages.find_replay_model import FindReplayModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.enums import ReplaysViews
from server_side_replay.gui.impl.gen.view_models.views.lobby.table_base_model import State
from gui.impl.gui_decorators import args2params
from server_side_replay.gui.impl.lobby.pages import PageSubModelPresenter
from server_side_replay.gui.impl.lobby.utils import WebReplaysHelper
from server_side_replay.gui.wgcg.data_wrappers.server_replays import DataNames
from server_side_replay.gui.wgcg.providers.server_replays_provider import ServerReplaysProvider
if TYPE_CHECKING:
    from typing import Optional
    from server_side_replay.gui.wgcg.data_wrappers import server_replays
_logger = logging.getLogger(__name__)

class FindReplayPage(PageSubModelPresenter):

    def __init__(self, viewModel, parentView):
        self.__foundReplay = None
        self.__serverReplayProvider = ServerReplaysProvider()
        self.__serverReplayProvider.start()
        super(FindReplayPage, self).__init__(viewModel, parentView)
        return

    @property
    def pageId(self):
        return ReplaysViews.FINDREPLAY

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        self.__updateState()
        super(FindReplayPage, self).initialize(*args, **kwargs)

    def _getEvents(self):
        return super(FindReplayPage, self)._getEvents() + ((self.__serverReplayProvider.onDataReceived, self.__onDataReceived),
         (self.__serverReplayProvider.onDataFailed, self.__onDataFailed),
         (self.viewModel.onFind, self.__onFind),
         (self.viewModel.onWatch, self.__onWatch),
         (self.viewModel.onRefresh, self.__onRefresh))

    def __updateState(self):
        with self.viewModel.transaction() as tx:
            tx.setState(State.INITIAL)

    def __onRefresh(self):
        with self.viewModel.transaction() as tx:
            tx.setState(State.INITIAL)
            self.__foundReplay = None
        return

    @args2params(unicode)
    def __onFind(self, searchText):
        _logger.info('__onFind: %s', searchText)
        with self.viewModel.transaction() as tx:
            tx.setState(State.INITIAL)
            tx.setIsLoading(True)
            self.__serverReplayProvider.findReplay(searchText)

    @adisp_process
    def __onWatch(self):
        if self.__foundReplay is None:
            _logger.error('Can not find the found replay')
            return
        else:
            helper = WebReplaysHelper()
            relativePath = yield helper.getRelativePath(self.__foundReplay.replay_link)
            BattleReplay.predefinedVehicleID = 0
            BigWorld.player().startWatchingReplay(relativePath)
            return

    def __onDataReceived(self, dataName, data):
        if dataName == DataNames.FIND_REPLAY:
            with self.viewModel.transaction() as tx:
                tx.setState(State.SUCCESS)
                tx.setIsLoading(False)
                self.__foundReplay = data
            return

    def __onDataFailed(self, dataName):
        if dataName == DataNames.FIND_REPLAY:
            with self.viewModel.transaction() as tx:
                tx.setState(State.ERROR)
                tx.setIsLoading(False)
            return
