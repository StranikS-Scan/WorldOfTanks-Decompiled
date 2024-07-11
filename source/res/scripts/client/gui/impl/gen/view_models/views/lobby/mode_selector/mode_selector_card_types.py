# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_card_types.py
from frameworks.wulf import ViewModel

class ModeSelectorCardTypes(ViewModel):
    __slots__ = ()
    DEFAULT = 0
    RANDOM = 1
    RANKED = 2
    MAPBOX = 3
    EPIC_BATTLE = 4
    BATTLE_ROYALE = 5
    FUN_RANDOM = 6
    COMP7 = 7
    VERSUS_AI = 8
    COSMIC = 9
    RACES = 10

    def __init__(self, properties=0, commands=0):
        super(ModeSelectorCardTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ModeSelectorCardTypes, self)._initialize()
