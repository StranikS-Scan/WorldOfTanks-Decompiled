# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/user_missions/hangar_widget/overlap_ctrl.py
from battle_royale.gui.impl.lobby.views.states import BattleRoyaleHangarState
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin

class BattleRoyaleOverlapCtrlMixin(OverlapCtrlMixin):

    def _onVisibleRouteChanged(self, routeInfo):
        self._isInHangar = routeInfo.state == self._lobbyStateMachine.getStateByCls(BattleRoyaleHangarState)
        self._updateViewModelIfNeeded()
