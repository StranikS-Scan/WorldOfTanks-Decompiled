# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/postmortem_panel/postmortem_panel_view.py
import logging
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_GUI_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.postmorten_panel.postmortem_info_panel_view_model import PostmortemInfoPanelViewModel
from gui.impl.pub import ViewImpl
from gui.shared.events import DeathCamEvent
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
_logger = logging.getLogger(__name__)

class PostmortemPanelView(ViewImpl, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __BLINK_DURATION = 5

    def __init__(self):
        viewSettings = ViewSettings(R.views.battle.postmortem_panel.PostmortemPanelView(), ViewFlags.VIEW, PostmortemInfoPanelViewModel())
        super(PostmortemPanelView, self).__init__(viewSettings)

    @property
    def viewModel(self):
        return super(PostmortemPanelView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PostmortemPanelView, self)._initialize()
        isFrontline = self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE
        self.viewModel.setIsFrontline(isFrontline)
        isFreeCamAvailable = avatar_getter.isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM)
        self.viewModel.setIsFreecamAvailable(isFreeCamAvailable)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        killCamCtrl = self.sessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged += self.__onKillCamStateChanged
        return

    def _finalize(self):
        super(PostmortemPanelView, self)._finalize()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        killCamCtrl = self.sessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged -= self.__onKillCamStateChanged
        self.stopCallback(self.__stopHint)
        return

    def __onPostMortemSwitched(self, _, respawnAvailable):
        self.__startHint()
        if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE:
            self.viewModel.setHasLivesAvailable(respawnAvailable)

    def __onKillCamStateChanged(self, state, _):
        if state is DeathCamEvent.State.FINISHED:
            self.__startHint()

    def __startHint(self):
        self.viewModel.setIsBlinking(True)
        self.delayCallback(self.__BLINK_DURATION, self.__stopHint)

    def __stopHint(self):
        self.viewModel.setIsBlinking(False)
