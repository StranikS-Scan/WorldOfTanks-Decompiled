# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/battle_matters_entry_point.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.battle_matters.battle_matters_entry_point_view import BattleMattersEntryPointView
from shared_utils import nextTick

class BattleMattersEntryPoint(InjectComponentAdaptor):

    @nextTick
    def _createInjectView(self, *args):
        super(BattleMattersEntryPoint, self)._createInjectView(*args)

    def _makeInjectView(self):
        return BattleMattersEntryPointView()
