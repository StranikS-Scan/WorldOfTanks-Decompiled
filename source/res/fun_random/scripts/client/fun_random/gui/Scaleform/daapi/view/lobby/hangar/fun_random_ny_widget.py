# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/fun_random_ny_widget.py
from fun_random.gui.impl.lobby.feature.fun_random_hangar_widget_view import FunRandomHangarWidgetView
from gui.impl.gen import R
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class FunRandomNYHangarWidgetComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return FunRandomHangarWidgetView(R.views.fun_random.lobby.feature.FunRandomHangarNyWidgetView())
