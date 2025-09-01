# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/user_missions/hangar_widget/overlap_ctrl.py
from comp7_light.gui.impl.lobby.hangar.states import Comp7LightRootHangarState
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin

class Comp7LightOverlapCtrlMixin(OverlapCtrlMixin):

    def _onVisibleRouteChanged(self, routeInfo):
        self._isInHangar = routeInfo.state == self._lobbyStateMachine.getStateByCls(Comp7LightRootHangarState)
        self._updateViewModelIfNeeded()
