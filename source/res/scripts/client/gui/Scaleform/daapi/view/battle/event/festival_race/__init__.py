# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/__init__.py
MINIMAP_MIN_SIZE_INDEX = 0
MINIMAP_MAX_SIZE_INDEX = 1

def clampMinimapSizeIndex(index):
    return min(max(index, MINIMAP_MIN_SIZE_INDEX), MINIMAP_MAX_SIZE_INDEX)
