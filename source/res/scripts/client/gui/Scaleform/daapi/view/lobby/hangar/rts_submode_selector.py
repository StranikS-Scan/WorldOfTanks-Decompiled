# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/rts_submode_selector.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.rts.rts_submode_selector_view import RTSSubModeSelectorView

class RTSSubModeSelector(InjectComponentAdaptor):

    def _makeInjectView(self):
        return RTSSubModeSelectorView()
