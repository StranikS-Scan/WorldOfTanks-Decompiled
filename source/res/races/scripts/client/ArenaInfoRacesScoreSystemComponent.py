# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/ArenaInfoRacesScoreSystemComponent.py
import BigWorld
import Event

class ArenaInfoRacesScoreSystemComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *args):
        self.onArenaScoreUpdated = Event.Event()

    def set_totalScore(self, *args, **kwargs):
        self.onArenaScoreUpdated(self.totalScore)
