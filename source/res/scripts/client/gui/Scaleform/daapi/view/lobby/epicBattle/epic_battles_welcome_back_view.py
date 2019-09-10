# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_battles_welcome_back_view.py
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EpicBattlesWelcomeBackViewMeta import EpicBattlesWelcomeBackViewMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.game_control.links import URLMacros
from gui.game_control import gc_constants
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from helpers import dependency
from helpers.i18n import makeString as localize
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.game_control import IEpicBattleMetaGameController
from web.web_client_api.sound import HangarSoundWebApi
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from epic_cycle_helpers import getCurrentWelcomeScreenVersion
_NR_OF_TILES = 3
_DEFAULT_TILE_SHOW_DELAY = 200
_TILE_SHOW_DELAY_STEP = 180

class EpicBattlesWelcomeBackView(LobbySubView, EpicBattlesWelcomeBackViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(EpicBattlesWelcomeBackView, self).__init__(ctx)
        self.__browserID = None
        self.__urlMacros = URLMacros()
        self.__settings = GUI_SETTINGS.epicWelcomeBack.get('welcomeVideo', {})
        self.__backPageAlias = ctx.get('previousPage', VIEW_ALIAS.LOBBY_HANGAR)
        return

    def onBackBtnClicked(self):
        self.__close(self.__backPageAlias)

    def onCloseBtnClicked(self):
        self.__close()

    def onContinueBtnClicked(self):
        self.__close()

    def onChangesLinkClicked(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.FRONTLINE_CHANGES))

    def playVideo(self):
        self.__showVideo()

    def _populate(self):
        super(EpicBattlesWelcomeBackView, self)._populate()
        showBackBtn = self.__backPageAlias != VIEW_ALIAS.LOBBY_HANGAR
        title = localize(EPIC_BATTLE.EPICBATTLESWELCOMEBACKVIEW_TITLE)
        self.as_setInitDataS({'titleLabelBig': text_styles.epicTitle(title),
         'titleLabelSmall': text_styles.heroTitle(title),
         'bgSource': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG,
         'tileList': self.__makeTileList(),
         'playVideoBtnLabel': text_styles.concatStylesToSingleLine(icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_PLAYICON, width=14, height=15, vSpace=-2), localize(EPIC_BATTLE.EPICBATTLESWELCOMEBACKVIEW_PLAYVIDEOBTN_LABEL)),
         'showBackBtn': showBackBtn})

    def __makeTileList(self):
        return [ {'iconSource': RES_ICONS.getEpicWelcomeBackImgTilePath(nr),
         'titleLabel': localize(EPIC_BATTLE.getTileLabel(nr)),
         'descriptionLabel': localize(EPIC_BATTLE.getTileDescr(nr)),
         'showDelay': _DEFAULT_TILE_SHOW_DELAY + nr * _TILE_SHOW_DELAY_STEP} for nr in xrange(1, _NR_OF_TILES + 1) ]

    def __close(self, nextView=VIEW_ALIAS.LOBBY_HANGAR):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        version = getCurrentWelcomeScreenVersion()
        stateFlags['lastShownEpicWelcomeScreen'] = version
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
        self.fireEvent(events.DirectLoadViewEvent(SFViewLoadParams(nextView)), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def __showVideo(self):
        url = yield self.__urlMacros.parse(self.__settings.get('url'))
        webBrowser = self.__getCurrentBrowser()
        if not webBrowser or url != webBrowser.url:
            title = localize(EPIC_BATTLE.EPICBATTLESWELCOMEBACKVIEW_VIDEO_TITLE)
            self.__browserID = yield self.browserCtrl.load(url, title, showActionBtn=False, browserID=self.__browserID, browserSize=gc_constants.BROWSER.VIDEO_SIZE, isDefault=False, showCloseBtn=True, handlers=self.__createWebHandlers())

    def __getCurrentBrowser(self):
        return self.browserCtrl.getBrowser(self.__browserID)

    def __createWebHandlers(self):
        return HangarSoundWebApi().getHandlers()
