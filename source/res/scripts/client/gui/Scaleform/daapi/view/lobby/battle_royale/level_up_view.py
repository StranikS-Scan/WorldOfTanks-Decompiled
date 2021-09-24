# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/level_up_view.py
import SoundGroups
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EpicCurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.BattleRoyaleLevelUpViewMeta import BattleRoyaleLevelUpViewMeta
from gui.Scaleform.daapi.view.lobby.epicBattle import after_battle_reward_view_helpers
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

def _getTitleString(prevTitle, achievedTitle):
    titleDiff = achievedTitle - prevTitle
    if titleDiff == 1:
        lvlReachedText = backport.text(R.strings.battle_royale.levelUp.title(), level=achievedTitle)
    elif titleDiff > 2:
        lvlReachedText = backport.text(R.strings.battle_royale.levelUp.severalTitles(), firstLevel=prevTitle + 1, lastLevel=achievedTitle)
    else:
        lvlReachedText = backport.text(R.strings.battle_royale.levelUp.twoTitles(), firstLevel=prevTitle + 1, secondLevel=achievedTitle)
    return lvlReachedText


class BattleRoyaleLevelUpView(BattleRoyaleLevelUpViewMeta):
    _MAX_VISIBLE_AWARDS = 8
    _awardsFormatter = EpicCurtailingAwardsComposer(_MAX_VISIBLE_AWARDS, getEpicViewAwardPacker())
    __eventsCache = dependency.descriptor(IEventsCache)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(BattleRoyaleLevelUpView, self).__init__()
        self.__ctx = ctx
        self.__maxLvlReached = False
        self.__isProgressBarAnimating = False

    def onIntroStartsPlaying(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_ACHIEVED_RANK)

    def onRibbonStartsPlaying(self):
        if not self.__maxLvlReached:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED)
        else:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED_MAX)

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onWindowClose(self):
        self.__close()

    def _populate(self):
        super(BattleRoyaleLevelUpView, self)._populate()
        battleRoyaleInfo = self.__ctx['reusableInfo'].personal.getBattleRoyaleInfo()
        title, _ = battleRoyaleInfo.get('accBRTitle', (None, None))
        prevTitle, _ = battleRoyaleInfo.get('prevBRTitle', (None, None))
        maxTitle = self.__battleRoyaleController.getMaxPlayerLevel()
        season = self.__battleRoyaleController.getCurrentSeason() or None
        cycleNumber = 0
        if season is not None:
            cycleNumber = self.__battleRoyaleController.getCurrentOrNextActiveCycleNumber(season)
        awardsVO = self._awardsFormatter.getFormattedBonuses(self.__getBonuses(title), size=AWARDS_SIZES.BIG)
        awardsSmallVO = self._awardsFormatter.getFormattedBonuses(self.__getBonuses(title))
        if prevTitle >= maxTitle or title >= maxTitle:
            self.__maxLvlReached = True
        lvlReachedText = _getTitleString(prevTitle, title)
        data = {'awards': awardsVO,
         'awardsSmall': awardsSmallVO,
         'epicMetaLevelIconData': after_battle_reward_view_helpers.getProgressionIconVODict(cycleNumber, title),
         'levelUpText': lvlReachedText,
         'backgroundImageSrc': backport.image(R.images.gui.maps.icons.battleRoyale.backgrounds.back_congrats()),
         'maxLvlReached': self.__maxLvlReached}
        self.as_setDataS(data)
        return

    def __getBonuses(self, level):
        questsProgressData = self.__ctx['reusableInfo'].progress.getQuestsProgress()
        bonuses = after_battle_reward_view_helpers.getQuestBonuses(questsProgressData, (self.__battleRoyaleController.TOKEN_QUEST_ID,), self.__battleRoyaleController.TOKEN_QUEST_ID + str(level))
        bonuses = mergeBonuses(bonuses)
        bonuses = splitBonuses(bonuses)
        return bonuses

    def __close(self):
        self.destroy()
