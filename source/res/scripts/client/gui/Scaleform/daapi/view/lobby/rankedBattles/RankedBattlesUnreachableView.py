# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesUnreachableView.py
import SoundGroups
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesUnreachableViewMeta import RankedBattlesUnreachableViewMeta
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control import gc_constants
from gui.game_control.links import URLMarcos
from gui.ranked_battles.constants import SOUND
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.formatters.icons import makeImageTag
from helpers import dependency, int2roman
from helpers.i18n import makeString
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController, IBrowserController

class RankedBattlesUnreachableView(LobbySubView, RankedBattlesUnreachableViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)
    settingsCore = dependency.descriptor(ISettingsCore)
    rankedController = dependency.descriptor(IRankedBattlesController)
    __background_alpha__ = 0.5

    def __init__(self, ctx=None):
        super(RankedBattlesUnreachableView, self).__init__()
        self.__currentVersionBrowserID = None
        self.__settings = GUI_SETTINGS.rankedBattles.get('unreachableVideo', {})
        self.__urlMacros = URLMarcos()
        self.__levelsRangeStr = ''
        return

    def onEscapePress(self):
        self._exitHangar()

    def onCloseBtnClick(self):
        self._exitHangar()

    def onLeaderboardBtnClick(self):
        self.rankedController.openWebLeaguePage()
        self.__close()

    def onVideoBtnClick(self):
        if self.__settings.get('isEnabled', False):
            self.__showVideo()

    def _populate(self):
        super(RankedBattlesUnreachableView, self)._populate()
        self.as_setDataS(self.__getData())

    def __getData(self):
        bottomItems = self.__getBottomItems()
        centerTextStr = RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_UNREACHABLETEXT
        centerTextStr = text_styles.vehicleStatusCriticalText(centerTextStr)
        bottomTextStr = text_styles.highTitle(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_BOTTOMTEXT)
        return {'bottomRules': bottomItems,
         'headerText': text_styles.superPromoTitle(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_HEADERTEXT),
         'centerText': self.__formatUnreachableLevels(centerTextStr),
         'bottomText': self.__formatUnreachableLevels(bottomTextStr),
         'closeBtnLabel': RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_CLOSEBTNLABEL,
         'closeBtnTooltip': '',
         'videoBtnLabel': RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_VIDEOBTNLABEL,
         'videoBtnTooltip': '',
         'videoBtnIcon': makeImageTag(RES_ICONS.MAPS_ICONS_BUTTONS_BUTTON_PLAY2, 32, 32, -11, 0),
         'leaderboardBtnLabel': RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_LEADERBOARDBTNLABEL,
         'leaderboardBtnTooltip': '',
         'leaderboardBtnIcon': makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ICON_BUTTON_LIST, 28, 28, -8, 0),
         'bgImage': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_BG_PIC_RANK_LOCK,
         'centerImg': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_RANKED_BATTLE_LOCKED_SM,
         'centerImgBig': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_RANKED_BATTLE_LOCKED_BIG}

    def __getBottomItems(self):
        result = list()
        result.append({'tooltip': '',
         'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_ICON_PREM,
         'description': text_styles.main(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_BOTTOM_PREMIUM)})
        result.append({'tooltip': '',
         'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_ICON_RANKS_TASK_200X100,
         'description': text_styles.main(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_BOTTOM_MISSIONS)})
        result.append({'tooltip': '',
         'image': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_XLESSVIEW_ICON_RESERVES,
         'description': text_styles.main(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_BOTTOM_RESERVES)})
        return result

    def _exitHangar(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__close()

    def __close(self):
        self.__currentVersionBrowserID = None
        SoundGroups.g_instance.playSound2D(SOUND.ANIMATION_WINDOW_CLOSED)
        self.destroy()
        return

    @process
    def __showVideo(self):
        url = yield self.__urlMacros.parse(self.__settings.get('url'))
        webBrowser = self.__getCurrentBrowser()
        if not webBrowser or url != webBrowser.url:
            title = makeString(RANKED_BATTLES.RANKEDBATTLESUNREACHABLEVIEW_VIDEOBROWSER_TITLE)
            self.__currentVersionBrowserID = yield self.browserCtrl.load(url, title, showActionBtn=False, browserID=self.__currentVersionBrowserID, browserSize=gc_constants.BROWSER.VIDEO_SIZE, isDefault=False, showCloseBtn=True)

    def __getCurrentBrowser(self):
        return self.browserCtrl.getBrowser(self.__currentVersionBrowserID)

    def __formatUnreachableLevels(self, message):
        if self.__levelsRangeStr == '':
            minLevel, maxLevel = self.rankedController.getSuitableVehicleLevels()
            if minLevel == maxLevel:
                self.__levelsRangeStr = int2roman(minLevel)
            else:
                self.__levelsRangeStr = '{0}-{1}'.format(int2roman(minLevel), int2roman(maxLevel))
        return message.format(levels=self.__levelsRangeStr)
