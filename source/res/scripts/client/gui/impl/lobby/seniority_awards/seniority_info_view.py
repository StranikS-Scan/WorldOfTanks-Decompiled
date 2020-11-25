# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_info_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_info_view_model import SeniorityInfoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from seniority_awards_sounds import playSound, SeniorityInfoViewEvents

class SeniorityInfoView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = SeniorityInfoViewModel()
        super(SeniorityInfoView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(SeniorityInfoView, self)._initialize()
        playSound(SeniorityInfoViewEvents.ENTRY_VIEW_ENTER)

    def _finalize(self):
        playSound(SeniorityInfoViewEvents.ENTRY_VIEW_EXIT)
        super(SeniorityInfoView, self)._finalize()

    @property
    def viewModel(self):
        return super(SeniorityInfoView, self).getViewModel()


class SeniorityInfoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, viewID=R.views.lobby.seniority_awards.SeniorityInfoView(), parent=None):
        super(SeniorityInfoViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SeniorityInfoView(viewID), parent=parent)
