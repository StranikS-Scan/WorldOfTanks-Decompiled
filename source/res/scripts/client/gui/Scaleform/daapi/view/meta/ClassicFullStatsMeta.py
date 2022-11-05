# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClassicFullStatsMeta.py
from gui.Scaleform.daapi.view.battle.shared.tabbed_full_stats import TabbedFullStatsComponent

class ClassicFullStatsMeta(TabbedFullStatsComponent):

    def onSelectQuest(self, questID):
        self._printOverrideError('onSelectQuest')

    def onPersonalReservesTabViewed(self, visible):
        self._printOverrideError('onPersonalReservesTabViewed')

    def as_questProgressPerformS(self, data):
        return self.flashObject.as_questProgressPerform(data) if self._isDAAPIInited() else None

    def as_updateProgressTrackingS(self, data):
        return self.flashObject.as_updateProgressTracking(data) if self._isDAAPIInited() else None
