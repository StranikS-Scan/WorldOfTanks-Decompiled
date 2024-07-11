# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/battle_helpers.py
import logging
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def getRemainingTime(sessionProvider=None):
    arenaPeriod = sessionProvider.shared.arenaPeriod
    endTime = arenaPeriod.getEndTime()
    arenaInfo = sessionProvider.arenaVisitor.getArenaInfo()
    if arenaInfo:
        arenaInfoRacesComponent = arenaInfo.dynamicComponents.get('arenaInfoRacesComponent', None)
        if arenaInfoRacesComponent and arenaInfoRacesComponent.raceEndTime:
            endTime = endTime - arenaPeriod.getLength() + arenaInfoRacesComponent.raceEndTime
    return max(0, endTime - BigWorld.serverTime())
