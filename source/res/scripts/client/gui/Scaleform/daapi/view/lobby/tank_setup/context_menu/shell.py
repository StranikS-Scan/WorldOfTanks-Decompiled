# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/shell.py
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import CMLabel, option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import BaseItemContextMenu, TankSetupCMLabel, FIRST_SLOT, SECOND_SLOT, THIRD_SLOT
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from ids_generators import SequenceIDGenerator

class ShellItemContextMenu(BaseItemContextMenu):
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
        self._slotsCount = self._getVehicle().shells.getShellsCount()
