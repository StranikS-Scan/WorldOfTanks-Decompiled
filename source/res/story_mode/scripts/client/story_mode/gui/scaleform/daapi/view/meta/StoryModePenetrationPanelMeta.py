# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/meta/StoryModePenetrationPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoryModePenetrationPanelMeta(BaseDAAPIComponent):

    def as_setPenetrationS(self, penetrationType, isPurple):
        return self.flashObject.as_setPenetration(penetrationType, isPurple) if self._isDAAPIInited() else None
