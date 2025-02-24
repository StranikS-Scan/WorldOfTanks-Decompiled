# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
from comp7.gui.Scaleform.daapi.view.battle.shared.premature_leave import showComp7LeaverAliveWindow
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu

class Comp7IngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showComp7LeaverAliveWindow()
