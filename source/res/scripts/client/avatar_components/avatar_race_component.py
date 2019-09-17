# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_race_component.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from wotdecorators import condition, noexcept
from debug_utils import LOG_DEBUG_DEV
from Event import Event

class AvatarRaceComponent(object):
    ifEnabled = condition('isEnabledRace')

    def __init__(self):
        self.onCheckpointEvent = None
        self.onRepairNodePositionEvent = None
        self.onRepairCountersEvent = None
        self.onNewRacePosition = None
        self.isEnabledRace = False
        return

    def onBecomePlayer(self):
        self.onCheckpointEvent = Event()
        self.onRepairNodePositionEvent = Event()
        self.onRepairCountersEvent = Event()
        self.onNewRacePosition = Event()
        self.isEnabledRace = BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.FESTIVAL_RACE)
        return None if not self.isEnabledRace else None

    def onBecomeNonPlayer(self):
        if not self.isEnabledRace:
            return
        else:
            self.onCheckpointEvent = None
            self.onRepairNodePositionEvent = None
            self.onRepairCountersEvent = None
            self.onNewRacePosition = None
            self.isEnabledRace = False
            return

    @noexcept
    @ifEnabled
    def handleKey(self, isDown, key, mods):
        pass

    @noexcept
    @ifEnabled
    def onWrongWay(self):
        LOG_DEBUG_DEV('RACE: AvatarRaceComponent: onWrongWay')
