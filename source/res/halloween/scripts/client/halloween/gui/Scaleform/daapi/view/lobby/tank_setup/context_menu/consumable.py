# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/consumable.py
import BigWorld
from adisp import adisp_process, adisp_async
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import CMLabel, option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import TankSetupCMLabel
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import consumableDecorator, ConsumableItemContextMenu, ConsumableSlotContextMenu, HangarConsumableSlotContextMenu
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.halloween import HWBuyAndInstallConsumables
from ids_generators import SequenceIDGenerator
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_cm_handlers import EquipmentCMHandler
from items import vehicles

@consumableDecorator
class HWConsumableItemContextMenu(ConsumableItemContextMenu):
    _sqGen = SequenceIDGenerator(ConsumableItemContextMenu._sqGen.currSequenceID)

    def showInfo(self):
        pass

    @property
    def hwEqCtrl(self):
        return BigWorld.player().HWAccountEquipmentController

    def _getVehicleItems(self):
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(self._getVehicle())
        return hwVehicle.hwConsumables

    def _initFlashValues(self, ctx):
        super(HWConsumableItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _getOptionCustomData(self, label):
        optionData = super(HWConsumableItemContextMenu, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.visible = False
        return optionData


@consumableDecorator
class HWConsumableSlotContextMenu(ConsumableSlotContextMenu):
    _sqGen = SequenceIDGenerator(ConsumableSlotContextMenu._sqGen.currSequenceID)

    @property
    def hwEqCtrl(self):
        return BigWorld.player().HWAccountEquipmentController

    def showInfo(self):
        pass

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        super(HWConsumableSlotContextMenu, self).unload()

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOff(self):
        super(HWConsumableSlotContextMenu, self).takeOff()

    def _getVehicleItems(self):
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(self._getVehicle())
        return hwVehicle.hwConsumables

    def _getOptionCustomData(self, label):
        optionData = super(HWConsumableSlotContextMenu, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.visible = False
        return optionData

    def _initFlashValues(self, ctx):
        super(HWConsumableSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()


@consumableDecorator
class HangarHWConsumableSlotContextMenu(HangarConsumableSlotContextMenu):
    _sqGen = SequenceIDGenerator(HangarConsumableSlotContextMenu._sqGen.currSequenceID)

    @property
    def hwEqCtrl(self):
        return BigWorld.player().HWAccountEquipmentController

    def showInfo(self):
        pass

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        self.__unloadAction()

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOffFromSlot(self):
        self.__unloadAction()

    def _getVehicleItems(self):
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(self._getVehicle())
        return hwVehicle.hwConsumables

    def _getOptionCustomData(self, label):
        optionData = super(HangarHWConsumableSlotContextMenu, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.visible = False
        return optionData

    def _initFlashValues(self, ctx):
        super(HangarHWConsumableSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _putOnAction(self, onId):
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(self._getCopyVehicle())
        hwVehicle.hwConsumables.layout = hwVehicle.hwConsumables.installed
        layout = hwVehicle.hwConsumables.layout
        self._makePutOnAction(TankSetupConstants.HWCONSUMABLES, onId, hwVehicle, layout)

    @adisp_async
    @adisp_process
    def _doPutOnAction(self, vehicle, callback, skipDialog=False):
        action = HWBuyAndInstallConsumables(vehicle, confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @adisp_process
    def __unloadAction(self):
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(self._getCopyVehicle())
        hwVehicle.hwConsumables.layout = hwVehicle.hwConsumables.installed
        hwVehicle.hwConsumables.layout[self._installedSlotId] = None
        result = yield self._doPutOnAction(hwVehicle)
        if result:
            self._sendLastSlotAction(TankSetupConstants.HWCONSUMABLES, BaseSetupModel.REVERT_SLOT_ACTION, {'slotID': self._installedSlotId})
        return


class HWEquipmentCMHandler(EquipmentCMHandler):

    def _getOptionCustomData(self, label):
        optionData = super(HWEquipmentCMHandler, self)._getOptionCustomData(label)
        item = vehicles.getItemByCompactDescr(self._id)
        isHalloween = 'halloween_equipment' in item.tags
        if isHalloween and label in (CMLabel.BUY_MORE, CMLabel.SELL):
            optionData.visible = False
        return optionData
