# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/context_menu/veh_module.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import CMLabel, option
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.base import BaseItemContextMenu, TankSetupCMLabel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from ids_generators import SequenceIDGenerator

class VehModuleItemContextMenu(BaseItemContextMenu):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.nextSequenceID, CMLabel.INFORMATION)
    def showInfo(self):
        self._sendSlotAction(BaseSetupModel.SHOW_INFO_SLOT_ACTION)

    @option(__sqGen.nextSequenceID, TankSetupCMLabel.SELECT)
    def select(self):
        self._sendSlotAction(BaseSetupModel.SELECT_SLOT_ACTION)
