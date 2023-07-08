# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/platoon/view/fun_platoon_members_view.py
import logging
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import PrebattleTypes
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
_logger = logging.getLogger(__name__)

class FunRandomMembersView(SquadMembersView, FunAssetPacksMixin, FunSubModesWatcher):
    _prebattleType = PrebattleTypes.FUNRANDOM

    def _getBonusState(self):
        return BonusState.NO_BONUS

    @hasDesiredSubMode(defReturn='')
    def _getTitle(self):
        subModeName = backport.text(self.getDesiredSubMode().getLocalsResRoot().userName())
        return backport.text(R.strings.fun_random.platoonView.title(), subModeName=subModeName)

    def _setBonusInformation(self, bonusState):
        self._currentBonusState = bonusState
        with self.viewModel.header.transaction() as model:
            model.setShowNoBonusPlaceholder(True)
            model.setShowInfoIcon(False)

    def _setHeaderBg(self, fileName, model):
        model.header.setBackgroundImage(backport.image(self.getModeIconsResRoot().platoon.dyn(fileName)()))

    def _onFindPlayers(self):
        pass

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _addListeners(self):
        super(FunRandomMembersView, self)._addListeners()
        self.startSubSelectionListening(self.__onSubModeSelected)

    def _removeListeners(self):
        self.stopSubSelectionListening(self.__onSubModeSelected)
        super(FunRandomMembersView, self)._removeListeners()

    def _updateFindPlayersButton(self, *args):
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(value=False)

    def __onSubModeSelected(self, *_):
        self.viewModel.setRawTitle(self._getTitle())
