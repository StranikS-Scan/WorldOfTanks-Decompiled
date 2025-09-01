# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions_presenter.py
from comp7.gui.impl.lobby.entry_point_presenter import EntryPointPresenter
from comp7.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7OverlapCtrlMixin
from comp7.gui.impl.lobby.weekly_quests_widget_presenter import WeeklyQuestsWidgetPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter

class _BattlePassPresenter(BattlePassPresenter, Comp7OverlapCtrlMixin):
    pass


class _QuestsPresenter(QuestsPresenter, Comp7OverlapCtrlMixin):
    pass


class Comp7UserMissionsPresenter(UserMissionsPresenter):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.user_missions.hangarWidget.Quests(): _QuestsPresenter}

    def _getChildComponents(self):
        return {R.aliases.comp7.shared.EntryPoint(): EntryPointPresenter,
         R.aliases.comp7.shared.WeeklyQuestsWidget(): WeeklyQuestsWidgetPresenter}

    def _updateEntryPoints(self, vm):
        vm.setIsAnyEntryPointAvailable(True)
