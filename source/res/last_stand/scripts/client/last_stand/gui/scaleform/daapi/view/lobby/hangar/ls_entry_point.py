# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/hangar/ls_entry_point.py
from frameworks.wulf import ViewFlags
from last_stand.gui.impl.lobby.feature.ls_entry_point_view import LSEntryPointView
from last_stand.gui.scaleform.daapi.view.meta.LSEntryPointMeta import LSEntryPointMeta

class LSEntryPoint(LSEntryPointMeta):

    def _makeInjectView(self):
        return LSEntryPointView(ViewFlags.VIEW)
