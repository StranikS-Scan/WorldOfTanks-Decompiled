# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_intro.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE
from gui.ranked_battles.ranked_helpers import getRankedBattlesIntroPageUrl
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesIntroMeta import RankedBattlesIntroMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared import event_dispatcher, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.utils.functions import getUniqueViewName
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
BLOCKS_COUNT = 3

class RankedBattlesIntro(LobbySubView, RankedBattlesIntroMeta):
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def onAcceptClick(self):
        self.__setShowStateFlags()
        self.onClose()

    def onClose(self):
        self.__setShowStateFlags()
        event_dispatcher.showHangar()

    def onDetailedClick(self):
        url = GUI_SETTINGS.lookup('infoPageRanked')
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def onPlayVideoClick(self):
        self.__showVideo()

    def _populate(self):
        super(RankedBattlesIntro, self)._populate()
        self.__update()
        self.__rankedController.onUpdated += self.__update
        self.__rankedController.onGameModeStatusUpdated += self.__update
        self.__rankedController.onGameModeStatusTick += self.__updateTimer

    def _dispose(self):
        self.__rankedController.onGameModeStatusTick -= self.__updateTimer
        self.__rankedController.onGameModeStatusUpdated -= self.__update
        self.__rankedController.onUpdated -= self.__update
        super(RankedBattlesIntro, self)._dispose()

    def __update(self, _=None):
        headerData = {'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
         'leftSideText': backport.text(R.strings.ranked_battles.introPage.description()),
         'rightSideText': None,
         'tooltip': None}
        blocksData = []
        for index in range(BLOCKS_COUNT):
            index += 1
            imgSource = backport.image(R.images.gui.maps.icons.rankedBattles.intro.dyn('block{}'.format(index))())
            title = text_styles.promoSubTitle(backport.text(R.strings.ranked_battles.introPage.blocks.dyn('block{}'.format(index)).title()))
            descr = text_styles.mainBig(backport.text(R.strings.ranked_battles.introPage.blocks.dyn('block{}'.format(index)).description()))
            blocksData.append({'imgSource': imgSource,
             'title': title,
             'description': descr})

        if not self.__rankedController.isYearRewardEnabled():
            blocksData[-1]['imgSource'] = backport.image(R.images.gui.maps.icons.rankedBattles.intro.yearRewardDisabled())
            blocksData[-1]['description'] = text_styles.mainBig(backport.text(R.strings.ranked_battles.introPage.blocks.yearRewardDisabled()))
        url = getRankedBattlesIntroPageUrl()
        self.__state = RANKEDBATTLES_CONSTS.INTRO_STATE_NORMAL
        if self.__rankedController.isFrozen():
            self.__state = RANKEDBATTLES_CONSTS.INTRO_STATE_DISABLED
            if not self.__rankedController.getSeasonPassed() and not self.__rankedController.getCurrentSeason():
                self.__state = RANKEDBATTLES_CONSTS.INTRO_STATE_BEFORE_SEASON
        if self.__state == RANKEDBATTLES_CONSTS.INTRO_STATE_DISABLED:
            self.as_setAlertMessageBlockDataS({'alertIcon': backport.image(R.images.gui.maps.icons.library.alertBigIcon()),
             'statusText': text_styles.vehicleStatusCriticalText(backport.text(R.strings.ranked_battles.introPage.alert.disabled())),
             'buttonVisible': False})
        elif self.__state == RANKEDBATTLES_CONSTS.INTRO_STATE_BEFORE_SEASON:
            self.__updateTimer()
        if self.__state != RANKEDBATTLES_CONSTS.INTRO_STATE_NORMAL and self.__rankedController.getRankedWelcomeCallback() is None:
            self.__rankedController.setRankedWelcomeCallback(lambda : None)
        self.as_setDataS({'state': self.__state,
         'hasURL': bool(url),
         'headerData': headerData,
         'blocksData': blocksData})
        return

    def __updateTimer(self):
        timeTill = self.__rankedController.getTimer()
        if self.__state == RANKEDBATTLES_CONSTS.INTRO_STATE_BEFORE_SEASON:
            self.as_setBeforeSeasonBlockDataS({'title': text_styles.highlightText(backport.text(R.strings.ranked_battles.introPage.alert.beforeSeason())),
             'time': text_styles.highlightText(backport.getTillTimeStringByRClass(timeTill, R.strings.ranked_battles.introPage.timeLeft)),
             'iconSrc': backport.image(R.images.gui.maps.icons.library.ClockIcon_1())})

    def __showVideo(self):
        webHandlers = webApiCollection(ui_web_api.CloseViewWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
        alias = VIEW_ALIAS.BROWSER_VIEW
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'url': getRankedBattlesIntroPageUrl(),
         'webHandlers': webHandlers,
         'returnAlias': self.alias}), EVENT_BUS_SCOPE.LOBBY)

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setShowStateFlags(self):
        if self.__state != RANKEDBATTLES_CONSTS.INTRO_STATE_NORMAL:
            return
        stateFlags = self.__getShowStateFlags()
        stateFlags[GuiSettingsBehavior.RANKED_WELCOME_VIEW_SHOWED] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
