# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DailyQuestMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DailyQuestMeta(BaseDAAPIComponent):

    def updateWidgetLayout(self, value):
        self._printOverrideError('updateWidgetLayout')

    def as_showWidgetS(self):
        return self.flashObject.as_showWidget() if self._isDAAPIInited() else None

    def as_hideWidgetS(self):
        return self.flashObject.as_hideWidget() if self._isDAAPIInited() else None
