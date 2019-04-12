# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TabbedFullStatsMeta.py
from gui.Scaleform.daapi.view.battle.classic.base_stats import StatsBase

class TabbedFullStatsMeta(StatsBase):

    def onSelectQuest(self, questID):
        self._printOverrideError('onSelectQuest')

    def as_setActiveTabS(self, tabIndex):
        return self.flashObject.as_setActiveTab(tabIndex) if self._isDAAPIInited() else None

    def as_questProgressPerformS(self, data):
        return self.flashObject.as_questProgressPerform(data) if self._isDAAPIInited() else None

    def as_resetActiveTabS(self):
        return self.flashObject.as_resetActiveTab() if self._isDAAPIInited() else None

    def as_updateProgressTrackingS(self, data):
        return self.flashObject.as_updateProgressTracking(data) if self._isDAAPIInited() else None
