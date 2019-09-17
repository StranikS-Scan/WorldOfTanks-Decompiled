# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestRaceIngameHelpMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FestRaceIngameHelpMeta(BaseDAAPIComponent):

    def as_setTitleS(self, title):
        return self.flashObject.as_setTitle(title) if self._isDAAPIInited() else None

    def as_setItemsS(self, items):
        return self.flashObject.as_setItems(items) if self._isDAAPIInited() else None

    def as_setHotKeyHintS(self, hint):
        return self.flashObject.as_setHotKeyHint(hint) if self._isDAAPIInited() else None

    def as_setHotKeyHintEnabledS(self, enabled):
        return self.flashObject.as_setHotKeyHintEnabled(enabled) if self._isDAAPIInited() else None
