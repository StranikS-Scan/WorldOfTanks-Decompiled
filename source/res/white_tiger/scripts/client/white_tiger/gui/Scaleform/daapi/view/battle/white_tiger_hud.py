# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger_hud.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from white_tiger.gui.impl.battle.white_tiger_hud_view import WhiteTigerHudView

class WhiteTigerHud(InjectComponentAdaptor):

    def _makeInjectView(self):
        return WhiteTigerHudView()
