# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/gui_lootbox_integration/tooltip_handler.py
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import LootBoxTooltipBaseHandler

class NyDecorationTooltipHandler(LootBoxTooltipBaseHandler):

    def __call__(self, event):
        view = self.view
        return view(event.getArgument('toyID'))
