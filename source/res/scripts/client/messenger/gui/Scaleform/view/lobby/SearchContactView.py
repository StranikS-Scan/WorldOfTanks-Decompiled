# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/SearchContactView.py
from gui.Scaleform.locale.MESSENGER import MESSENGER
from helpers import i18n
from messenger.gui.Scaleform.data.search_data_providers import SearchUsersDataProvider
from messenger.gui.Scaleform.meta.SearchContactViewMeta import SearchContactViewMeta
from messenger.gui.Scaleform.view.lobby import ACCOUNT_NAME_MIN_CHARS_LENGTH, ACCOUNT_NAME_MAX_CHARS_LENGTH
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.interfaces import ISearchHandler
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.rq_cooldown import getRequestCoolDown

class SearchContactView(SearchContactViewMeta, ISearchHandler):

    def __init__(self):
        super(SearchContactView, self).__init__()
        self._searchDP = None
        self._cooldownInfo = self.proto.contacts.getUserSearchCooldownInfo()
        self.addListener(self._cooldownInfo.eventType, self.__handleSetSearchCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def search(self, data):
        self._searchDP.find(data)

    def onSearchComplete(self, result):
        pass

    def onSearchFailed(self, reason):
        pass

    def _populate(self):
        self._searchDP = SearchUsersDataProvider(self.proto.contacts.getUserSearchProcessor())
        super(SearchContactView, self)._populate()
        self._searchDP.init(self.as_getSearchDPS(), [self])
        self.as_setSearchResultTextS(i18n.makeString(MESSENGER.DIALOGS_SEARCHCONTACT_LABELS_RESULT))
        self.as_setSearchDisabledS(getRequestCoolDown(self._cooldownInfo.requestScope, self._cooldownInfo.actionId))

    def _dispose(self):
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        self.removeListener(self._cooldownInfo.eventType, self.__handleSetSearchCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SearchContactView, self)._dispose()
        return

    def _getInitDataObject(self):
        defData = self._getDefaultInitData(MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_TITLE, MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_BTNOK_LABEL, MESSENGER.MESSENGER_CONTACTS_VIEW_ADDUSER_BTNCANCEL_LABEL, MESSENGER.CONTACTS_SEARCHVIEW_TOOLTIPS_BTNS_ADD, MESSENGER.CONTACTS_SEARCHVIEW_TOOLTIPS_BTNS_CLOSE)
        defData['inputPrompt'] = MESSENGER.MESSENGER_CONTACTS_SEARCHUSERS_SEARCHINPUTPROMPT
        defData['searchCoolDown'] = str(self._searchDP.processor.getSearchCoolDown())
        defData['accMinChars'] = ACCOUNT_NAME_MIN_CHARS_LENGTH
        defData['accMaxChars'] = ACCOUNT_NAME_MAX_CHARS_LENGTH
        return defData

    def __handleSetSearchCoolDown(self, event):
        if event.requestID is self._cooldownInfo.actionId:
            self.as_setSearchDisabledS(event.coolDown)
