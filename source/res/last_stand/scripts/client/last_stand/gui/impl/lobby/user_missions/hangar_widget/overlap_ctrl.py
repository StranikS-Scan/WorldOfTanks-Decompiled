# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/user_missions/hangar_widget/overlap_ctrl.py
from __future__ import absolute_import
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from last_stand.gui.impl.lobby.states import LastStandRootHangarState

class LastStandOverlapCtrlMixin(OverlapCtrlMixin):

    def _onVisibleRouteChanged(self, routeInfo):
        self._isInHangar = routeInfo.state == self._lobbyStateMachine.getStateByCls(LastStandRootHangarState)
        self._updateViewModelIfNeeded()
