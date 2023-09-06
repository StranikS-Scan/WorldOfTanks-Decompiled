# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/GUILootboxesPersonality.py
from gui_lootboxes.gui.Scaleform import registerLootboxesTooltipsBuilders
from gui_lootboxes.gui.game_control import registerGuiLootBoxesGameControllers
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.entry_point_view import LootBoxesEntryPointWidget
from gui_lootboxes.messenger.formatters.collections_by_type import registerLootBoxClientFormatters, registerLootBoxServerFormatters
from gui.impl.gen import R
from gui.shared.system_factory import registerCarouselEventEntryPoint

def preInit():
    registerCarouselEventEntryPoint(R.views.gui_lootboxes.lobby.gui_lootboxes.EntryPointView(), LootBoxesEntryPointWidget)
    registerLootboxesTooltipsBuilders()
    registerGuiLootBoxesGameControllers()
    registerLootBoxClientFormatters()
    registerLootBoxServerFormatters()


def init():
    pass


def start():
    pass


def fini():
    pass
