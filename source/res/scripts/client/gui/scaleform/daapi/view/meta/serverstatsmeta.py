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
        if self._isDAAPIInited():
            return self.flashObject.as_setPeripheryChanging(isChanged)

    def as_setServersListS(self, servers):
        if self._isDAAPIInited():
            return self.flashObject.as_setServersList(servers)

    def as_disableRoamingDDS(self, disable):
        if self._isDAAPIInited():
            return self.flashObject.as_disableRoamingDD(disable)

    def as_setServerStatsS(self, stats, tooltipType):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStats(stats, tooltipType)

    def as_setServerStatsInfoS(self, tooltipFullData):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStatsInfo(tooltipFullData)
