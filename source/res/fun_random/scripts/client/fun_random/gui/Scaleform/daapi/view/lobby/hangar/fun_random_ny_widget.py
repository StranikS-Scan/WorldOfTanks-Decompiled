# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/fun_random_ny_widget.py
from fun_random.gui.impl.lobby.feature.fun_random_hangar_widget_view import FunRandomHangarWidgetView
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.FunRandomNYHangarWidgetMeta import FunRandomNYHangarWidgetMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import hasAliveInject
from frameworks.wulf import ViewStatus
from shared_utils import nextTick

class FunRandomNYHangarWidgetComponent(FunRandomNYHangarWidgetMeta):

    @nextTick
    @hasAliveInject()
    def updateLoaded(self):
        self.as_updateHitAreaS()

    def _addInjectContentListeners(self):
        self._injectView.onStatusChanged += self._onViewReady

    def _removeInjectContentListeners(self):
        self._injectView.onStatusChanged -= self._onViewReady

    def _makeInjectView(self):
        return FunRandomHangarWidgetView(R.views.fun_random.lobby.feature.FunRandomHangarNyWidgetView())

    def _onViewReady(self, state):
        if state == ViewStatus.LOADED:
            self.updateLoaded()
