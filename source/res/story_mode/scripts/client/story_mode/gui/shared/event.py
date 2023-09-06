# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/event.py
from gui.shared.event_bus import SharedEvent

class StoryModeViewReadyEvent(SharedEvent):
    VIEW_READY = 'StoryModeViewReadyEvent.VIEW_READY'

    def __init__(self, viewID):
        super(StoryModeViewReadyEvent, self).__init__(self.VIEW_READY)
        self.viewID = viewID
