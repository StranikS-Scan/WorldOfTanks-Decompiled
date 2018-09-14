# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_filter_popover.py
from account_helpers.AccountSettings import AccountSettings, MISSIONS_PAGE
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import HIDE_DONE, HIDE_UNAVAILABLE
from gui.Scaleform.daapi.view.meta.MissionsFilterPopoverViewMeta import MissionsFilterPopoverViewMeta
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import MissionsEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms

class MissionsFilterPopoverView(MissionsFilterPopoverViewMeta):

    def __init__(self, ctx=None):
        self.__filterData = None
        super(MissionsFilterPopoverView, self).__init__()
        return

    def changeFilter(self, hideUnavailable, hideDone):
        newData = {HIDE_DONE: hideDone,
         HIDE_UNAVAILABLE: hideUnavailable}
        if self.__filterData != newData:
            self.__filterData = newData
            AccountSettings.setFilter(MISSIONS_PAGE, self.__filterData)
            self.fireEvent(MissionsEvent(MissionsEvent.ON_FILTER_CHANGED, ctx=self.__filterData), EVENT_BUS_SCOPE.LOBBY)

    def setDefaultFilter(self):
        self.changeFilter(False, False)

    def _populate(self):
        self.__filterData = AccountSettings.getFilter(MISSIONS_PAGE)
        super(MissionsFilterPopoverView, self)._populate()
        self.as_setInitDataS(self.__getInitialVO())
        self.as_setStateS(self.__filterData)

    def _dispose(self):
        self.fireEvent(MissionsEvent(MissionsEvent.ON_FILTER_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        self.__filterData = None
        super(MissionsFilterPopoverView, self)._dispose()
        return

    def __getInitialVO(self):
        dataVO = {'titleLabel': text_styles.highTitle(QUESTS.MISSIONS_FILTER_POPOVER_TITLE),
         'hideDoneLabel': _ms(QUESTS.MISSIONS_FILTER_POPOVER_HIDEDONE),
         'hideUnavailableLabel': _ms(QUESTS.MISSIONS_FILTER_POPOVER_HIDEUNAVAILABLE),
         'defaultButtonLabel': _ms(QUESTS.MISSIONS_FILTER_POPOVER_DEFAULTBUTTON_LABEL),
         'defaultButtonTooltip': makeTooltip(QUESTS.MISSIONS_FILTER_POPOVER_DEFAULTBUTTON_HEADER, QUESTS.MISSIONS_FILTER_POPOVER_DEFAULTBUTTON_BODY)}
        return dataVO
