# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/shared/tooltips/contexts.py
from helpers import dependency
from gui.shared.tooltips import TOOLTIP_COMPONENT
from gui.shared.tooltips.contexts import ToolTipContext
from skeletons.gui.shared import IItemsCache

class FallTanksHangarAmmoContext(ToolTipContext):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(FallTanksHangarAmmoContext, self).__init__(TOOLTIP_COMPONENT.HANGAR)

    def buildItem(self, intCD):
        return self.__itemsCache.items.getItemByCD(int(intCD))
