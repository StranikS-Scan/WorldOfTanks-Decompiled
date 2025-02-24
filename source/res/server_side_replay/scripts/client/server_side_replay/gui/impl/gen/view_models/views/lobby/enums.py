# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/gen/view_models/views/lobby/enums.py
from enum import Enum, IntEnum

class ReplaysViews(IntEnum):
    BESTREPLAYS = 0
    MYREPLAYS = 1
    FINDREPLAY = 2


class TankmanLocation(Enum):
    INBARRACKS = 'in_barracks'
    INTANK = 'in_tank'
    DISMISSED = 'dismissed'
