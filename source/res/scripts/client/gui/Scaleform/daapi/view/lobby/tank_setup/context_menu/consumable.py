# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/consumable.py
from adisp import adisp_process, adisp_async
from gui import shop
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import CMLabel, option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import TankSetupCMLabel
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base_equipment import BaseEquipmentItemContextMenu, BaseEquipmentSlotContextMenu, BaseHangarEquipmentSlotContextMenu
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from ids_generators import SequenceIDGenerator

def consumableDecorator(originalClass):
    originalMethod = originalClass._getOptionCustomData

    def _getOptionCustomData(self, label):
        optionData = originalMethod(self, label)
        consumable = self._itemsCache.items.getItemByCD(self._intCD)
        if label in (CMLabel.BUY_MORE, TankSetupCMLabel.UNLOAD, TankSetupCMLabel.TAKE_OFF):
            optionData.enabled = optionData.enabled and not consumable.isBuiltIn
        return optionData

    originalClass._getOptionCustomData = _getOptionCustomData
    return originalClass


@consumableDecorator
class ConsumableItemContextMenu(BaseEquipmentItemContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentItemContextMenu._sqGen.currSequenceID)

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buyMore(self):
        shop.showBuyEquipmentOverlay(itemId=self._intCD, source=shop.Source.EXTERNAL, origin=shop.Origin.CONSUMABLES, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)

    def _getCopyVehicle(self):
        copyVehicle = super(ConsumableItemContextMenu, self)._getCopyVehicle()
        copyVehicle.consumables.setInstalled(*self._getVehicleItems().layout)
        return copyVehicle

    def _getOptionCustomData(self, label):
        optionData = super(ConsumableItemContextMenu, self)._getOptionCustomData(label)
        for slotID, slotLabel in enumerate(TankSetupCMLabel.PUT_ON_LIST):
            if slotLabel == label:
                consumable = self._getVehicleItems().layout[slotID]
                optionData.enabled = optionData.enabled and (consumable is None or not consumable.isBuiltIn)
                break

        return optionData

    def _initFlashValues(self, ctx):
        super(ConsumableItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _getVehicleItems(self):
        return self._getVehicle().consumables


@consumableDecorator
class ConsumableSlotContextMenu(BaseEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentSlotContextMenu._sqGen.currSequenceID)

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buyMore(self):
        shop.showBuyEquipmentOverlay(itemId=self._intCD, source=shop.Source.EXTERNAL, origin=shop.Origin.CONSUMABLES, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        self._sendSlotAction(BaseSetupModel.SELECT_SLOT_ACTION, intCD=None, currentSlotId=self._installedSlotId)
        return

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOff(self):
        self._sendSlotAction(BaseSetupModel.REVERT_SLOT_ACTION)

    def _initFlashValues(self, ctx):
        super(ConsumableSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _getVehicleItems(self):
        return self._getVehicle().consumables


@consumableDecorator
class HangarConsumableSlotContextMenu(BaseHangarEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseHangarEquipmentSlotContextMenu._sqGen.currSequenceID)

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buyMore(self):
        shop.showBuyEquipmentOverlay(itemId=self._intCD, source=shop.Source.EXTERNAL, origin=shop.Origin.CONSUMABLES, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        self.__unloadAction()

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOffFromSlot(self):
        self.__unloadAction()

    def _initFlashValues(self, ctx):
        super(HangarConsumableSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _putOnAction(self, onId):
        copyVehicle = self._getCopyVehicle()
        copyVehicle.consumables.setLayout(*copyVehicle.consumables.installed)
        layout = copyVehicle.consumables.layout
        self._makePutOnAction(TankSetupConstants.CONSUMABLES, onId, copyVehicle, layout)

    @adisp_async
    @adisp_process
    def _doPutOnAction(self, vehicle, callback):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_CONSUMABLES, vehicle, confirmOnlyExchange=True)
        result = yield ActionsFactory.asyncDoAction(action)
        callback(result)

    def _getVehicleItems(self):
        return self._getVehicle().consumables

    @adisp_process
    def __unloadAction(self):
        copyVehicle = self._getCopyVehicle()
        copyVehicle.consumables.setLayout(*copyVehicle.consumables.installed)
        copyVehicle.consumables.layout[self._installedSlotId] = None
        result = yield self._doPutOnAction(copyVehicle)
        if result:
            self._sendLastSlotAction(TankSetupConstants.CONSUMABLES, BaseSetupModel.REVERT_SLOT_ACTION, {'slotID': self._installedSlotId})
        return
