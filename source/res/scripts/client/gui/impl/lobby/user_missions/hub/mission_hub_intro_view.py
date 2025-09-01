# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/mission_hub_intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.mission_hub_intro_view_model import MissionHubIntroViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur

class MissionHubIntroView(ViewImpl):
    __slots__ = ('__header', '__description', '__icon', '__buttonText')

    def __init__(self, header, description, icon, buttonText=None):
        settings = ViewSettings(R.views.mono.user_missions.hub.mission_hub_intro_view(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW)
        settings.model = MissionHubIntroViewModel()
        self.__header = header
        self.__description = description
        self.__icon = icon
        if buttonText is None:
            self.__buttonText = R.strings.user_missions.welcome.button()
        else:
            self.__buttonText = buttonText
        super(MissionHubIntroView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(MissionHubIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MissionHubIntroView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setHeader(self.__header)
            vm.setDescription(self.__description)
            vm.setIcon(self.__icon)
            vm.setButtonText(self.__buttonText)

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose),)

    def _onClose(self):
        self.destroyWindow()


class MissionHubIntroWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, header, icon, description, buttonText=None):
        super(MissionHubIntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MissionHubIntroView(header, icon, description, buttonText), layer=WindowLayer.FULLSCREEN_WINDOW)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.TOP_SUB_VIEW)

    def _finalize(self):
        self.__blur.fini()
        super(MissionHubIntroWindow, self)._finalize()
