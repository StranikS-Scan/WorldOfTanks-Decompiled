# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_craft_states.py
from frameworks.wulf import ViewModel

class NewYearCraftStates(ViewModel):
    __slots__ = ()
    CRAFT_REGULAR = 0
    CRAFT_MEGA = 1
    CRAFT_REGULAR_WITH_FILLER = 2

    def __init__(self, properties=0, commands=0):
        super(NewYearCraftStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NewYearCraftStates, self)._initialize()
