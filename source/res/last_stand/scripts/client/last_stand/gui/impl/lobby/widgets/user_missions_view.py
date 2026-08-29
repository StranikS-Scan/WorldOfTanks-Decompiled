# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/user_missions_view.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from last_stand.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.reward_path_presenter import RewardPathCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.shop_card_presenter import ShopCardPresenter
from last_stand.gui.impl.lobby.tooltips.battle_pass_in_progress_tooltip import LSBattlePassInProgressTooltipView
from last_stand.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import LastStandOverlapCtrlMixin
if typing.TYPE_CHECKING:
    from frameworks.wulf import View

class _BattlePassPresenter(BattlePassPresenter, LastStandOverlapCtrlMixin):
    _battlePassController = dependency.descriptor(IBattlePassController)

    @property
    def isPaused(self):
        return self.__battlePass.isPaused()

    def _createInProgressTooltipView(self):
        return LSBattlePassInProgressTooltipView()

    def isVisible(self):
        return not self._battlePassController.isDisabled()


class _QuestsCardPresenter(TooltipPositionerMixin, LastStandOverlapCtrlMixin, QuestsCardPresenter):

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(_QuestsCardPresenter, self)._onLoading(*args, **kwargs)

    def isVisible(self):
        return True


class LastStandUserMissionsPresenter(UserMissionsPresenter):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.last_stand.shared.Shop(): ShopCardPresenter,
     R.aliases.last_stand.shared.RewardPath(): RewardPathCardPresenter,
     R.aliases.last_stand.shared.Quests(): _QuestsCardPresenter}
