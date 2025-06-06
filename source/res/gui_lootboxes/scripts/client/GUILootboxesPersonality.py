# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/GUILootboxesPersonality.py
from gui_lootboxes.gui.Scaleform import registerLootboxesTooltipsBuilders
from gui_lootboxes.gui.game_control import registerGuiLootBoxesGameControllers
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.entry_point_view import LootBoxesEntryPointWidget
from gui_lootboxes.messenger.formatters.collections_by_type import registerLootBoxClientFormatters, registerLootBoxServerFormatters
from gui_lootboxes.notification import registerClientNotificationListener, registerClientNotificationHandler
from gui.impl.gen import R
from gui.shared.system_factory import registerCarouselEventEntryPoint
from gui.impl.lobby.loot_box.unique_reward_handler import MTLUniqueRewardHandler
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import registerHandler

def preInit():
    registerCarouselEventEntryPoint(R.views.gui_lootboxes.lobby.gui_lootboxes.EntryPointView(), LootBoxesEntryPointWidget)
    registerLootboxesTooltipsBuilders()
    registerGuiLootBoxesGameControllers()
    registerClientNotificationListener()
    registerClientNotificationHandler()
    registerLootBoxClientFormatters()
    registerLootBoxServerFormatters()
    registerHandler(MTLUniqueRewardHandler)


def init():
    pass


def start():
    pass


def fini():
    pass
