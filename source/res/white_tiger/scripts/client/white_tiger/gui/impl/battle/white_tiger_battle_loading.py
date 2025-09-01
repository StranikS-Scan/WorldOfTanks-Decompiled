# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/battle/white_tiger_battle_loading.py
import logging
import BigWorld
from white_tiger.gui.wt_event_helpers import isBoss
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from white_tiger.gui.impl.gen.view_models.views.battle.white_tiger_loading_view_model import WhiteTigerLoadingViewModel, PlayerTypeEnum
from helpers import dependency
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class WhiteTigerBattleLoadingView(ViewImpl, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.white_tiger.battle.WhiteTigerBattleLoading(), model=WhiteTigerLoadingViewModel())
        super(WhiteTigerBattleLoadingView, self).__init__(settings)
        with self.viewModel.transaction() as model:
            if self.__isBossPlayer():
                model.setPlayerType(PlayerTypeEnum.BOSS)
            else:
                model.setPlayerType(PlayerTypeEnum.HUNTER)

    @property
    def viewModel(self):
        return super(WhiteTigerBattleLoadingView, self).getViewModel()

    def updateSpaceLoadProgress(self, progress):
        self.__updateProgress(progress)

    def _subscribe(self):
        super(WhiteTigerBattleLoadingView, self)._subscribe()
        self.sessionProvider.addArenaCtrl(self)

    def _unsubscribe(self):
        super(WhiteTigerBattleLoadingView, self)._unsubscribe()
        self.sessionProvider.removeArenaCtrl(self)

    def _onLoading(self, *args, **kwargs):
        super(WhiteTigerBattleLoadingView, self)._onLoading(*args, **kwargs)
        self.__updateProgress(0)

    def __updateProgress(self, progress):
        with self.viewModel.transaction() as model:
            model.setCurrentProgress(int(progress * 100))

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)


class WhiteTigerBattleLoadingWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WhiteTigerBattleLoadingWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=WhiteTigerBattleLoadingView(), layer=WindowLayer.OVERLAY, parent=parent)
