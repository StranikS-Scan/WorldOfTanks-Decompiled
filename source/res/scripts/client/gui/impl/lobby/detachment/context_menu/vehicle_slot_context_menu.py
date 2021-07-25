# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/context_menu/vehicle_slot_context_menu.py
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import option
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showDetachmentViewById, showVehicleInfo
from gui import SystemMessages
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.shared.gui_items.processors.detachment import DetachmentSwapVehicleSlots
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import decorators
from items.components.detachment_constants import DetachmentSlotType
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
from shared_utils import CONST_CONTAINER
from ids_generators import SequenceIDGenerator

class MenuItems(CONST_CONTAINER):
    RETRAINING = 'retraining'
    VEHICLE_INFO = 'vehicleInfo'
    ADD_TO_COMPARISON = 'addToComparison'
    MOVE_TO_SLOT_0 = 'moveToFirst'
    MOVE_TO_SLOT_1 = 'moveToSecond'
    MOVE_TO_SLOT_2 = 'moveToThird'
    GO_TO_HANGAR = 'goToHangar'


def menuHandler(name):
    return '_' + name


class VehicleSlotContextMenu(AbstractContextMenuHandler):
    __sqGen = SequenceIDGenerator()
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cmProxy, ctx=None):
        super(VehicleSlotContextMenu, self).__init__(cmProxy, ctx, {mi:menuHandler(mi) for mi in MenuItems.ALL()})

    @option(__sqGen.next(), MenuItems.RETRAINING)
    def _retraining(self):
        if self._currentSlotVehType:
            showDetachmentViewById(NavigationViewModel.VEHICLE_LIST, {'detInvID': self._detInvID,
             'vehicleSlotIndex': int(self._currentSlotIndex)})

    @option(__sqGen.next(), MenuItems.VEHICLE_INFO)
    def _vehicleInfo(self):
        showVehicleInfo(self._currentSlotVehType)

    @option(__sqGen.next(), MenuItems.ADD_TO_COMPARISON)
    def _addToComparison(self):
        basket = self.__comparisonBasket
        if not basket.isLocked:
            basket.addVehicle(self._currentSlotVehType)

    @option(__sqGen.next(), MenuItems.MOVE_TO_SLOT_0)
    def _moveToFirst(self):
        self.__moveVehicleToSlot(0)

    @option(__sqGen.next(), MenuItems.MOVE_TO_SLOT_1)
    def _moveToSecond(self):
        self.__moveVehicleToSlot(1)

    @option(__sqGen.next(), MenuItems.MOVE_TO_SLOT_2)
    def _moveToThird(self):
        self.__moveVehicleToSlot(2)

    @option(__sqGen.next(), MenuItems.GO_TO_HANGAR)
    def _goToHangar(self):
        event_dispatcher.selectVehicleInHangar(self._currentSlotVehType)

    def _initFlashValues(self, ctx):
        self._currentSlotIndex = int(ctx.slotIndex)
        self._detInvID = int(ctx.detInvID)
        detachment = self.__getDetachment()
        self._detachment = detachment
        self._slotsInfo = detachment.getDescriptor().getAllSlotsInfo(DetachmentSlotType.VEHICLES)
        currentSlotVehType = self._slotsInfo[self._currentSlotIndex].typeCompDescr
        self._currentSlotVehType = currentSlotVehType
        vehGuiItem = self.__itemsCache.items.getItemByCD(currentSlotVehType) if currentSlotVehType else None
        self._vehGuiItem = vehGuiItem
        self._canCompare = self.__comparisonBasket.isReadyToAdd(vehGuiItem)
        return

    def _generateOptions(self, ctx=None):
        options = []
        currentSlotInfo = self._slotsInfo[self._currentSlotIndex]
        if not currentSlotInfo.available:
            return options
        else:
            currentSlotEmpty = currentSlotInfo.typeCompDescr is None
            canOperateSlot = not (currentSlotEmpty or currentSlotInfo.locked)
            label = backport.text(R.strings.menu.contextMenu.detachment.vehicleSlot.retraning())
            options.append(self._makeItem(MenuItems.RETRAINING, label, {'enabled': canOperateSlot}))
            label = backport.text(R.strings.menu.contextMenu.detachment.vehicleSlot.info())
            options.append(self._makeItem(MenuItems.VEHICLE_INFO, label, {'enabled': not currentSlotEmpty}))
            label = backport.text(R.strings.menu.contextMenu.detachment.vehicleSlot.addToCompare())
            options.append(self._makeItem(MenuItems.ADD_TO_COMPARISON, label, {'enabled': self._canCompare}))
            for i, slotInfo in enumerate(self._slotsInfo):
                if self._currentSlotIndex == i:
                    continue
                menuItem = self.__generateMoveSlotItemOption(i, slotInfo.available, slotInfo.locked or currentSlotEmpty)
                if menuItem:
                    options.append(menuItem)

            label = backport.text(R.strings.menu.contextMenu.selectVehicleInHangar())
            options.append(self._makeItem(MenuItems.GO_TO_HANGAR, label, {'enabled': self._vehGuiItem and self._vehGuiItem.isInInventory}))
            return options

    def __getDetachment(self):
        return self.__detachmentCache.getDetachment(self._detInvID)

    def __generateMoveSlotItemOption(self, slotIndex, available, locked):
        handler = getattr(MenuItems, 'MOVE_TO_SLOT_{}'.format(slotIndex), None)
        if handler is not None:
            label = backport.text(R.strings.menu.contextMenu.detachment.vehicleSlot.moveToSlot(), number=slotIndex + 1)
            return self._makeItem(handler, label, {'enabled': available and not locked})
        else:
            return

    @decorators.process('updating')
    def __moveVehicleToSlot(self, slotID):
        processor = DetachmentSwapVehicleSlots(self._detInvID, slot1Index=self._currentSlotIndex, slot2Index=slotID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
