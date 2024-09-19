# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: wt/scripts/client/wt_personality.py
from gui.impl.gen import R
from gui.shared.system_factory import registerCarouselEventEntryPoint
from debug_utils import LOG_DEBUG
from gui.impl.lobby.wt_event.wt_event_loot_box_entry_point import WTEventLootBoxEntrancePointWidget

def preInit():
    registerCarouselEventEntryPoint(R.views.lobby.wt_event.WTEventBoxEntryPoint(), WTEventLootBoxEntrancePointWidget)


def init():
    LOG_DEBUG('init', __name__)


def start():
    pass


def fini():
    pass
