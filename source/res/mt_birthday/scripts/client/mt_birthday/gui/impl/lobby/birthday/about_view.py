# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/about_view.py
from gui.impl.common.browser import Browser, BrowserSettings
from gui.impl.gen import R
from gui import GUI_SETTINGS
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api

def _browserHandlers():
    return webApiCollection(PromoWebApi, RequestWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)


def createAboutView(events, *_):
    return AboutView(events)


class AboutView(Browser):
    __slots__ = ('__mainViewEvents',)

    def __init__(self, mainViewEvents):
        super(AboutView, self).__init__(GUI_SETTINGS.lookup('birthdayInfoPageURL'), BrowserSettings(R.views.common.Browser()), _browserHandlers())
        self.__mainViewEvents = mainViewEvents

    def _getEvents(self):
        return super(AboutView, self)._getEvents() + ((self.__mainViewEvents.onTabChange, self.__onTabChange), (self.onBrowserObtained, self.__setIsAudioMutable))

    def __setIsAudioMutable(self, _):
        self.browser.setIsAudioMutable(True)

    def __onTabChange(self, oldTabId, _):
        if oldTabId == TabId.ABOUT and self.browser is not None:
            self.browser.refresh()
        return
