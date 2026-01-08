# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/battle_modifiers_panel.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.hangar.battle_modifiers_panel_view import BattleModifiersPanelView

class BattleModifiersPanelInject(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(BattleModifiersPanelInject, self).__init__()
        self.__view = None
        return

    def _makeInjectView(self, *args):
        self.__view = BattleModifiersPanelView()
        return self.__view

    def _dispose(self):
        self.__view = None
        super(BattleModifiersPanelInject, self)._dispose()
        return
