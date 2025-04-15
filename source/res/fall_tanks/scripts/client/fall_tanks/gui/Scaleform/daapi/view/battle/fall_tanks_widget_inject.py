# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/fall_tanks_widget_inject.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from fall_tanks.gui.impl.battle.battle_page.fall_tanks_battle_widget import FallTanksBattleWidgetView

class FallTanksBattleWidgetInject(InjectComponentAdaptor):

    def _makeInjectView(self, *args):
        return FallTanksBattleWidgetView()
