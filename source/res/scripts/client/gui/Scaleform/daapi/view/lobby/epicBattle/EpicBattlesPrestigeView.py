# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesPrestigeView.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict, EPIC_META_LEVEL_ICON_SIZE
from gui.Scaleform.daapi.view.meta.EpicBattlesPrestigeViewMeta import EpicBattlesPrestigeViewMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency, i18n, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_PRESTIGE_TOKEN_TEMPLATE = 'epicmetagame:prestige:%d'
_PRESTIGE_TOKEN_INFINITE = 'epicmetagame:prestige:infinite'

class EpicBattlesPrestigeView(LobbySubView, EpicBattlesPrestigeViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyCtx = dependency.instance(ILobbyContext)

    def onEscapePress(self):
        self.__back()

    def onCloseBtnClick(self):
        self.__close()

    def onBackBtnClick(self):
        self.__back()

    def onResetBtnClick(self):
        pass

    def _populate(self):
        super(EpicBattlesPrestigeView, self)._populate()
        pPrestigeLevel, _, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        nextPrestigeLevel = pPrestigeLevel + 1
        metaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel
        maxPrestigeLevel = metaLevel.get('maxPrestigeLevel', 0)
        if maxPrestigeLevel >= 0 and pPrestigeLevel >= maxPrestigeLevel:
            LOG_ERROR('This line of code should never be reached!')
            self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
            return
        awardsVO = ''
        prestigeLvlTxt = i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_PRESTIGELEVEL, level=int2roman(nextPrestigeLevel + 1))
        data = {'prestigeLevelText': prestigeLvlTxt,
         'prestigeTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_MAINTITLE),
         'removeAbilitiesContainerTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_REMOVEABILITIES_TITLE),
         'resetLevelContainerTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_RESETLEVEL_TITLE),
         'rewardTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_CONGRATULATIONS),
         'awards': awardsVO,
         'metaLevelIconPrestige': getEpicMetaIconVODict(nextPrestigeLevel, 1, EPIC_META_LEVEL_ICON_SIZE.BIG),
         'epicMetaLevelIconData': getEpicMetaIconVODict(nextPrestigeLevel, 1),
         'backgroundImageSrc': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BLUR_BG}
        self.as_setDataS(data)

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __back(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
