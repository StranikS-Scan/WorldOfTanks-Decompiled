# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/user_missions_presenter.py
from frontline.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import FLOverlapCtrlMixin
from frontline.gui.impl.lobby.views.frontline_event_widget import FrontlineEventWidget
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter

class _BattlePassPresenter(BattlePassPresenter, FLOverlapCtrlMixin):
    pass


class FrontlineUserMissionsPresenter(UserMissionsPresenter):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.user_missions.hangarWidget.Events(): FrontlineEventWidget}
