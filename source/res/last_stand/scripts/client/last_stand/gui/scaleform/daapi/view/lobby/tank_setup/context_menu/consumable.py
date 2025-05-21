# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/tank_setup/context_menu/consumable.py
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import consumableDecorator, HangarConsumableSlotContextMenu
from last_stand.gui.shared.event_dispatcher import showModuleInfo
from ids_generators import SequenceIDGenerator
from LSAccountEquipmentController import getLSConsumables
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from last_stand.gui.impl.lobby.tank_setup.interactor import ActionTypes
from adisp import adisp_process, adisp_async

@consumableDecorator
class LSHangarConsumableSlotContextMenu(HangarConsumableSlotContextMenu):
    _sqGen = SequenceIDGenerator(HangarConsumableSlotContextMenu._sqGen.currSequenceID)

    def _putOnAction(self, onId):
        copyVehicle = self._getCopyVehicle()
        extConsumables = getLSConsumables(copyVehicle)
        extConsumables.layout = extConsumables.installed.copy()
        layout = extConsumables.layout
        self._makePutOnAction(LSTankSetupConstants.LS_CONSUMABLES, onId, copyVehicle, layout)

    @adisp_async
    @adisp_process
    def _doPutOnAction(self, vehicle, callback):
        actionName = ActionTypes.BUY_AND_INSTALL_LS_CONSUMABLES_ACTION
        action = ActionsFactory.getAction(actionName, vehicle, confirmOnlyExchange=True)
        result = yield ActionsFactory.asyncDoAction(action)
        callback(result)

    def _getVehicleItems(self):
        return self._getVehicle().consumables

    @adisp_process
    def _unloadAction(self):
        copyVehicle = self._getCopyVehicle()
        extConsumables = getLSConsumables(copyVehicle)
        extConsumables.layout = extConsumables.installed.copy()
        extConsumables.layout[self._installedSlotId] = None
        result = yield self._doPutOnAction(copyVehicle)
        if result:
            self._sendLastSlotAction(LSTankSetupConstants.LS_CONSUMABLES, BaseSetupModel.REVERT_SLOT_ACTION, {'slotID': self._installedSlotId})
        return

    def _showInfo(self):
        showModuleInfo(self._intCD, self._getVehicle().descriptor)
