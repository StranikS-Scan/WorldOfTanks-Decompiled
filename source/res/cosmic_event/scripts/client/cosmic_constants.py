# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_constants.py
from enum import Enum
COSMIC_BANNER_ENTRY_POINT = 'CosmicBannerEntryPoint'

class EVENT_STATES(Enum):
    START = 0
    FINISH = 1
    SUSPEND = 2
    RESUME = 3
