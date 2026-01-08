# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/battle_modifiers_panel_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Queue(IntEnum):
    STRONGHOLD = 0
    GLOBALMAP = 1


class BattleModifiersPanelViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattleModifiersPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getQueue(self):
        return Queue(self._getNumber(0))

    def setQueue(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(BattleModifiersPanelViewModel, self)._initialize()
        self._addNumberProperty('queue')
