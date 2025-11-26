# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/user_missions/hangar_widget/presenters/user_missions_presenter.py
import typing
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.overlap_ctrl import BattleRoyaleOverlapCtrlMixin
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.presenters.event_shop_presenter import BattleRoyaleEventShopPresenter
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.presenters.progression_presenter import BattleRoyaleProgressionPresenter
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.presenters.quests_presenter import BattleRoayaleQuestsPresenter
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional

class _BattlePassPresenter(BattlePassPresenter, BattleRoyaleOverlapCtrlMixin):
    pass


class BattleRoyaleUserMissionsPresenter(UserMissionsPresenter):
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    _WIDGET_ALIAS = R.aliases.user_missions.hangarWidget
    _BATTLE_ROYALE_WIDGET_ALIAS = R.aliases.battle_royale.hangarWidget
    _CHILDREN = {_WIDGET_ALIAS.BattlePass(): _BattlePassPresenter,
     _WIDGET_ALIAS.Quests(): BattleRoayaleQuestsPresenter}

    def __init__(self):
        super(BattleRoyaleUserMissionsPresenter, self).__init__()
        self.__brQuestsPresenter = None
        return

    def _getChildComponents(self):
        return {self._BATTLE_ROYALE_WIDGET_ALIAS.Progression(): BattleRoyaleProgressionPresenter,
         self._BATTLE_ROYALE_WIDGET_ALIAS.EventShop(): BattleRoyaleEventShopPresenter}

    def _updateEntryPoints(self, vm):
        vm.setIsAnyEntryPointAvailable(True)

    def _updateMissions(self, vm):
        isVisible = self.__brProgression.isEnabled
        self._addChild(self._WIDGET_ALIAS.Quests(), isVisible)
        vm.setAreMissionsActive(isVisible)

    def _addChild(self, posId, isEnable):
        uid = self._childrenUidByPosition.get(posId)
        if self._childrenByUid.get(uid):
            return
        super(BattleRoyaleUserMissionsPresenter, self)._addChild(posId, isEnable)
