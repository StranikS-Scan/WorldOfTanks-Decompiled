# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/fest_race_ingame_menu.py
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import event_dispatcher as battle_event_dispatcher

class FestRaceIngameMenu(IngameMenu):

    def helpClick(self):
        self.destroy()
        battle_event_dispatcher.showEventHelp(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_MENU)
