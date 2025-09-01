# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/user_missions_presenter.py
from comp7_light.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7LightOverlapCtrlMixin
from comp7_light.gui.impl.lobby.entry_point_presenter import EntryPointPresenter
from comp7_light.gui.impl.lobby.progression_quests_presenter import ProgressionQuestsPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter

class _BattlePassPresenter(BattlePassPresenter, Comp7LightOverlapCtrlMixin):
    pass


class _QuestsPresenter(QuestsPresenter, Comp7LightOverlapCtrlMixin):
    pass


class Comp7LightUserMissionsPresenter(UserMissionsPresenter):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.user_missions.hangarWidget.Quests(): _QuestsPresenter}

    def _getChildComponents(self):
        return {R.aliases.comp7_light.shared.EntryPoint(): EntryPointPresenter,
         R.aliases.comp7_light.shared.Quests(): ProgressionQuestsPresenter}

    def _updateEntryPoints(self, vm):
        vm.setIsAnyEntryPointAvailable(True)
