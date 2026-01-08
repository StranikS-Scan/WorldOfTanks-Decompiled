# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/user_missions/hangar_widget/event_banners/comp7_wci_entry_point.py
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.comp7_constants import FUNCTIONAL_FLAG
from comp7.gui.impl.lobby.user_missions.hangar_widget.event_banners.comp7_tournament_event_banner import Comp7TournamentEventBanner
from comp7.gui.shared import event_dispatcher as comp7_events
from helpers.ingame_tournament_helper import IngameTournamentType
from skeletons.gui.game_control import IComp7Controller

class Comp7WCIEntryPoint(Comp7TournamentEventBanner):
    NAME = COMP7_HANGAR_ALIASES.COMP7_WCI_ENTRY_POINT
    _TOURNAMENT_TYPE = IngameTournamentType.WCI

    def onClick(self):
        comp7_events.showComp7WCIScreen()

    @classmethod
    def isTournamentEntryPointAvailable(cls, comp7Ctrl=None):
        return super(Comp7WCIEntryPoint, cls).isTournamentEntryPointAvailable() and cls.__isRandomPrbActive()

    @classmethod
    def __isRandomPrbActive(cls):
        return bool(cls.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM) if cls.prbEntity is not None else False
