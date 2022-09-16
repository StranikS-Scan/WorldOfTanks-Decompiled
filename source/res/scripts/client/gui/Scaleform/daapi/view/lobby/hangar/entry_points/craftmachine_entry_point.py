# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/entry_points/craftmachine_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.CraftMachineEntryPointMeta import CraftMachineEntryPointMeta
from gui.impl.lobby.craft_machine.craftmachine_entry_point_view import CraftmachineEntryPointView

class CraftMachineEntryPoint(CraftMachineEntryPointMeta):

    def _makeInjectView(self):
        self.__view = CraftmachineEntryPointView(ViewFlags.COMPONENT)
        return self.__view
