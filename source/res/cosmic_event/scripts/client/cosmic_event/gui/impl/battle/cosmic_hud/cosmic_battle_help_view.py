# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/cosmic_battle_help_view.py
import CommandMapping
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_battle_help_view_model import CosmicBattleHelpViewModel
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui import InputHandler
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl

class CosmicBattleHelpView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.cosmic_event.battle.cosmic_hud.CosmicBattleHelpView()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = CosmicBattleHelpViewModel()
        super(CosmicBattleHelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CosmicBattleHelpView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        InputHandler.g_instance.onKeyUp += self.__handleKeyUpEvent

    def _finalize(self):
        InputHandler.g_instance.onKeyUp -= self.__handleKeyUpEvent

    def __handleKeyUpEvent(self, event):
        if CommandMapping.g_instance.isFired(CommandMapping.CMD_SHOW_HELP, event.key):
            self.destroyWindow()


class CosmicHelpWindow(WindowImpl):

    def __init__(self):
        super(CosmicHelpWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CosmicBattleHelpView())
