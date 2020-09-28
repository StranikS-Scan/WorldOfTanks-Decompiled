# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel_widget.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.battle.wt_event.players_panel_view import PlayersPanelView
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView

class PlayersPanelWidget(InjectComponentAdaptor, IAbstractPeriodView):

    def _makeInjectView(self):
        return PlayersPanelView()
