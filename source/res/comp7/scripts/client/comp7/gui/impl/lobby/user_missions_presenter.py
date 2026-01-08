# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions_presenter.py
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.impl.lobby.entry_point_presenter import EntryPointPresenter
from comp7.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import Comp7OverlapCtrlMixin
from comp7.gui.impl.lobby.weekly_quests_widget_presenter import WeeklyQuestsWidgetPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.event_banners_presenter import EventBannersPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter

class _BattlePassPresenter(BattlePassPresenter, Comp7OverlapCtrlMixin):
    pass


class _QuestsPresenter(QuestsPresenter, Comp7OverlapCtrlMixin):
    pass


class _EventBannersPresenter(EventBannersPresenter, Comp7OverlapCtrlMixin):
    __ALLOWED_EVENT_IDS = (COMP7_HANGAR_ALIASES.COMP7_OLS_ENTRY_POINT,)

    def _getEventEntries(self):
        allEventEntries = super(_EventBannersPresenter, self)._getEventEntries()
        return [ event for event in allEventEntries if event.id in self.__ALLOWED_EVENT_IDS ]


class Comp7UserMissionsPresenter(UserMissionsPresenter):
    _CHILDREN = {R.aliases.user_missions.hangarWidget.BattlePass(): _BattlePassPresenter,
     R.aliases.user_missions.hangarWidget.Events(): _EventBannersPresenter,
     R.aliases.user_missions.hangarWidget.Quests(): _QuestsPresenter}

    def _getChildComponents(self):
        return {R.aliases.comp7.shared.EntryPoint(): EntryPointPresenter,
         R.aliases.comp7.shared.WeeklyQuestsWidget(): WeeklyQuestsWidgetPresenter}
