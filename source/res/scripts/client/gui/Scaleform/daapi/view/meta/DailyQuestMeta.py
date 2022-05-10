# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DailyQuestMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DailyQuestMeta(BaseDAAPIComponent):

    def updateWidgetLayout(self, value):
        self._printOverrideError('updateWidgetLayout')

    def as_setEnabledS(self, isEnabled):
        return self.flashObject.as_setEnabled(isEnabled) if self._isDAAPIInited() else None
