# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dragon_boat/dragon_boat_team_finish_view.py
import WWISE
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.game_control.dragon_boat_controller import DBOAT_REGISTRATION
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dragon_boat.dragon_boat_finish_view_model import DragonBoatFinishViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showDragonBoatTab

class DragonBoatTeamFinishView(ViewImpl):
    __slots__ = ('__closeCallback', '__team')

    def __init__(self, team, closeCallback=None):
        settings = ViewSettings(R.views.lobby.dragon_boats.FinishScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = DragonBoatFinishViewModel()
        self.__closeCallback = closeCallback
        self.__team = team
        super(DragonBoatTeamFinishView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DragonBoatTeamFinishView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onPickNewTeamBtnClick += self.__onPickNewTeam

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onPickNewTeamBtnClick -= self.__onPickNewTeam

    def _onLoading(self, *args, **kwargs):
        super(DragonBoatTeamFinishView, self)._onLoading(*args, **kwargs)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_cn_dragonboat_finish()))
        with self.viewModel.transaction() as tx:
            tx.setTeam(self.__team)

    def __onClose(self):
        self.destroyWindow()
        if self.__closeCallback is not None:
            self.__closeCallback()
        return

    def __onPickNewTeam(self):
        self.destroyWindow()
        showDragonBoatTab(url=DBOAT_REGISTRATION)


class DragonBoatTeamFinishWindow(LobbyWindow):

    def __init__(self, team=1, parent=None, closeCallback=None):
        super(DragonBoatTeamFinishWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.OVERLAY, content=DragonBoatTeamFinishView(team, closeCallback), parent=parent)
