# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_intro.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE
from gui.ranked_battles.ranked_helpers import getRankedBattlesIntroPageUrl
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesIntroMeta import RankedBattlesIntroMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared import event_dispatcher, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
BLOCKS_COUNT = 3

class RankedBattlesIntro(LobbySubView, RankedBattlesIntroMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE

    def onAcceptClick(self):
        self.__setShowStateFlags()
        self.onClose()

    def onClose(self):
        self.__setShowStateFlags()
        event_dispatcher.showHangar()

    def onDetailedClick(self):
        self.__setShowStateFlags()
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID})

    def onPlayVideoClick(self):
        self.__showVideo()

    def _populate(self):
        super(RankedBattlesIntro, self)._populate()
        headerData = {'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
         'leftSideText': backport.text(R.strings.ranked_battles.intoPage.description()),
         'rightSideText': None,
         'tooltip': None}
        data = []
        for index in range(BLOCKS_COUNT):
            index += 1
            title = backport.text(R.strings.ranked_battles.intoPage.blocks.dyn('block{}'.format(index)).title())
            descr = backport.text(R.strings.ranked_battles.intoPage.blocks.dyn('block{}'.format(index)).description())
            data.append({'title': title,
             'description': descr})

        self.as_setDataS(headerData, data)
        return

    def __showVideo(self):
        webHandlers = webApiCollection(ui_web_api.CloseViewWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BROWSER_VIEW, ctx={'url': getRankedBattlesIntroPageUrl(),
         'webHandlers': webHandlers,
         'returnAlias': self.alias}), EVENT_BUS_SCOPE.LOBBY)

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setShowStateFlags(self):
        stateFlags = self.__getShowStateFlags()
        stateFlags[GuiSettingsBehavior.RANKED_WELCOME_VIEW_SHOWED] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
