# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/welcome_screen.py
from account_helpers.AccountSettings import LOOT_BOXES_INTRO_SHOWN
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.welcome_screen_model import WelcomeScreenModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_OVERLAY_SOUND_SPACE

class LootBoxesWelcomeScreen(ViewImpl):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    _COMMON_SOUND_SPACE = LOOT_BOXES_OVERLAY_SOUND_SPACE

    def __init__(self):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.WelcomeScreen())
        settings.model = WelcomeScreenModel()
        super(LootBoxesWelcomeScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LootBoxesWelcomeScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.__guiLootBoxes.setSetting(LOOT_BOXES_INTRO_SHOWN, True)
        self.destroyWindow()


class LootBoxesWelcomeScreenWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(LootBoxesWelcomeScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesWelcomeScreen(), layer=WindowLayer.OVERLAY, parent=parent)
