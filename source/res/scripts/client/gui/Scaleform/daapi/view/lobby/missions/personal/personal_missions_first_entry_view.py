# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_first_entry_view.py
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleHangarSoundCommand, handleHangarSoundCommandFini
from gui.Scaleform.daapi.view.meta.PersonalMissionFirstEntryViewMeta import PersonalMissionFirstEntryViewMeta
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control import gc_constants
from gui.game_control.links import URLMarcos
from gui.server_events.pm_constants import PERSONAL_MISSIONS_SOUND_SPACE, FIRST_ENTRY_STATE as _FES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from helpers import i18n, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBrowserController
from web_client_api.commands import createHangarSoundHandler

class PersonalMissionFirstEntryView(LobbySubView, PersonalMissionFirstEntryViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, ctx):
        super(PersonalMissionFirstEntryView, self).__init__(ctx)
        self.__currentVersionBrowserID = None
        self.__urlMacros = URLMarcos()
        self.__settings = GUI_SETTINGS.personalMissions.get('welcomeVideo', {})
        return

    def playVideo(self):
        if self.__settings.get('isEnabled', False):
            self.__showVideo()

    def backBtnClicked(self):
        self.__currentVersionBrowserID = None
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def bigBtnClicked(self):
        self.__settingsCore.serverSettings.setPersonalMissionsFirstEntryState(_FES.TUTORIAL_WAS_SHOWN)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalMissionFirstEntryView, self)._populate()
        self.as_setInitDataS({'titleLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_TITLE,
         'subtitleLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_SUBTITLE,
         'bigBtnLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ACKNOWLEDGEBTN,
         'playVideoBtnLabel': text_styles.concatStylesToSingleLine(icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_PLAYICON, width=14, height=15, vSpace=-2), i18n.makeString(PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_VIDEOBTNLABEL)),
         'playVideoBtnVisible': self.__settings.get('isEnabled', False),
         'bgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_INFOSCREENBG,
         'tileList': [self.__makeTileData(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET_BIG, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM0_HEADER, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM0_DESCR), self.__makeTileData(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_GEAR_BIG, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM2_HEADER, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM2_DESCR), self.__makeTileData(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_BALANCE, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM1_HEADER, PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ITEM1_DESCR)],
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'isFirstEntry': self.__settingsCore.serverSettings.getPersonalMissionsFirstEntryState() == _FES.NOT_VISITED})

    @process
    def __showVideo(self):
        url = yield self.__urlMacros.parse(self.__settings.get('url'))
        webBrowser = self.__getCurrentBrowser()
        if not webBrowser or url != webBrowser.url:
            title = i18n.makeString(PERSONAL_MISSIONS.PERSONALMISSIONS_VIDEO_TITLE)
            self.__currentVersionBrowserID = yield self.browserCtrl.load(url, title, showActionBtn=False, browserID=self.__currentVersionBrowserID, browserSize=gc_constants.BROWSER.VIDEO_SIZE, isDefault=False, showCloseBtn=True, handlers=self.__createWebHandlers())

    @staticmethod
    def __makeTileData(iconSource, titleLabel, descriptionLabel):
        return {'iconSource': iconSource,
         'titleLabel': titleLabel,
         'descriptionLabel': descriptionLabel}

    def __getCurrentBrowser(self):
        return self.browserCtrl.getBrowser(self.__currentVersionBrowserID)

    def __createWebHandlers(self):
        return [createHangarSoundHandler(handleHangarSoundCommand, handleHangarSoundCommandFini)]
