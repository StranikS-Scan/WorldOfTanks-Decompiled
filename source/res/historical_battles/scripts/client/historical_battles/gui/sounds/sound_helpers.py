# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_helpers.py
import typing
import BigWorld
from debug_utils import LOG_WARNING
if typing.TYPE_CHECKING:
    from ArenaPhasesComponent import ArenaPhasesComponent
    from typing import Optional

def getArenaPhasesComponent():
    arenaPhasesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('phasesComponent')
    if not arenaPhasesComponent:
        LOG_WARNING('ArenaPhasesComponent is missing')
        return None
    else:
        return arenaPhasesComponent
