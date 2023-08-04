# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/open_box_error.py
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.open_box_error_view_model import OpenBoxErrorViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl

class LootBoxesOpenBoxErrorView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = OpenBoxErrorViewModel()
        super(LootBoxesOpenBoxErrorView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LootBoxesOpenBoxErrorView, self).getViewModel()

    def _getEvents(self):
        return ((g_playerEvents.onDisconnected, self.__onDisconnected), (self.viewModel.toHangar, self.__gotoHangar))

    def __onDisconnected(self):
        self.destroyWindow()

    def __gotoHangar(self):
        parent = self.getParentWindow().parent
        if not parent.typeFlag & WindowFlags.MAIN_WINDOW:
            parent.destroy()
        else:
            self.destroyWindow()


class LootBoxesOpenBoxErrorWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(LootBoxesOpenBoxErrorWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesOpenBoxErrorView(R.views.gui_lootboxes.lobby.gui_lootboxes.OpenBoxErrorView()), parent=parent, layer=WindowLayer.OVERLAY)
