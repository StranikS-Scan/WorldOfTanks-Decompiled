# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_user_missions_presenter.py
from __future__ import absolute_import
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_progression_presenter import FunRandomProgressionPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_progression_quests_presenter import FunRandomProgressionQuestsPresenter
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter

class _BattlePassPresenter(BattlePassPresenter):
    pass


class _QuestsPresenter(QuestsPresenter):
    pass


class FunRandomUserMissionsPresenter(UserMissionsPresenter, FunProgressionWatcher):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.user_missions.hangarWidget.Quests(): _QuestsPresenter}

    def _getChildComponents(self):
        return {R.aliases.fun_random.shared.ProgressionEntryPoint(): FunRandomProgressionPresenter,
         R.aliases.fun_random.shared.ProgressionQuests(): FunRandomProgressionQuestsPresenter}
