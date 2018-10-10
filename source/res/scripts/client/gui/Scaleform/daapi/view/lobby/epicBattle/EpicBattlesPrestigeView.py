# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesPrestigeView.py
from collections import namedtuple
import SoundGroups
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EpicBattlesPrestigeViewMeta import EpicBattlesPrestigeViewMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from helpers import i18n
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from debug_utils import LOG_ERROR
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
import BigWorld
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict, EPIC_META_LEVEL_ICON_SIZE
from helpers import int2roman
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
_PRESTIGE_TOKEN_TEMPLATE = 'epicmetagame:prestige:%d'
EpicBattlesPrestigeViewVO = namedtuple('EpicBattlesPrestigeViewVO', ('prestigeLevelText', 'prestigeTitleText', 'removeAbilitiesContainerTitleText', 'resetLevelContainerTitleText', 'rewardTitleText', 'backgroundImageSrc', 'metaLevelIconPrestige', 'epicMetaLevelIconData', 'awards'))

class EpicBattlesPrestigeView(LobbySubView, EpicBattlesPrestigeViewMeta):
    epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyCtx = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(EpicBattlesPrestigeView, self).__init__()

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onBackBtnClick(self):
        self.__back()

    def onResetBtnClick(self):
        BigWorld.player().epicMetaGame.triggerEpicMetaGamePrestige()
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PRESTIGE_RESET)

    def _populate(self):
        super(EpicBattlesPrestigeView, self)._populate()
        pPrestigeLevel, _, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        if pPrestigeLevel >= self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxPrestigeLevel', 0):
            LOG_ERROR('This line of code should never be reached!')
            self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
            return
        else:
            allQuests = self.eventsCache.getAllQuests()
            currentPrestigeQuest = allQuests.get(_PRESTIGE_TOKEN_TEMPLATE % (pPrestigeLevel + 1), None)
            if currentPrestigeQuest:
                bonuses = currentPrestigeQuest.getBonuses()
                awardsVO = sum([ bonus.getEpicAwardVOs(withDescription=False) for bonus in bonuses ], [])
            else:
                awardsVO = []
            prestigeLvlTxt = i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_PRESTIGELEVEL, level=int2roman(pPrestigeLevel + 1))
            data = EpicBattlesPrestigeViewVO(prestigeLevelText=prestigeLvlTxt, prestigeTitleText=i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_MAINTITLE), removeAbilitiesContainerTitleText=i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_REMOVEABILITIES_TITLE), resetLevelContainerTitleText=i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_RESETLEVEL_TITLE), rewardTitleText=i18n.makeString(EPIC_BATTLE.EPICBATTLESPRESTIGEVIEW_CONGRATULATIONS), awards=awardsVO, metaLevelIconPrestige=getEpicMetaIconVODict(pPrestigeLevel + 1, 1, EPIC_META_LEVEL_ICON_SIZE.BIG), epicMetaLevelIconData=getEpicMetaIconVODict(pPrestigeLevel + 1, 1), backgroundImageSrc=RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BLUR_BG)
            self.as_setDataS(data._asdict())
            return

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __back(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_INFO_ALIAS), EVENT_BUS_SCOPE.LOBBY)
