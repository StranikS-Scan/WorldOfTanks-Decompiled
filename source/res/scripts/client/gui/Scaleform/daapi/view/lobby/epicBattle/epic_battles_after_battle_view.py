# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_battles_after_battle_view.py
from constants import EPIC_ABILITY_PTS_NAME
from gui.game_control.event_progression_controller import EVENT_PROGRESSION_FINISH_TOKEN
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.event_progression.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.lobby.event_progression import after_battle_reward_view_helpers
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EpicCurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.EpicBattlesAfterBattleViewMeta import EpicBattlesAfterBattleViewMeta
from gui.server_events.awards_formatters import getEpicViewAwardPacker
from gui.server_events.bonuses import EpicAbilityPtsBonus
from gui.shared.formatters import text_styles
from gui.shared.utils import toUpper
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
import SoundGroups

class EpicBattlesAfterBattleView(EpicBattlesAfterBattleViewMeta):
    _MAX_VISIBLE_AWARDS = 6
    _awardsFormatter = EpicCurtailingAwardsComposer(_MAX_VISIBLE_AWARDS, getEpicViewAwardPacker())
    __eventsCache = dependency.descriptor(IEventsCache)
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(EpicBattlesAfterBattleView, self).__init__()
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
        self.destroy()

    def onCloseBtnClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def onProgressBarStartAnim(self):
        if not self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_START)
            self.__isProgressBarAnimating = True

    def onProgressBarCompleteAnim(self):
        if self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_STOP)
            self.__isProgressBarAnimating = False

    def destroy(self):
        self.onProgressBarCompleteAnim()
        super(EpicBattlesAfterBattleView, self).destroy()

    def _populate(self):
        super(EpicBattlesAfterBattleView, self)._populate()
        epicMetaGame = self.__ctx['reusableInfo'].personal.avatar.extensionInfo
        _, pMetaLevel, pFamePts = epicMetaGame.get('metaLevel', (None, None, None))
        _, prevPMetaLevel, prevPFamePts = epicMetaGame.get('prevMetaLevel', (None, None, None))
        boosterFLXP = epicMetaGame.get('boosterFlXP', 0)
        originalFlXP = epicMetaGame.get('originalFlXP', 0)
        maxMetaLevel = self.__epicMetaGameCtrl.getMaxPlayerLevel()
        famePtsToProgress = self.__epicMetaGameCtrl.getLevelProgress()
        season = self.__epicMetaGameCtrl.getCurrentSeason() or None
        cycleNumber = 0
        if season is not None:
            cycleNumber = self.__epicMetaGameCtrl.getCurrentOrNextActiveCycleNumber(season)
        famePointsReceived = sum(famePtsToProgress[prevPMetaLevel:pMetaLevel]) + pFamePts - prevPFamePts
        achievedRank = max(epicMetaGame.get('playerRank', 0), 1)
        rankNameId = R.strings.epic_battle.rank.dyn('rank' + str(achievedRank))
        rankName = toUpper(backport.text(rankNameId())) if rankNameId.exists() else ''
        awardsVO = self._awardsFormatter.getFormattedBonuses(self.__getBonuses(prevPMetaLevel, pMetaLevel))
        fameBarVisible = True
        if prevPMetaLevel >= maxMetaLevel or pMetaLevel >= maxMetaLevel:
            boosterFLXP = famePointsReceived - originalFlXP if famePointsReceived > originalFlXP else 0
            if prevPMetaLevel >= maxMetaLevel:
                fameBarVisible = False
            else:
                self.__maxLvlReached = True
        lvlReachedText = toUpper(backport.text(R.strings.epic_battle.epic_battles_after_battle.Level_Up_Title(), level=pMetaLevel))
        data = {'awards': awardsVO,
         'progress': self.__getProgress(pMetaLevel, pFamePts, prevPMetaLevel, prevPFamePts, maxMetaLevel, boosterFLXP),
         'barText': '+' + str(min(originalFlXP, famePointsReceived)),
         'barBoostText': '+' + str(boosterFLXP),
         'epicMetaLevelIconData': getProgressionIconVODict(cycleNumber, pMetaLevel),
         'rank': achievedRank,
         'rankText': text_styles.epicTitle(rankName),
         'rankSubText': text_styles.promoTitle(backport.text(R.strings.epic_battle.epic_battles_after_battle.Achieved_Rank())),
         'levelUpText': text_styles.heroTitle(lvlReachedText),
         'backgroundImageSrc': backport.image(R.images.gui.maps.icons.epicBattles.backgrounds.back_congrats()),
         'fameBarVisible': fameBarVisible,
         'maxLevel': maxMetaLevel,
         'maxLvlReached': self.__maxLvlReached}
        self.as_setDataS(data)
        return

    def __getBonuses(self, prevLevel, currentLevel):
        questsProgressData = self.__ctx['reusableInfo'].personal.getQuestsProgress()
        bonuses = after_battle_reward_view_helpers.getQuestBonuses(questsProgressData, (EVENT_PROGRESSION_FINISH_TOKEN, self.__epicMetaGameCtrl.TOKEN_QUEST_ID), self.__epicMetaGameCtrl.TOKEN_QUEST_ID + str(currentLevel))
        for level in range(prevLevel, currentLevel + 1):
            bonuses.extend([self.__getAbilityPointsRewardBonus(level)])

        bonuses = after_battle_reward_view_helpers.formatBonuses(bonuses)
        return bonuses

    def __getAbilityPointsRewardBonus(self, level):
        abilityPts = self.__lobbyCtx.getServerSettings().epicMetaGame.metaLevel['abilityPointsForLevel'] or []
        return [EpicAbilityPtsBonus(name=EPIC_ABILITY_PTS_NAME, value=abilityPts[level - 1])] if level and level <= len(abilityPts) else []

    def __getProgress(self, curLevel, curFamePoints, prevLevel, prevFamePoints, maxLevel, boostedXP):
        getPointsProgressForLevel = self.__epicMetaGameCtrl.getPointsProgressForLevel
        originalXP = curFamePoints - boostedXP
        pLevel = prevLevel + float(prevFamePoints) / float(getPointsProgressForLevel(prevLevel)) if prevLevel != maxLevel else maxLevel
        cLevel = curLevel + float(originalXP) / float(getPointsProgressForLevel(curLevel)) if curLevel != maxLevel else maxLevel
        if boostedXP:
            if curLevel == maxLevel:
                cLevel = maxLevel - float(boostedXP) / float(getPointsProgressForLevel(curLevel - 1))
            cBoostedLevel = curLevel + float(curFamePoints) / float(getPointsProgressForLevel(curLevel)) if curLevel != maxLevel else maxLevel
        else:
            cBoostedLevel = cLevel
        return (pLevel, cLevel, cBoostedLevel)
