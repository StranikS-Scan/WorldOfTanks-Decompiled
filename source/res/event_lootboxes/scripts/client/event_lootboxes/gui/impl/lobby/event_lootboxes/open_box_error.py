# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/open_box_error.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.open_box_error_view_model import OpenBoxErrorViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl

class EventLootBoxesOpenBoxErrorView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = OpenBoxErrorViewModel()
        super(EventLootBoxesOpenBoxErrorView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventLootBoxesOpenBoxErrorView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _finalize(self):
        g_playerEvents.onDisconnected -= self.__onDisconnected

    def __onDisconnected(self):
        self.destroyWindow()


class EventLootBoxesOpenBoxErrorWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(EventLootBoxesOpenBoxErrorWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EventLootBoxesOpenBoxErrorView(R.views.event_lootboxes.lobby.event_lootboxes.OpenBoxErrorView()), parent=parent)
