# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/tankmen_cfg.py
from typing import TYPE_CHECKING
from constants import ITEM_DEFS_PATH
from items.readers import skills_readers
from items.readers import tankmen_readers
if TYPE_CHECKING:
    from items.components import tankmen_components
_g_loreConfig = None
_g_autoFillConfig = None

def getLoreConfig():
    global _g_loreConfig
    if _g_loreConfig is None:
        _g_loreConfig = tankmen_readers.readLoreConfig(ITEM_DEFS_PATH + 'tankmen/common/lore.xml')
    return _g_loreConfig


def getAutoFillConfig():
    global _g_autoFillConfig
    if _g_autoFillConfig is None:
        _g_autoFillConfig = skills_readers.readAutoFillConfig(ITEM_DEFS_PATH + 'tankmen/common/autofill.xml')
    return _g_autoFillConfig
