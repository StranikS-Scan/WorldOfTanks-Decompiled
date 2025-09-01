# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/arena_gui_types_constants.py
from frameworks.wulf import ViewModel

class ArenaGuiTypesConstants(ViewModel):
    __slots__ = ()
    UNKNOWN = 0
    RANDOM = 1
    TRAINING = 2
    CYBERSPORT = 5
    FALLOUT = 6
    EVENT_BATTLES = 7
    FALLOUT_CLASSIC = 13
    FALLOUT_MULTITEAM = 14
    SORTIE_2 = 15
    FORT_BATTLE_2 = 16
    RANKED = 17
    EPIC_RANDOM = 19
    EPIC_RANDOM_TRAINING = 20
    EPIC_BATTLE = 21
    EPIC_TRAINING = 22
    BATTLE_ROYALE = 23
    MAPBOX = 24
    MAPS_TRAINING = 25
    RTS = 26
    RTS_TRAINING = 27
    RTS_BOOTCAMP = 28
    WINBACK = 31
    STORY_MODE_ONBOARDING = 100
    STORY_MODE_REGULAR = 104

    def __init__(self, properties=0, commands=0):
        super(ArenaGuiTypesConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ArenaGuiTypesConstants, self)._initialize()
