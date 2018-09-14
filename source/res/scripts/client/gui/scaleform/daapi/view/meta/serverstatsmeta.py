# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ServerStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ServerStatsMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def relogin(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('relogin')

    def startListenCsisUpdate(self, startListenCsis):
        """
        :param startListenCsis:
        :return :
        """
        self._printOverrideError('startListenCsisUpdate')

    def as_changePeripheryFailedS(self):
        """
        :return :
        """
        return self.flashObject.as_changePeripheryFailed() if self._isDAAPIInited() else None

    def as_disableRoamingDDS(self, disable):
        """
        :param disable:
        :return :
        """
        return self.flashObject.as_disableRoamingDD(disable) if self._isDAAPIInited() else None

    def as_setServerStatsS(self, stats, tooltipType):
        """
        :param stats:
        :param tooltipType:
        :return :
        """
        return self.flashObject.as_setServerStats(stats, tooltipType) if self._isDAAPIInited() else None

    def as_setServerStatsInfoS(self, tooltipFullData):
        """
        :param tooltipFullData:
        :return :
        """
        return self.flashObject.as_setServerStatsInfo(tooltipFullData) if self._isDAAPIInited() else None

    def as_getServersDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getServersDP() if self._isDAAPIInited() else None

    def as_setSelectedServerIndexS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_setSelectedServerIndex(index) if self._isDAAPIInited() else None
