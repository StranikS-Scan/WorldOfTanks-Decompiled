# Embedded file name: scripts/client/messenger/gui/Scaleform/data/search_data_providers.py
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter
from messenger.proto.bw.search_processors import SearchChannelsProcessor
from messenger.proto.bw_chat2.search_processor import SearchUsersProcessor
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import ISearchHandler

class SearchDataProvider(DAAPIDataProvider, ISearchHandler):

    def __init__(self, processor):
        super(SearchDataProvider, self).__init__()
        self._processor = processor
        self._processor.addHandler(self)
        self._list = []

    def __del__(self):
        LOG_DEBUG('SearchDataProvider deleted:', self)

    @property
    def processor(self):
        return self._processor

    @property
    def collection(self):
        return self._list

    def init(self, flashObject, exHandlers = None):
        self.setFlashObject(flashObject)
        self._processor.init()
        if exHandlers is not None and hasattr(exHandlers, '__iter__'):
            for handler in exHandlers:
                self._processor.addHandler(handler)

        return

    def fini(self):
        self._dispose()
        if self._processor is not None:
            self._processor.fini()
            self._processor = None
        return

    def find(self, token, **kwargs):
        return self._processor.find(token, **kwargs)

    def onSearchComplete(self, result):
        if not len(result):
            SystemMessages.pushI18nMessage(MESSENGER.CLIENT_INFORMATION_EMPTYSEARCHRESULT_MESSAGE, type=SystemMessages.SM_TYPE.Warning)
        self.buildList(result)
        self.refresh()

    def onSearchFailed(self, reason):
        if reason:
            SystemMessages.pushMessage(reason, type=SystemMessages.SM_TYPE.Error)
        self._list = []
        self.refresh()


class SearchChannelsDataProvider(SearchDataProvider):

    def __init__(self, searchProcessor = None):
        if searchProcessor is None:
            searchProcessor = SearchChannelsProcessor()
        super(SearchChannelsDataProvider, self).__init__(searchProcessor)
        return

    def buildList(self, result):
        self._list = []
        result = sorted(result, key=lambda item: item.getFullName().lower())
        for item in result:
            self._list.append({'id': item.getID(),
             'name': item.getFullName()})

    def emptyItem(self):
        return {'id': 0,
         'name': ''}

    def onExcludeFromSearch(self, entity):
        channelID = entity.getID()
        self._list = filter(lambda item: item['id'] != channelID, self._list)
        self.refresh()


class SearchUsersDataProvider(SearchDataProvider):

    def __init__(self, exclude = None):
        super(SearchUsersDataProvider, self).__init__(SearchUsersProcessor())
        self._converter = ContactConverter()
        if exclude is not None:
            self.__exclude = exclude
        else:
            self.__exclude = []
        return

    def buildList(self, result):
        self._list = []
        result = sorted(result, cmp=self._getSearchComparator)
        for item in result:
            if item.getID() not in self.__exclude:
                self._list.append(self._converter.makeVO(item))

    def emptyItem(self):
        return None

    def init(self, flashObject, exHandlers = None):
        super(SearchUsersDataProvider, self).init(flashObject, exHandlers)
        g_messengerEvents.users.onUserActionReceived += self.__onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated

    def fini(self):
        super(SearchUsersDataProvider, self).fini()
        g_messengerEvents.users.onUserActionReceived -= self.__onUserActionReceived
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated

    def _getSearchComparator(self, user, other):
        return cmp(user.getName().lower(), other.getName().lower())

    def __onUserActionReceived(self, _, user):
        self.__updateUserInSearch(user)

    def __onUserStatusUpdated(self, user):
        self.__updateUserInSearch(user)

    def __updateUserInSearch(self, user):
        for idx, item in enumerate(self._list):
            if item['dbID'] == user.getID():
                newItem = self._converter.makeVO(user)
                newItem['userProps']['clanAbbrev'] = item['userProps']['clanAbbrev']
                self._list[idx] = newItem
                break

        self.refresh()
