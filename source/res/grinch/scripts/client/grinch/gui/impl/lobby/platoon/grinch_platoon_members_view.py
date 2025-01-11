# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/lobby/platoon/grinch_platoon_members_view.py
from enum import Enum
from grinch.gui.Scaleform.daapi.view.lobby.prb_windows.grinch_squad_action_button_statew_vo import GrinchSquadActionButtonStateVO
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from helpers import i18n

class _PrebattleTypes(Enum):
    GRINCH = 'grinch'


class GrinchMembersView(SquadMembersView):
    _prebattleType = _PrebattleTypes.GRINCH

    def _onLoading(self):
        super(GrinchMembersView, self)._onLoading()
        self.viewModel.setShouldShowFindPlayersButton(False)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.platoon.members.header.grinch()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.grinch.members.header.tooltip.header())
        tooltipBody = backport.text(R.strings.platoon.grinch.members.header.tooltip.body())
        return (tooltipHeader, tooltipBody)

    def _getActionButtonStateVO(self):
        return GrinchSquadActionButtonStateVO(self._platoonCtrl.getPrbEntity())
