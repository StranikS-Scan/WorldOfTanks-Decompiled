# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/platoon/HalloweenMemberView.py
from adisp import adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from helpers import i18n
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import PrebattleTypes

class HalloweenMemberView(SquadMembersView):
    _prebattleType = PrebattleTypes.HALLOWEEN

    @adisp_process
    def _onSwitchReady(self):
        result = yield self._platoonCtrl.togglePlayerReadyAction(checkAmmo=False)
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.halloween.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.halloween.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(False)
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setIcon(R.images.gui.maps.icons.battleTypes.c_40x40.eventSquad())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return BonusState.NO_BONUS

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.halloween()))))
        return title

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)
