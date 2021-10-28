# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/difficulty_window_view.py
import WWISE
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.difficulty_window_view_model import DifficultyWindowViewModel, WindowTypeEnum
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from gui.prb_control import prb_getters
from skeletons.gui.game_event_controller import IGameEventController
from gui.server_events.game_event.difficulty_progress import DifficultyLevelItem
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.lobby.halloween.event_difficulty_panel_view import EventDifficultyPanelView
from gui.impl.lobby.halloween.sound_constants import EventHangarSound
WINDOW_TYPE_BY_DIFFICULTY = {DifficultyLevelItem.MEDIUM: WindowTypeEnum.MEDIUM,
 DifficultyLevelItem.HARD: WindowTypeEnum.HARD}

class DifficultyWindowView(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)
    FIRST_BOSSFIGHT_LEVEL = 2

    def __init__(self, unlockedLevel):
        settings = ViewSettings(R.views.lobby.halloween.DifficultyWindowView())
        settings.model = DifficultyWindowViewModel()
        self.__difficultyPanel = EventDifficultyPanelView(windowViewName=self.__class__.__name__)
        super(DifficultyWindowView, self).__init__(settings)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)
        self._unlockedLevel = unlockedLevel

    @property
    def viewModel(self):
        return super(DifficultyWindowView, self).getViewModel()

    def _onLoading(self):
        super(DifficultyWindowView, self)._onLoading()
        self._addListeners()
        self.setChildView(self.__difficultyPanel.layoutID, self.__difficultyPanel)
        self.__fillModel()
        if self._unlockedLevel == self.FIRST_BOSSFIGHT_LEVEL:
            WWISE.WW_eventGlobal(EventHangarSound.BOSSFIGHT_OPENED)

    def __fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setWindowType(WINDOW_TYPE_BY_DIFFICULTY.get(self._unlockedLevel))

    def _finalize(self):
        self.__blur.fini()
        self._removeListeners()
        super(DifficultyWindowView, self)._finalize()

    def _addListeners(self):
        self.viewModel.onClose += self._onClose
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined

    def _removeListeners(self):
        self.viewModel.onClose -= self._onClose
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoined

    def _onClose(self):
        self._setDifficultyLevelShown()
        self.destroyWindow()

    def _setDifficultyLevelShown(self):
        level = self.gameEventController.getMaxUnlockedDifficultyLevel()
        difficultyCtrl = self.gameEventController.getDifficultyController()
        difficultyCtrl.setDifficultyLevelShown(level)

    def __onUnitJoined(self, _, __):
        self._onClose()
