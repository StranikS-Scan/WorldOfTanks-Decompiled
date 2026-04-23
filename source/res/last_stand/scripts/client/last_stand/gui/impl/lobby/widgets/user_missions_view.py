# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/user_missions_view.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService
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

    @property
    def isPaused(self):
        return self.__battlePass.isPaused()

    def _createInProgressTooltipView(self):
        return LSBattlePassInProgressTooltipView()


class _QuestsCardPresenter(TooltipPositionerMixin, LastStandOverlapCtrlMixin, QuestsCardPresenter):

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(_QuestsCardPresenter, self)._onLoading(*args, **kwargs)


class LastStandUserMissionsPresenter(UserMissionsPresenter):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __battlePassService = dependency.descriptor(IBattlePassService)
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.last_stand.shared.Shop(): ShopCardPresenter,
     R.aliases.last_stand.shared.RewardPath(): RewardPathCardPresenter,
     R.aliases.last_stand.shared.Quests(): _QuestsCardPresenter}

    def _getChildComponents(self):
        return self._CHILDREN

    def _getEvents(self):
        baseEvents = self._getBaseEvents()
        return baseEvents + ((self.__battlePassService.onBattlePassChanged, self._onBattlePassEvent), (self.viewModel.onPresenterDisappear, self._onPresenterDisappear), (self.viewModel.onWidgetUnmounted, self._onWidgetUnmounted))

    def _updateEntryPoints(self, vm):
        pass

    def _updateBattlePass(self, vm):
        isAvailable = not self.__battlePassController.isDisabled()
        self._addChild(self._WIDGET_ALIAS.BattlePass(), isAvailable)
        vm.setIsBattlePassActive(isAvailable)
