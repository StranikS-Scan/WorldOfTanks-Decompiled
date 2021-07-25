# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/adaptors/hangar_widget_adaptor.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.detachment.hangar_widget import HangarWidget

class HangarWidgetAdaptor(InjectComponentAdaptor):
    __slots__ = ()

    def _makeInjectView(self):
        return HangarWidget()

    def handleEscape(self):
        self.injectedView.handleEscape()
