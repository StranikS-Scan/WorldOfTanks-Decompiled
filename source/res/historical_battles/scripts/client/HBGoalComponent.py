# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBGoalComponent.py
import logging
from script_component.DynamicScriptComponent import DynamicScriptComponent
import Event
log = logging.getLogger(__name__)

class HBGoalComponent(DynamicScriptComponent):
    onGoalsUpdated = Event.Event()

    def __init__(self):
        super(HBGoalComponent, self).__init__()
        self.onGoalsUpdated(self.goalsInfo)

    def set_goalsInfo(self, prev):
        self.onGoalsUpdated(self.goalsInfo)

    def _onAvatarReady(self):
        self.onGoalsUpdated(self.goalsInfo)
