# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/ArenaInfoScoreSystemComponent.py
import BigWorld
import Event

class ArenaInfoScoreSystemComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *args):
        self.onArenaScoreUpdated = Event.Event()

    def set_totalScore(self, *args, **kwargs):
        self.onArenaScoreUpdated(self.totalScore)
