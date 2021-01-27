# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/bob_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.BOBEventEntryPointMeta import BOBEventEntryPointMeta
from gui.impl.lobby.bob.bob_entry_point_view import BobEntryPointView

class BobEntryPoint(BOBEventEntryPointMeta):

    def _makeInjectView(self):
        self.__view = BobEntryPointView(ViewFlags.COMPONENT)
        return self.__view
