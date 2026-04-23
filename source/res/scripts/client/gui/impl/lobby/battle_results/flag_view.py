# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/flag_view.py
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.impl.gen.view_models.views.lobby.battle_results.flag.flag_view_model import FlagViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.lobby_state_machine.router import SubstateRouter
_TEXTURE_PATH = 'particles/content_deferred/GFX_models/environment/hangar_v4/screen_flag.dds'

class FlagWindow(WindowImpl):

    def __init__(self):
        super(FlagWindow, self).__init__(wndFlags=WindowFlags.SURFACE, content=FlagView(), name=_TEXTURE_PATH)


class FlagView(ViewImpl, IRoutableView):
    _VIEW_SETTINGS_LAYOUT_ID = R.views.mono.post_battle.flag()
    _VIEW_MODEL = FlagViewModel

    def __init__(self):
        settings = ViewSettings(self._VIEW_SETTINGS_LAYOUT_ID)
        settings.model = self._VIEW_MODEL()
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateByCls(self._getLsmStateClass()))
        super(FlagView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(FlagView, self)._onLoading(*args, **kwargs)
        self.__router.init()

    def _finalize(self):
        self.__router.fini()
        self.__router = None
        super(FlagView, self)._finalize()
        return

    def _getLsmStateClass(self):
        from gui.impl.lobby.battle_results.states import PostBattleResultsState
        return PostBattleResultsState

    def getRouterModel(self):
        return self.viewModel.router

    @property
    def viewModel(self):
        return super(FlagView, self).getViewModel()
