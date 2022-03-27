# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/rts_warning_widget.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.rts.warning_widget_view import WarningWidgetView

class RtsWarningWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return WarningWidgetView()
