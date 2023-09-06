# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/impl/lobby/versus_ai_platoon_members_view.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import PrebattleTypes
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from helpers import i18n

class VersusAIMembersView(SquadMembersView):
    _prebattleType = PrebattleTypes.EVENT

    def __init__(self, prbType):
        super(VersusAIMembersView, self).__init__(prbType)
        self.viewModel.setShouldShowFindPlayersButton(False)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.versusAI_platoon.members.header.versusAI()))))
        return title
