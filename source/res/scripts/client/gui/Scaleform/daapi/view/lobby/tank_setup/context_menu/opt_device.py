# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/opt_device.py
import typing
from adisp import adisp_process, adisp_async
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import option, CMLabel
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import TankSetupCMLabel
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base_equipment import BaseEquipmentItemContextMenu, BaseEquipmentSlotContextMenu, BaseHangarEquipmentSlotContextMenu
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IWotPlusController
if typing.TYPE_CHECKING:
    from gui.game_control.wot_plus_controller import WotPlusController

class OptDeviceItemContextMenu(BaseEquipmentItemContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentItemContextMenu._sqGen.currSequenceID)

    def _initFlashValues(self, ctx):
        super(OptDeviceItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _upgradeEquipment(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        if self._itemInstalledSetupSlotIdx != NONE_ID:
            vehicle = self._getCopyVehicle()
            setupIdx = self._itemInstalledSetupIdx
            slotIdx = self._itemInstalledSetupSlotIdx
        else:
            vehicle = None
            setupIdx = None
            slotIdx = None
        ActionsFactory.doAction(ActionsFactory.UPGRADE_OPT_DEVICE, module=item, vehicle=vehicle, setupIdx=setupIdx, slotIdx=slotIdx)
        return

    def _getVehicleItems(self):
        return self._getVehicle().optDevices


class OptDeviceSlotContextMenu(BaseEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentSlotContextMenu._sqGen.currSequenceID)
    _wotPlusController = dependency.descriptor(IWotPlusController)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT)
    def demount(self):
        self._sendSlotAction(BaseSetupModel.DEMOUNT_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT_FROM_SETUP)
    def demountFromSetup(self):
        self._sendSlotAction(BaseSetupModel.DEMOUNT_SLOT_FROM_SETUP_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT_FROM_SETUPS)
    def demountFromSetups(self):
        self._sendSlotAction(BaseSetupModel.DEMOUNT_SLOT_FROM_SETUPS_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.DESTROY)
    def destroy(self):
        self._sendSlotAction(BaseSetupModel.DESTROY_SLOT_ACTION)

    @option(_sqGen.next(), CMLabel.DECONSTRUCT)
    def deconstruct(self):
        self._sendSlotAction(BaseSetupModel.DECONSTRUCT_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOff(self):
        self._sendSlotAction(BaseSetupModel.REVERT_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        self._sendSlotAction(BaseSetupModel.REVERT_SLOT_ACTION)

    def _initFlashValues(self, ctx):
        super(OptDeviceSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    def _isVisible(self, label):
        if label == TankSetupCMLabel.DESTROY:
            return self._isMounted and not self._getItem().isModernized and not self._wotPlusController.isFreeToDemount(self._getItem())
        if label == CMLabel.DECONSTRUCT:
            return self._isMounted and self._getItem().isModernized
        if label == TankSetupCMLabel.DEMOUNT:
            return self._isMounted and not self._isMountedMoreThanOne
        if label == TankSetupCMLabel.DEMOUNT_FROM_SETUP or label == TankSetupCMLabel.DEMOUNT_FROM_SETUPS:
            return self._isMountedMoreThanOne
        if label == TankSetupCMLabel.UNLOAD:
            return not self._isMounted and self._isItemInInventory() and not self._isItemInOtherLayout()
        return not self._isMounted and self._isInstalledInCurrentLayout() and (not self._isItemInInventory() or self._isItemInOtherLayout()) if label == TankSetupCMLabel.TAKE_OFF else super(OptDeviceSlotContextMenu, self)._isVisible(label)

    def _upgradeEquipment(self):
        self._sendSlotAction(BaseSetupModel.UPGRADE_SLOT_ACTION)

    def _getVehicleItems(self):
        return self._getVehicle().optDevices


class HangarOptDeviceSlotContextMenu(BaseHangarEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseHangarEquipmentSlotContextMenu._sqGen.currSequenceID)
    _wotPlusController = dependency.descriptor(IWotPlusController)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT)
    def demount(self):
        self._demountProcess(isDestroy=False, everywhere=True)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT_FROM_SETUP)
    def demountFromSetup(self):
        self._demountProcess(isDestroy=False, everywhere=False)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT_FROM_SETUPS)
    def demountFromSetups(self):
        self._demountProcess(isDestroy=False, everywhere=True)

    @option(_sqGen.next(), TankSetupCMLabel.DESTROY)
    def destroy(self):
        self._demountProcess(isDestroy=True, everywhere=True)

    @option(_sqGen.next(), CMLabel.DECONSTRUCT)
    def deconstruct(self):
        self._deconstruct()

    @adisp_process
    def _deconstruct(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        action = ActionsFactory.getAction(ActionsFactory.DECONSTRUCT_OPT_DEVICE, item, self._getVehicle(), self._installedSlotId)
        result = yield ActionsFactory.asyncDoAction(action)
        if result:
            actionType = BaseSetupModel.DESTROY_SLOT_ACTION
            self._sendLastSlotAction(TankSetupConstants.OPT_DEVICES, actionType, {'intCD': item.intCD,
             'slotID': self._installedSlotId})

    def _initFlashValues(self, ctx):
        super(HangarOptDeviceSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().installed.getCapacity()

    @adisp_process
    def _demountProcess(self, isDestroy=False, everywhere=True):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        action = ActionsFactory.getAction(ActionsFactory.REMOVE_OPT_DEVICE, self._getVehicle(), item, self._installedSlotId, isDestroy, forFitting=False, everywhere=everywhere)
        result = yield ActionsFactory.asyncDoAction(action)
        if result:
            if isDestroy:
                actionType = BaseSetupModel.DESTROY_SLOT_ACTION
            elif everywhere:
                actionType = BaseSetupModel.DEMOUNT_SLOT_FROM_SETUPS_ACTION
            else:
                actionType = BaseSetupModel.DEMOUNT_SLOT_ACTION
            self._sendLastSlotAction(TankSetupConstants.OPT_DEVICES, actionType, {'intCD': item.intCD,
             'slotID': self._installedSlotId})

    def _putOnAction(self, onId):
        copyVehicle = self._getCopyVehicle()
        layout = copyVehicle.optDevices.layout
        self._makePutOnAction(TankSetupConstants.OPT_DEVICES, onId, copyVehicle, layout)

    @adisp_async
    @adisp_process
    def _doPutOnAction(self, vehicle, callback):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, vehicle, confirmOnlyExchange=True)
        result = yield ActionsFactory.asyncDoAction(action)
        callback(result)

    def _upgradeEquipment(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        ActionsFactory.doAction(ActionsFactory.UPGRADE_OPT_DEVICE, module=item, vehicle=self._getVehicle(), setupIdx=self._itemInstalledSetupIdx, slotIdx=self._installedSlotId)

    def _getVehicleItems(self):
        return self._getVehicle().optDevices

    def _isVisible(self, label):
        if label == TankSetupCMLabel.DEMOUNT:
            return self._isMounted and not self._isMountedMoreThanOne
        if label == TankSetupCMLabel.DEMOUNT_FROM_SETUP or label == TankSetupCMLabel.DEMOUNT_FROM_SETUPS:
            return self._isMountedMoreThanOne
        if label == TankSetupCMLabel.DESTROY:
            return self._isMounted and not self._getItem().isModernized and not self._wotPlusController.isFreeToDemount(self._getItem())
        return self._isMounted and self._getItem().isModernized if label == CMLabel.DECONSTRUCT else super(HangarOptDeviceSlotContextMenu, self)._isVisible(label)
