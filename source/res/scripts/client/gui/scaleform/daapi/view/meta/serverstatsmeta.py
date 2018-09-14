# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ServerStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ServerStatsMeta(BaseDAAPIComponent):

    def getServers(self):
        self._printOverrideError('getServers')

    def relogin(self, id):
        self._printOverrideError('relogin')

    def isCSISUpdateOnRequest(self):
        self._printOverrideError('isCSISUpdateOnRequest')

    def startListenCsisUpdate(self, startListenCsis):
        self._printOverrideError('startListenCsisUpdate')

    def as_setPeripheryChangingS(self, isChanged):
        return self.flashObject.as_setPeripheryChanging(isChanged) if self._isDAAPIInited() else None

    def as_setServersListS(self, servers):
        return self.flashObject.as_setServersList(servers) if self._isDAAPIInited() else None

    def as_disableRoamingDDS(self, disable):
        return self.flashObject.as_disableRoamingDD(disable) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setServerStatsInfoS(self, tooltipFullData):
        return self.flashObject.as_setServerStatsInfo(tooltipFullData) if self._isDAAPIInited() else None
