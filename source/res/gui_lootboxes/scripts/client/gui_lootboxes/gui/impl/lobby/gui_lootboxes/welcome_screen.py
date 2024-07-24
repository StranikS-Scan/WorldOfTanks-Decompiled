# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/welcome_screen.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.welcome_screen_model import WelcomeScreenModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE

class LootBoxesWelcomeScreen(ViewImpl):
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE
    __slots__ = ('__closeCallback',)

    def __init__(self, layoutID, closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.model = WelcomeScreenModel()
        super(LootBoxesWelcomeScreen, self).__init__(settings)
        self.__closeCallback = closeCallback

    @property
    def viewModel(self):
        return super(LootBoxesWelcomeScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        if self.__closeCallback and callable(self.__closeCallback):
            self.__closeCallback()
        self.destroyWindow()


class LootBoxesWelcomeScreenWindow(LobbyWindow):
    __slots__ = ()
    DEFAULT_LAYOUT_ID = R.views.gui_lootboxes.lobby.gui_lootboxes.WelcomeScreen()

    def __init__(self, layoutID=None, closeCallback=None, parent=None):
        layoutID = layoutID or self.DEFAULT_LAYOUT_ID
        super(LootBoxesWelcomeScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesWelcomeScreen(layoutID=layoutID, closeCallback=closeCallback), layer=WindowLayer.OVERLAY, parent=parent)
