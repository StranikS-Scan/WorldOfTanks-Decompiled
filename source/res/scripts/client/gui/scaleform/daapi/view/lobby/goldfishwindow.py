# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/GoldFishWindow.py
from account_helpers.AccountSettings import AccountSettings, GOLD_FISH_LAST_SHOW_TIME
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.GoldFishWindowMeta import GoldFishWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.gold_fish import isGoldFishActionActive
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events
from helpers.time_utils import getCurrentTimestamp
BTN_WIDTH = 120

class GoldFishWindow(GoldFishWindowMeta):

    def __init__(self, _ = None):
        super(GoldFishWindow, self).__init__()

    def onBtnClick(self, action):
        if action == 'closeAction':
            self.onWindowClose()

    def eventHyperLinkClicked(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))

    def onWindowClose(self):
        if isGoldFishActionActive():
            AccountSettings.setFilter(GOLD_FISH_LAST_SHOW_TIME, getCurrentTimestamp())
            self.fireEvent(events.CloseWindowEvent(events.CloseWindowEvent.GOLD_FISH_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def _populate(self):
        super(GoldFishWindow, self)._populate()
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_GOLDFISH_GOLDFISHBG, 0)
        self.as_setWindowTitleS(MENU.GOLDFISH_WINDOWHEADER)
        self.as_setWindowTextsS(MENU.GOLDFISH_HEADER, MENU.GOLDFISH_EVENTTITLE, MENU.GOLDFISH_EVENTTEXT, MENU.GOLDFISH_EVENTLINK)
        self.as_setButtonsS([{'label': MENU.GOLDFISH_BUTTONCLOSE,
          'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK,
          'action': 'closeAction',
          'isFocused': True,
          'tooltip': ''}], TEXT_ALIGN.RIGHT, BTN_WIDTH)
