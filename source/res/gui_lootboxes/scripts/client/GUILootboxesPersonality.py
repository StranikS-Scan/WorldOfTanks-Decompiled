# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/GUILootboxesPersonality.py
from constants import LOOTBOX_LIMIT_ITEM_PREFIX
from gui.server_events.EventsCache import NOT_FOR_PERSONAL_MISSIONS_TOKENS
from gui_lootboxes.gui.Scaleform import registerLootboxesTooltipsBuilders
from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX
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
    NOT_FOR_PERSONAL_MISSIONS_TOKENS.extend((TOKEN_COMPENSATION_PREFIX, LOOTBOX_LIMIT_ITEM_PREFIX))


def init():
    pass


def start():
    pass


def fini():
    pass
