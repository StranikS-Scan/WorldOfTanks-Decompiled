# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/user_missions/fort_rush_overlap_ctrl.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.states import FortRushRootHangarState
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin

class FortRushOverlapCtrlMixin(OverlapCtrlMixin):

    def _onVisibleRouteChanged(self, routeInfo):
        self._isInHangar = routeInfo.state == self._lobbyStateMachine.getStateByCls(FortRushRootHangarState)
        self._updateViewModelIfNeeded()
