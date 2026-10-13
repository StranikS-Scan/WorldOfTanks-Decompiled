# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/user_missions/fort_rush_user_missions_presenter.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.presenters.fort_rush_progression_entry_point_presenter import FortRushProgressionEntryPointPresenter
from fort_rush.gui.impl.lobby.user_missions.fort_rush_quests_presenter import FortRushQuestsPresenter
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter

class FortRushUserMissionsPresenter(UserMissionsPresenter):
    _WIDGET_ALIAS = R.aliases.user_missions.hangarWidget
    _FORT_RUSH_ALIAS = R.aliases.fort_rush.shared
    _CHILDREN = {_WIDGET_ALIAS.Quests(): FortRushQuestsPresenter,
     _FORT_RUSH_ALIAS.Progression(): FortRushProgressionEntryPointPresenter}
