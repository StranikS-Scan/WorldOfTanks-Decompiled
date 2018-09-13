# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ServerStatsMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ServerStatsMeta(DAAPIModule):

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

    def as_setServerStatsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStats(data)

    def as_setServerStatsInfoS(self, tooltipFullData):
        if self._isDAAPIInited():
            return self.flashObject.as_setServerStatsInfo(tooltipFullData)
