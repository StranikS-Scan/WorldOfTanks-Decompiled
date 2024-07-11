# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/shared/event.py
from gui.shared.event_bus import SharedEvent

class RacesEvent(SharedEvent):
    OPEN_RACES = 'openRaces'
    ON_RACE_FIRST_LIGHTS = 'onRaceFirstLights'
    ON_RACE_LAST_LIGHTS = 'onRaceLastLights'
    ON_OPEN_F1_HELP = 'onOpenF1Helper'
    ON_RACE_FINISHED = 'onRaceFinished'
