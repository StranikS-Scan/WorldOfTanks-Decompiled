# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/fun_random_entry_point.py
from frameworks.wulf import ViewFlags
from fun_random.gui.impl.lobby.feature.fun_random_entry_point_view import FunRandomEntryPointView
from gui.Scaleform.daapi.view.meta.FunRandomEntryPointMeta import FunRandomEntryPointMeta

class FunRandomEntryPoint(FunRandomEntryPointMeta):

    def _makeInjectView(self):
        return FunRandomEntryPointView(ViewFlags.COMPONENT)
