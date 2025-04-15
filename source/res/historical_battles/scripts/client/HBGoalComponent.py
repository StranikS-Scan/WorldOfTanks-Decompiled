# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBGoalComponent.py
import logging
import BigWorld
import Event
log = logging.getLogger(__name__)

class HBGoalComponent(BigWorld.DynamicScriptComponent):
    onGoalsUpdated = Event.Event()

    def __init__(self):
        self.onGoalsUpdated(self.goalsInfo)

    def set_goalsInfo(self, prev):
        self.onGoalsUpdated(self.goalsInfo)
