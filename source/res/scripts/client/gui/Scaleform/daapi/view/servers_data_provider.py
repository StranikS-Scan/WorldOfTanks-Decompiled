# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/servers_data_provider.py
from account_helpers.settings_core.SettingsCore import g_settingsCore
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from helpers.i18n import makeString as _ms
from predefined_hosts import HOST_AVAILABILITY, getPingStatus, PING_STATUSES, g_preDefinedHosts, UNDEFINED_PING_VAL
from predefined_hosts import AUTO_LOGIN_QUERY_URL
_UNAVAILABLE_DATA_PLACEHOLDER = '--'
_PING_MAX_VALUE = 999

class _INDICATOR_STATUSES:
    WAITING = -1
    IGNORED = -2


class ServersDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(ServersDataProvider, self).__init__()
        self._list = []
        self._listMapping = {}
        self.__mapping = {}
        self.__selectedID = None
        self.__isColorBlind = g_settingsCore.getSetting('isColorBlind')
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def setSelectedID(self, sid):
        self.__selectedID = sid

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def buildList(self, cache):
        self.clear()
        if cache:
            for index, item in enumerate(cache):
                self._list.append(self._makeVO(index, item))

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def refreshItem(self, cache, clanDBID):
        isSelected = self.__selectedID == clanDBID
        self.buildList(cache)
        return True if isSelected and clanDBID not in self.__mapping else False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def refreshRandomItems(self, indexes, items):
        self.flashObject.invalidateItems(indexes, items)

    def refreshSingleItem(self, index, item):
        self.flashObject.invalidateItem(index, item)

    def _makeVO(self, index, item):
        pings = g_preDefinedHosts.getPingResult()
        hostName = item['data']
        pingValue = min(pings.get(hostName, UNDEFINED_PING_VAL), _PING_MAX_VALUE)
        csisStatus = item['csisStatus']
        serverName = item['label']
        pingState = self.__updatePingStatus(pingValue, item)
        enabled = csisStatus != HOST_AVAILABILITY.NOT_AVAILABLE
        strVal = _UNAVAILABLE_DATA_PLACEHOLDER if pingState == PING_STATUSES.UNDEFINED else str(pingValue)
        if pingState == PING_STATUSES.LOW:
            pingValueStr = text_styles.goodPing(strVal)
        else:
            pingValueStr = text_styles.standartPing(strVal)
        vo = {'id': item.get('id', 0),
         'data': hostName,
         'csisStatus': csisStatus,
         'label': serverName,
         'pingState': pingState,
         'pingValue': pingValueStr,
         'colorBlind': self.__isColorBlind,
         'enabled': enabled}
        if csisStatus == HOST_AVAILABILITY.NOT_RECOMMENDED:
            vo['tooltip'] = _ms(TOOLTIPS.SERVER_NOTRECOMENDED, icon=icons.serverAlert(), server=serverName)
        return vo

    def requestItemAtHandler(self, idx):
        item = super(ServersDataProvider, self).requestItemAtHandler(idx)
        if item is None:
            LOG_DEBUG(idx, item)
        return item

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__isColorBlind = diff['isColorBlind']
            for item in self._list:
                item['colorBlind'] = self.__isColorBlind

            self.refresh()

    @staticmethod
    def __updatePingStatus(pingValue, item):
        csisStatus = item['csisStatus']
        pingState = getPingStatus(pingValue)
        if csisStatus == HOST_AVAILABILITY.RECOMMENDED:
            return pingState
        elif csisStatus in (HOST_AVAILABILITY.NOT_AVAILABLE, HOST_AVAILABILITY.NOT_RECOMMENDED):
            return _INDICATOR_STATUSES.IGNORED
        elif csisStatus == HOST_AVAILABILITY.UNKNOWN:
            return _INDICATOR_STATUSES.WAITING
        elif item['data'] == AUTO_LOGIN_QUERY_URL:
            return _INDICATOR_STATUSES.IGNORED
        else:
            return pingState
