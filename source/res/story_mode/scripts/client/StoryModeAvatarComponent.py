# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/StoryModeAvatarComponent.py
from Event import Event
from script_component.ScriptComponent import ScriptComponent

class StoryModeAvatarComponent(ScriptComponent):
    onSMAbilityWrongPoint = Event()
    onPositionValidChanged = Event()

    def set_wrongApplicationPoint(self, _):
        self.onSMAbilityWrongPoint(self.wrongApplicationPoint)

    def set_isPositionValid(self, prevValue):
        self.onPositionValidChanged()

    def setNavMeshGirth(self, girth):
        self.cell.setNavMeshGirth(girth)

    def checkPosition(self, position):
        self.cell.checkPosition(position)
