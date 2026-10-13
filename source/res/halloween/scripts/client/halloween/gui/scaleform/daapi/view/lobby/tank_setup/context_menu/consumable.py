# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/tank_setup/context_menu/consumable.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import consumableDecorator, HangarConsumableSlotContextMenu
from halloween.gui.shared.event_dispatcher import showModuleInfo
from ids_generators import SequenceIDGenerator

@consumableDecorator
class HWHangarConsumableSlotContextMenu(HangarConsumableSlotContextMenu):
    _sqGen = SequenceIDGenerator(HangarConsumableSlotContextMenu._sqGen.currSequenceID)

    def _showInfo(self):
        showModuleInfo(self._intCD, self._getVehicle().descriptor)
