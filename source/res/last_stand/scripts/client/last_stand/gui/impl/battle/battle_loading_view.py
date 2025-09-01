# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/battle/battle_loading_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from last_stand.gui.impl.gen.view_models.views.battle.event_loading_view_model import EventLoadingViewModel
from helpers import dependency
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class BattleLoadingView(ViewImpl, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID=layoutID, model=EventLoadingViewModel())
        super(BattleLoadingView, self).__init__(settings)

    def updateSpaceLoadProgress(self, progress):
        self.__updateProgress(progress)

    def _subscribe(self):
        super(BattleLoadingView, self)._subscribe()
        self.sessionProvider.addArenaCtrl(self)

    def _unsubscribe(self):
        super(BattleLoadingView, self)._unsubscribe()
        self.sessionProvider.removeArenaCtrl(self)

    def _onLoading(self, *args, **kwargs):
        super(BattleLoadingView, self)._onLoading(*args, **kwargs)
        self.__updateProgress(0)

    @replaceNoneKwargsModel
    def __updateProgress(self, progress, model=None):
        model.setCurrentProgress(int(progress * 100))


class BattleLoadingWindow(WindowImpl):
    __slots__ = ()
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parent=None):
        super(BattleLoadingWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=BattleLoadingView(R.views.last_stand.mono.battle.battle_loading()), layer=WindowLayer.OVERLAY, parent=parent)
