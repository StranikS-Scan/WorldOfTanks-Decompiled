# Embedded file name: scripts/client/messenger/gui/Scaleform/view/SearchContactView.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.gui.Scaleform.data.search_data_providers import SearchUsersDataProvider
from messenger.gui.Scaleform.meta.SearchContactViewMeta import SearchContactViewMeta
from messenger.gui.Scaleform.view import ACCOUNT_NAME_MIN_CHARS_LENGTH, ACCOUNT_NAME_MAX_CHARS_LENGTH
from messenger.proto.interfaces import ISearchHandler
from gui.shared import events, EVENT_BUS_SCOPE
from messenger_common_chat2 import MESSENGER_ACTION_IDS, MESSENGER_LIMITS
from gui.shared.rq_cooldown import getRequestCoolDown, REQUEST_SCOPE

class SearchContactView(SearchContactViewMeta, ISearchHandler):

    def __init__(self):
        super(SearchContactView, self).__init__()
        self._searchDP = None
        self.addListener(events.CoolDownEvent.BW_CHAT2, self.__handleSetSearchCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def search(self, data):
        self._searchDP.find(data)

    def onSearchComplete(self, result):
        pass

    def onSearchFailed(self, reason):
        pass

    def _populate(self):
        super(SearchContactView, self)._populate()
        self._searchDP = SearchUsersDataProvider()
        self._searchDP.init(self.as_getSearchDPS(), [self])
        self.as_setSearchResultTextS(i18n.makeString(MESSENGER.DIALOGS_SEARCHCONTACT_LABELS_RESULT))
        self.as_setSearchDisabledS(getRequestCoolDown(REQUEST_SCOPE.BW_CHAT2, MESSENGER_ACTION_IDS.FIND_USERS_BY_NAME))

    def _dispose(self):
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        self.removeListener(events.CoolDownEvent.BW_CHAT2, self.__handleSetSearchCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SearchContactView, self)._dispose()
        return

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_TITLE, MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_BTNCANCEL_LABEL, MESSENGER.CONTACTS_SEARCHVIEW_TOOLTIPS_BTNS_ADD, MESSENGER.CONTACTS_SEARCHVIEW_TOOLTIPS_BTNS_CLOSE)
        defData['inputPrompt'] = MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_SEARCHINPUTPROMPT
        defData['searchCoolDown'] = str(MESSENGER_LIMITS.FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC)
        defData['accMinChars'] = ACCOUNT_NAME_MIN_CHARS_LENGTH
        defData['accMaxChars'] = ACCOUNT_NAME_MAX_CHARS_LENGTH
        return defData

    def __handleSetSearchCoolDown(self, event):
        if event.requestID is MESSENGER_ACTION_IDS.FIND_USERS_BY_NAME:
            self.as_setSearchDisabledS(event.coolDown)
