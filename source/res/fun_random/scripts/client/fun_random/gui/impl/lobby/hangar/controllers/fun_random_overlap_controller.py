# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/controllers/fun_random_overlap_controller.py
from __future__ import absolute_import
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from fun_random.gui.impl.lobby.hangar.states import DefaultFunRandomHangarState

class FunRandomOverlapCtrlMixin(OverlapCtrlMixin):

    def _onVisibleRouteChanged(self, routeInfo):
        defaultState = self._lobbyStateMachine.getStateByCls(DefaultFunRandomHangarState)
        self._isInHangar = routeInfo.state == defaultState
        self._updateViewModelIfNeeded()
