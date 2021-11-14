# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/customization/__init__.py
from collections import namedtuple
from items.components.c11n_constants import ProjectionDecalDirectionTags
from shared_utils import first

def directionByTag(tags):
    directionTags = (tag for tag in tags if tag.startswith(ProjectionDecalDirectionTags.PREFIX))
    return first(directionTags, ProjectionDecalDirectionTags.ANY)


def isNeedToMirrorProjectionDecal(item, slot):
    if not item.canBeMirroredHorizontally:
        return False
    itemDirection = directionByTag(item.tags)
    slotDirection = directionByTag(slot.tags)
    return False if itemDirection == ProjectionDecalDirectionTags.ANY or slotDirection == ProjectionDecalDirectionTags.ANY else itemDirection != slotDirection


CustomizationTooltipContext = namedtuple('CustomizationTooltipContext', ('itemCD', 'vehicleIntCD', 'showInventoryBlock', 'level', 'showOnlyProgressBlock'))
CustomizationTooltipContext.__new__.__defaults__ = (-1,
 -1,
 False,
 -1,
 False)
