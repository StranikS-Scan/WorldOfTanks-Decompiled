# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/event_welcome_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from helpers.time_utils import getTimestampFromUTC
from story_mode.account_settings import setWelcomeScreenSeen
from story_mode.gui.impl.gen.view_models.views.lobby.event_welcome_view_model import EventWelcomeViewModel
from story_mode_common.configs.story_mode_settings import settingsSchema

class EventWelcomeView(ViewImpl):
    __slots__ = ()
    layoutID = R.views.story_mode.lobby.EventWelcomeView()

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.VIEW, EventWelcomeViewModel())
        super(EventWelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventWelcomeView, self).getViewModel()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onClose, self.__onClose), (viewModel.onSubmit, self.__onClose), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoading(self, *args, **kwargs):
        super(EventWelcomeView, self)._onLoading(*args, **kwargs)
        self.__fillViewModel()

    def __fillViewModel(self):
        settings = settingsSchema.getModel()
        if settings:
            self.viewModel.setStartDate(getTimestampFromUTC(settings.entryPoint.eventStartAt.timetuple()))
            self.viewModel.setEndDate(getTimestampFromUTC(settings.entryPoint.eventEndAt.timetuple()))

    def __onClose(self):
        setWelcomeScreenSeen()
        self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()


class EventWelcomeWindow(WindowImpl):

    def __init__(self, layoutID):
        super(EventWelcomeWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EventWelcomeView(layoutID=layoutID))
