# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/mega_toy_bubble.py
import logging
from helpers import dependency
from items.components.ny_constants import ToyTypes
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, INewYearCraftMachineController
_logger = logging.getLogger(__name__)

class MegaToyBubble(object):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)

    @classmethod
    def mustBeShown(cls, toyType, isSelected):
        return False if isSelected else cls.__canBeSelected(toyType, isSelected)

    @classmethod
    def mustBeShownByType(cls, megaToyType=None):
        toyTypes = ToyTypes.MEGA if megaToyType is None else (megaToyType,)
        slotsData = cls.__itemsCache.items.festivity.getSlots()
        for toyType in toyTypes:
            megaDecoration = first(cls.__nyController.getToysByType(toyType))
            isSelected = False
            if megaDecoration is not None:
                isSelected = megaDecoration.getID() in slotsData
            if cls.mustBeShown(toyType, isSelected):
                return True

        return False

    @classmethod
    def __canBeSelected(cls, toyType, isSelected):
        megaDecoration = first(cls.__nyController.getToysByType(toyType))
        hasDecoration = megaDecoration is not None and megaDecoration.getCount() > 0
        currentCount = cls.__itemsCache.items.festivity.getShardsCount()
        craftCost = cls.__craftCtrl.calculateMegaToyCraftCost()
        ableToCraft = currentCount >= craftCost
        return (hasDecoration or ableToCraft) and not isSelected
