# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions/hangar_widget/event_banners/comp7_ols_entry_point.py
from helpers import dependency
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.impl.lobby.user_missions.hangar_widget.event_banners.comp7_tournament_event_banner import Comp7TournamentEventBanner
from comp7.gui.shared import event_dispatcher as comp7_events
from helpers.ingame_tournament_helper import IngameTournamentType
from skeletons.gui.game_control import IComp7Controller

class Comp7OLSEntryPoint(Comp7TournamentEventBanner):
    NAME = COMP7_HANGAR_ALIASES.COMP7_OLS_ENTRY_POINT
    _TOURNAMENT_TYPE = IngameTournamentType.OLS
    _BORDER_COLOR = '#AECBF4'

    def onClick(self):
        comp7_events.showComp7OLSScreen()

    @classmethod
    @dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller)
    def isTournamentEntryPointAvailable(cls, comp7Ctrl=None):
        return super(Comp7OLSEntryPoint, cls).isTournamentEntryPointAvailable() and comp7Ctrl.isModePrbActive()
