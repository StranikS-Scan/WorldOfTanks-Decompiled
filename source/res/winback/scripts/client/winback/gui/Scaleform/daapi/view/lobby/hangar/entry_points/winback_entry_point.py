# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/daapi/view/lobby/hangar/entry_points/winback_entry_point.py
from frameworks.wulf import ViewFlags
from winback.gui.impl.lobby.views.winback_widget_view import WinbackWidgetView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class WinbackEntryPointWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = WinbackWidgetView(ViewFlags.VIEW)
        return self.__view
