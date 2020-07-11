# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesPrestigeView.py
import logging
import SoundGroups
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_progression.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prestige_progress import getPrestigeLevelAwardsVOs
from gui.Scaleform.daapi.view.meta.EpicBattlesPrestigeViewMeta import EpicBattlesPrestigeViewMeta
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.gui_items.processors.common import EpicPrestigeTrigger
from gui.shared.utils import decorators
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency, i18n, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
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
        self.__triggerPrestige()

    def _populate(self):
        super(EpicBattlesPrestigeView, self)._populate()
        pPrestigeLevel, _, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        nextPrestigeLevel = pPrestigeLevel + 1
        metaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel
        maxPrestigeLevel = metaLevel.get('maxPrestigeLevel', 0)
        if 0 <= maxPrestigeLevel <= pPrestigeLevel:
            _logger.error('This line of code should never be reached!')
            self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
            return
        awardsVO = getPrestigeLevelAwardsVOs(self.eventsCache.getAllQuests(), nextPrestigeLevel, AWARDS_SIZES.BIG)
        prestigeLvlTxt = i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_PRESTIGELEVEL, level=int2roman(nextPrestigeLevel + 1))
        iconData = getProgressionIconVODict(nextPrestigeLevel, 1)
        data = {'prestigeLevelText': prestigeLvlTxt,
         'prestigeTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_MAINTITLE),
         'removeAbilitiesContainerTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_REMOVEABILITIES_TITLE),
         'resetLevelContainerTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_RESETLEVEL_TITLE),
         'rewardTitleText': i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_CONGRATULATIONS),
         'awards': awardsVO,
         'metaLevelIconPrestige': iconData,
         'epicMetaLevelIconData': iconData,
         'backgroundImageSrc': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG}
        self.as_setDataS(data)

    @decorators.process('updating')
    def __triggerPrestige(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PRESTIGE_RESET)
        result = yield EpicPrestigeTrigger().request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        elif result.success:
            self.as_showSuccessfullPrestigeS()

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __back(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
