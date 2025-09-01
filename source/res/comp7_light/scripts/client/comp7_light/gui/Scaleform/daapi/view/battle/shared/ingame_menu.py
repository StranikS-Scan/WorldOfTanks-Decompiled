# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
from comp7_light.gui.Scaleform.daapi.view.battle.shared.premature_leave import showComp7LightLeaverAliveWindow
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu

class Comp7LightIngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showComp7LightLeaverAliveWindow()
