# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/entry_points/fun_random_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.FunRandomEntryPointMeta import FunRandomEntryPointMeta
from gui.impl.lobby.fun_random.fun_random_entry_point_view import FunRandomEntryPointView

class FunRandomEntryPoint(FunRandomEntryPointMeta):

    def _makeInjectView(self):
        return FunRandomEntryPointView(ViewFlags.COMPONENT)
