# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TabScreenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TabScreenMeta(BaseDAAPIComponent):

    def onSelectQuest(self, questID):
        self._printOverrideError('onSelectQuest')

    def onStatsTableVisibiltyToggled(self, isVisible):
        self._printOverrideError('onStatsTableVisibiltyToggled')

    def as_questProgressPerformS(self, data):
        return self.flashObject.as_questProgressPerform(data) if self._isDAAPIInited() else None

    def as_updateProgressTrackingS(self, data):
        return self.flashObject.as_updateProgressTracking(data) if self._isDAAPIInited() else None

    def as_setActiveTabS(self, tabIndex):
        return self.flashObject.as_setActiveTab(tabIndex) if self._isDAAPIInited() else None

    def as_resetActiveTabS(self):
        return self.flashObject.as_resetActiveTab() if self._isDAAPIInited() else None

    def as_updateTabsS(self, dataProvider):
        return self.flashObject.as_updateTabs(dataProvider) if self._isDAAPIInited() else None
