# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_first_entry_view.py
from adisp import adisp_process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.PersonalMissionFirstEntryViewMeta import PersonalMissionFirstEntryViewMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showPersonalMissionBrowserView
from gui.game_control.links import URLMacros
from gui.server_events.pm_constants import PERSONAL_MISSIONS_SOUND_SPACE, SOUNDS, PM_TUTOR_FIELDS
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from helpers import i18n, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api

class PersonalMissionFirstEntryView(LobbySubView, PersonalMissionFirstEntryViewMeta):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE
    __settingsCore = dependency.descriptor(ISettingsCore)
    __CARDS = (3, 3, 4, 4)
    __R_PERSONAL_MISSION_FIRST_ENTRY_VIEW = R.strings.personal_missions.PersonalMissionFirstEntryView

    def __init__(self, ctx):
        super(PersonalMissionFirstEntryView, self).__init__(ctx)
        self.__urlMacros = URLMacros()
        self.__settings = GUI_SETTINGS.personalMissions.get('welcomeVideo', {})
        self.__cardsLen = len(self.__CARDS)

    def playVideo(self):
        if self.__settings.get('isEnabled', False):
            self.__showVideo()

    def backBtnClicked(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onViewClose(self, isAcceptBtnClick=False):
        if isAcceptBtnClick:
            self.__settingsCore.serverSettings.saveInUIStorage({PM_TUTOR_FIELDS.GREETING_SCREEN_SHOWN: True})
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS)), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onCardClick(self, cardIndex):
        self.__updateDetailedData(cardIndex)

    def onNextCardClick(self, cardIndex):
        self.__updateDetailedData(cardIndex + 1)

    def onPrevCardClick(self, cardIndex):
        self.__updateDetailedData(cardIndex - 1)

    def _populate(self):
        super(PersonalMissionFirstEntryView, self)._populate()
        infoBlocks = [ self.__makeTileData(cardIndex) for cardIndex in xrange(0, self.__cardsLen) ]
        firstEntry = not self.__settingsCore.serverSettings.getUIStorage().get(PM_TUTOR_FIELDS.GREETING_SCREEN_SHOWN)
        self.as_setInitDataS({'titleLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_TITLE,
         'bigBtnLabel': PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_ACKNOWLEDGEBTN,
         'playVideoBtnLabel': text_styles.concatStylesToSingleLine(icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_PLAYICON, width=14, height=15, vSpace=-2), i18n.makeString(PERSONAL_MISSIONS.PERSONALMISSIONFIRSTENTRYVIEW_VIDEOBTNLABEL)),
         'playVideoBtnVisible': self.__settings.get('isEnabled', False),
         'bgSource': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_INFOSCREENBG,
         'infoBlocks': infoBlocks,
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'isFirstEntry': firstEntry})
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MAX_MISSIONS_ZOOM)

    def _dispose(self):
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MIN_MISSIONS_ZOOM)
        super(PersonalMissionFirstEntryView, self)._dispose()

    def __updateDetailedData(self, cardIndex):
        cardIndex = self.__normalizeSlotIndex(cardIndex)
        blocksLen = self.__CARDS[cardIndex]
        blocks = []
        for blockIndex in xrange(0, blocksLen):
            blocks.append({'title': PERSONAL_MISSIONS.getBlockTitle(cardIndex, blockIndex),
             'description': PERSONAL_MISSIONS.getBlockDescription(cardIndex, blockIndex),
             'image': RES_ICONS.getBlockImageByStep(cardIndex, blockIndex)})

        item = self.__R_PERSONAL_MISSION_FIRST_ENTRY_VIEW.dyn('item{}'.format(cardIndex))
        data = {'index': cardIndex,
         'icon': RES_ICONS.getInfoIcon(cardIndex),
         'title': PERSONAL_MISSIONS.getCardHeader(cardIndex),
         'description': PERSONAL_MISSIONS.getCardInnerDescription(cardIndex),
         'blocks': blocks,
         'notificationIcon': RES_ICONS.MAPS_ICONS_LIBRARY_WARNINGICON_1,
         'notificationLabel': backport.text(item.warning()) if item and 'warning' in item.keys() else ''}
        self.as_setDetailedCardDataS(data)

    @adisp_process
    def __showVideo(self):
        url = yield self.__urlMacros.parse(self.__settings.get('url'))
        webHandlers = webApiCollection(ui_web_api.CloseViewWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
        ctx = {'url': url,
         'webHandlers': webHandlers,
         'returnAlias': self.alias}
        showPersonalMissionBrowserView(ctx)

    @staticmethod
    def __makeTileData(cardIndex):
        return {'index': cardIndex,
         'iconSource': RES_ICONS.getInfoIcon(cardIndex),
         'titleLabel': PERSONAL_MISSIONS.getCardHeader(cardIndex),
         'descriptionLabel': PERSONAL_MISSIONS.getCardDescription(cardIndex)}

    def __normalizeSlotIndex(self, slotIndex):
        if slotIndex >= self.__cardsLen:
            return 0
        return self.__cardsLen - 1 if slotIndex < 0 else slotIndex
