# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/EventLootboxesPersonality.py
from event_lootboxes.gui.Scaleform import registerLootboxesTooltipsBuilders
from event_lootboxes.gui.impl.lobby.event_lootboxes.entry_point_view import EventLootBoxesEntryPointWidget
from gui.impl.gen import R
from gui.shared.system_factory import registerCarouselEventEntryPoint

def preInit():
    registerCarouselEventEntryPoint(R.views.event_lootboxes.lobby.event_lootboxes.EntryPointView(), EventLootBoxesEntryPointWidget)
    registerLootboxesTooltipsBuilders()


def init():
    pass


def start():
    pass


def fini():
    pass
