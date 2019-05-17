# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/servers_data_provider.py
import logging
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import icons
from gui.shared.formatters.servers import formatPingStatus
from helpers import dependency
from helpers.i18n import makeString as _ms
from predefined_hosts import AUTO_LOGIN_QUERY_URL
from predefined_hosts import HOST_AVAILABILITY, PING_STATUSES, g_preDefinedHosts
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class _INDICATOR_STATUSES(object):
    WAITING = -1
    IGNORED = -2
    ALL = (PING_STATUSES.UNDEFINED,
     PING_STATUSES.HIGH,
     PING_STATUSES.NORM,
     PING_STATUSES.LOW,
     WAITING,
     IGNORED)


class ServersDataProvider(SortableDAAPIDataProvider):
    __PING_MAX_VALUE = 999
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ServersDataProvider, self).__init__()
        self._list = []
        self.__mapping = {}
        self.__selectedID = None
        self.__isColorBlind = self.__settingsCore.getSetting('isColorBlind')
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    @property
    def collection(self):
        return self._list

    @property
    def isColorBlind(self):
        return self.__isColorBlind

    def emptyItem(self):
        return None

    def clear(self):
        self.__clearLists()
        self.__selectedID = None
        return

    def fini(self):
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.clear()
        self.destroy()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def getSelectedID(self):
        return self.__selectedID

    def setSelectedID(self, sid):
        self.__selectedID = sid

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                _logger.error('Item not found %i', index)

        return vo

    def buildList(self, cache):
        self.__clearLists()
        for index, item in enumerate(cache):
            vo = self._makeVO(index, item)
            self._list.append(vo)
            self.__mapping[vo['id']] = index

        if self.__selectedID not in self.__mapping:
            self.__selectedID = None
        return

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def refreshRandomItems(self, indexes, items):
        self.flashObject.invalidateItems(indexes, items)

    def refreshSingleItem(self, index, item):
        self.flashObject.invalidateItem(index, item)

    def requestItemAtHandler(self, idx):
        item = super(ServersDataProvider, self).requestItemAtHandler(idx)
        if item is None:
            _logger.debug('Item with id %i is None', idx)
        return item

    def _makeVO(self, index, item):
        hostName = item['data']
        pingValue, pingStatus = g_preDefinedHosts.getHostPingData(hostName)
        pingValue = min(pingValue, self.__PING_MAX_VALUE)
        csisStatus = item['csisStatus']
        serverName = item['label']
        pingIndicatorState = self.__getUpdatedPingStatus(pingStatus, item)
        enabled = item.get('enabled', csisStatus != HOST_AVAILABILITY.NOT_AVAILABLE)
        pingValueStr = formatPingStatus(csisStatus, self.__isColorBlind, False, pingStatus, pingValue)
        vo = {'id': item.get('id', 0),
         'data': hostName,
         'csisStatus': csisStatus,
         'label': serverName,
         'pingState': pingIndicatorState,
         'pingValue': pingValueStr,
         'enabled': enabled}
        if csisStatus == HOST_AVAILABILITY.NOT_RECOMMENDED:
            vo['tooltip'] = _ms(TOOLTIPS.SERVER_NOTRECOMENDED, icon=icons.serverAlert(), server=serverName)
        elif 'tooltip' in item:
            vo['tooltip'] = item['tooltip']
        return vo

    def __clearLists(self):
        self._list = []
        self.__mapping.clear()

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__isColorBlind = diff['isColorBlind']
            for item in self._list:
                pingValue, pingStatus = g_preDefinedHosts.getHostPingData(item['data'])
                pingValueStr = formatPingStatus(item['csisStatus'], self.__isColorBlind, False, pingStatus, pingValue)
                item['pingValue'] = pingValueStr

            self.refresh()

    def __getUpdatedPingStatus(self, pingStatus, item):
        csisStatus = item['csisStatus']
        if pingStatus == PING_STATUSES.REQUESTED:
            return _INDICATOR_STATUSES.WAITING
        if csisStatus == HOST_AVAILABILITY.RECOMMENDED or csisStatus == HOST_AVAILABILITY.UNKNOWN:
            return self.__checkPingForValidStatus(pingStatus)
        if csisStatus in (HOST_AVAILABILITY.NOT_AVAILABLE, HOST_AVAILABILITY.NOT_RECOMMENDED):
            return _INDICATOR_STATUSES.IGNORED
        if csisStatus == HOST_AVAILABILITY.REQUESTED:
            return _INDICATOR_STATUSES.WAITING
        return _INDICATOR_STATUSES.IGNORED if item['data'] == AUTO_LOGIN_QUERY_URL else self.__checkPingForValidStatus(pingStatus)

    @staticmethod
    def __checkPingForValidStatus(incomeStatus):
        if incomeStatus in _INDICATOR_STATUSES.ALL:
            return incomeStatus
        else:
            _logger.error('Mismatch ping status "%s" and available indicator statuses.', incomeStatus)
            return None
