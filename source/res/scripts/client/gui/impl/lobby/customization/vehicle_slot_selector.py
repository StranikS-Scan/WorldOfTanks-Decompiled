# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/vehicle_slot_selector.py
import logging
from typing import TYPE_CHECKING
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.customization import ICustomizationService
if TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.customization.context.context import CustomizationContext
    from gui.customization.shared import C11nId
_logger = logging.getLogger(__name__)

class VehicleSlotSelector(object):
    __service = dependency.descriptor(ICustomizationService)
    __CLICKS_TO_SELECT_SLOT = 2

    def __init__(self):
        self.__ctx = self.__service.getCtx()
        self.__selectionCount = 0
        self.__selectedSlot = None
        return

    @property
    def selectedSlot(self):
        return self.__selectedSlot

    @property
    def attached(self):
        return self.__selectedSlot is not None

    def selectItem(self, intCD):
        self.__selectionCount = 0
        self.__selectedSlot = None
        return

    def unselectItem(self):
        self.__selectionCount = 0
        self.__selectedSlot = None
        return

    @nextTick
    def selectSlot(self, slotId):
        if self.__ctx.mode.selectedItem is not None:
            if self.__selectedSlot == slotId:
                self.__selectionCount += 1
            else:
                self.__selectionCount = 1
        self.__selectedSlot = slotId
        if self.__selectionCount == self.__CLICKS_TO_SELECT_SLOT:
            self.__ctx.mode.unselectItem()
        self.__ctx.mode.selectSlot(slotId)
        return

    def unselectSlot(self):
        self.__selectedSlot = None
        return
