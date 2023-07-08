# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/fun_random_strengths_weaknesses_panel.py
from fun_random.gui.impl.lobby.feature.fun_random_strengths_weaknesses_panel import FunRandomStrengthsWeaknessesPanel
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class StrengthsWeaknessesPanelInject(InjectComponentAdaptor):
    __slots__ = ()

    def _makeInjectView(self, *args):
        return FunRandomStrengthsWeaknessesPanel()
