# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ServerStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ServerStatsMeta(BaseDAAPIComponent):

    def relogin(self, id):
        self._printOverrideError('relogin')

    def startListenCsisUpdate(self, startListenCsis):
        self._printOverrideError('startListenCsisUpdate')

    def as_changePeripheryFailedS(self):
        return self.flashObject.as_changePeripheryFailed() if self._isDAAPIInited() else None

    def as_disableRoamingDDS(self, disable):
        return self.flashObject.as_disableRoamingDD(disable) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setServerStatsInfoS(self, tooltipFullData):
        return self.flashObject.as_setServerStatsInfo(tooltipFullData) if self._isDAAPIInited() else None

    def as_getServersDPS(self):
        return self.flashObject.as_getServersDP() if self._isDAAPIInited() else None

    def as_setSelectedServerIndexS(self, index):
        return self.flashObject.as_setSelectedServerIndex(index) if self._isDAAPIInited() else None
