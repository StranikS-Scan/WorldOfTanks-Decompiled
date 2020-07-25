# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/opt_device.py
from adisp import process, async
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import TankSetupCMLabel
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base_equipment import BaseEquipmentItemContextMenu, BaseEquipmentSlotContextMenu, BaseHangarEquipmentSlotContextMenu
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from ids_generators import SequenceIDGenerator

class OptDeviceItemContextMenu(BaseEquipmentItemContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentItemContextMenu._sqGen.currSequenceID)

    def _initFlashValues(self, ctx):
        super(OptDeviceItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicle().optDevices.installed.getCapacity()

    def _upgradeEquipment(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        ActionsFactory.doAction(ActionsFactory.UPGRADE_OPT_DEVICE, module=item, vehicle=None, slotIdx=None)
        return


class OptDeviceSlotContextMenu(BaseEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseEquipmentSlotContextMenu._sqGen.currSequenceID)

    @option(_sqGen.next(), TankSetupCMLabel.DESTROY)
    def destroy(self):
        self._sendSlotAction(BaseSetupModel.DESTROY_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT)
    def demount(self):
        self._sendSlotAction(BaseSetupModel.DEMOUNT_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.TAKE_OFF)
    def takeOff(self):
        self._sendSlotAction(BaseSetupModel.REVERT_SLOT_ACTION)

    @option(_sqGen.next(), TankSetupCMLabel.UNLOAD)
    def unload(self):
        self._sendSlotAction(BaseSetupModel.REVERT_SLOT_ACTION)

    def _initFlashValues(self, ctx):
        super(OptDeviceSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicle().optDevices.installed.getCapacity()

    def _isVisible(self, label):
        if label == TankSetupCMLabel.DEMOUNT or label == TankSetupCMLabel.DESTROY:
            return self._isMounted
        if label == TankSetupCMLabel.UNLOAD:
            return not self._isMounted and self._isItemInInventory()
        return not self._isMounted and not self._isItemInInventory() if label == TankSetupCMLabel.TAKE_OFF else super(OptDeviceSlotContextMenu, self)._isVisible(label)

    def _upgradeEquipment(self):
        self._sendSlotAction(BaseSetupModel.UPGRADE_SLOT_ACTION)


class HangarOptDeviceSlotContextMenu(BaseHangarEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseHangarEquipmentSlotContextMenu._sqGen.currSequenceID)

    @option(_sqGen.next(), TankSetupCMLabel.DEMOUNT)
    def demount(self):
        self._demountProcess(isDestroy=False)

    @option(_sqGen.next(), TankSetupCMLabel.DESTROY)
    def destroy(self):
        self._demountProcess(isDestroy=True)

    def _initFlashValues(self, ctx):
        super(HangarOptDeviceSlotContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicle().optDevices.installed.getCapacity()

    @process
    def _demountProcess(self, isDestroy=False):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        action = ActionsFactory.getAction(ActionsFactory.REMOVE_OPT_DEVICE, self._getVehicle(), item, self._installedSlotId, isDestroy)
        result = yield ActionsFactory.asyncDoAction(action)
        if result:
            self._sendLastSlotAction(TankSetupConstants.OPT_DEVICES, BaseSetupModel.DESTROY_SLOT_ACTION if isDestroy else BaseSetupModel.DEMOUNT_SLOT_ACTION, {'intCD': item.intCD,
             'slotID': self._installedSlotId})

    def _putOnAction(self, onId):
        copyVehicle = self._getCopyVehicle()
        layout = copyVehicle.optDevices.layout
        self._makePutOnAction(TankSetupConstants.OPT_DEVICES, onId, copyVehicle, layout)

    @async
    @process
    def _doPutOnAction(self, vehicle, callback):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, vehicle, confirmOnlyExchange=True)
        result = yield ActionsFactory.asyncDoAction(action)
        callback(result)

    def _upgradeEquipment(self):
        item = self._itemsCache.items.getItemByCD(self._intCD)
        ActionsFactory.doAction(ActionsFactory.UPGRADE_OPT_DEVICE, module=item, vehicle=self._getVehicle(), slotIdx=self._installedSlotId, blurd3D=True)
