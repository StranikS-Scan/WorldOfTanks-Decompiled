# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/meta/StoryModeSubtitlesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoryModeSubtitlesMeta(BaseDAAPIComponent):

    def as_showS(self, message):
        return self.flashObject.as_show(message) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
