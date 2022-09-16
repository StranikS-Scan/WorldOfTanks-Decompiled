# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/shell.py
from adisp import adisp_async, adisp_process
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import CMLabel, option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import TankSetupCMLabel, FIRST_SLOT, SECOND_SLOT, THIRD_SLOT, BaseTankSetupContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base_equipment import BaseHangarEquipmentSlotContextMenu
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from ids_generators import SequenceIDGenerator

class ShellItemContextMenu(BaseTankSetupContextMenu):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        self._sendSlotAction(BaseSetupModel.SHOW_INFO_SLOT_ACTION)

    @option(__sqGen.next(), TankSetupCMLabel.PUT_ON_FIRST)
    def putOnFirst(self):
        self._sendPutOnSlotAction(onId=FIRST_SLOT)

    @option(__sqGen.next(), TankSetupCMLabel.PUT_ON_SECOND)
    def putOnSecond(self):
        self._sendPutOnSlotAction(onId=SECOND_SLOT)

    @option(__sqGen.next(), TankSetupCMLabel.PUT_ON_THIRD)
    def putOnThird(self):
        self._sendPutOnSlotAction(onId=THIRD_SLOT)

    def _sendPutOnSlotAction(self, onId):
        view = self._getEmitterView()
        if view is None or self._slotType != view.getSelectedSetup():
            return
        else:
            view.sendSlotAction({'actionType': BaseSetupModel.SWAP_SLOTS_ACTION,
             'intCD': self._intCD,
             'leftID': min(onId, self._installedSlotId),
             'rightID': max(onId, self._installedSlotId)})
            return

    def _initFlashValues(self, ctx):
        super(ShellItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().getShellsCount()

    def _getVehicleItems(self):
        return self._getVehicle().shells


class HangarShellItemContextMenu(BaseHangarEquipmentSlotContextMenu):
    _sqGen = SequenceIDGenerator(BaseHangarEquipmentSlotContextMenu._sqGen.currSequenceID)

    def _initFlashValues(self, ctx):
        super(HangarShellItemContextMenu, self)._initFlashValues(ctx)
        self._slotsCount = self._getVehicleItems().getShellsCount()

    def _putOnAction(self, onId):
        copyVehicle = self._getCopyVehicle()
        layout = copyVehicle.shells.layout
        self._makePutOnAction(TankSetupConstants.SHELLS, onId, copyVehicle, layout)

    def _isVisible(self, label):
        return False if label == CMLabel.UPGRADE else super(HangarShellItemContextMenu, self)._isVisible(label)

    @adisp_async
    @adisp_process
    def _doPutOnAction(self, vehicle, callback):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_SHELLS, vehicle, confirmOnlyExchange=True)
        result = yield ActionsFactory.asyncDoAction(action)
        callback(result)

    def _getVehicleItems(self):
        return self._getVehicle().shells
