# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_battles_after_battle_view.py
import collections
import SoundGroups
from constants import EPIC_ABILITY_PTS_NAME
from epic_constants import EPIC_SELECT_BONUS_NAME
from gui.Scaleform.daapi.view.lobby.epicBattle.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EpicCurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.EpicBattlesAfterBattleViewMeta import EpicBattlesAfterBattleViewMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicBattleViewAwardPacker
from gui.server_events.bonuses import EpicAbilityPtsBonus
from gui.shared.event_dispatcher import showEpicRewardsSelectionWindow, showFrontlineAwards
from gui.shared.formatters import text_styles
from gui.shared.utils import toUpper
from gui.server_events.bonuses import mergeBonuses
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController, IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
from skeletons.gui.battle_results import IBattleResultsService

class EpicBattlesAfterBattleView(EpicBattlesAfterBattleViewMeta):
    _MAX_VISIBLE_AWARDS = 6
    _BONUS_ORDER_PRIORITY = {'battlePassPoints': 1,
     'abilityPts': 2,
     'crystal': 3,
     'goodies': 4,
     EPIC_SELECT_BONUS_NAME: 5,
     'crewBooks': 6}
    _MIDDLE_PRIORITY = 50
    _awardsFormatter = EpicCurtailingAwardsComposer(_MAX_VISIBLE_AWARDS, getEpicBattleViewAwardPacker())
    __eventsCache = dependency.descriptor(IEventsCache)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __battlePass = dependency.descriptor(IBattlePassController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleResultsService = dependency.descriptor(IBattleResultsService)

    def __init__(self, ctx=None):
        super(EpicBattlesAfterBattleView, self).__init__()
        self.__ctx = ctx
        self.__maxLvlReached = False
        self.__isProgressBarAnimating = False
        self.__isViewWatchedLogStopped = False
        self.__rewardsSelectionWindow = None
        self.__awardsWindow = None
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()
        return

    def onIntroStartsPlaying(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_ACHIEVED_RANK)

    def onRibbonStartsPlaying(self):
        if not self.__maxLvlReached:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED)
        else:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED_MAX)

    def onNextBtnClick(self):
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.NEXT.value, parentScreen=EpicBattleLogKeys.HANGAR.value)
        arenaUniqueID = self.__ctx['levelUpInfo'].get('arenaUniqueID')
        if arenaUniqueID and self.__battleResultsService.areResultsPosted(arenaUniqueID):
            self.__battleResultsService.notifyBattleResultsPosted(arenaUniqueID, True)
        self.destroy()

    def onEscapePress(self):
        self.__logCloseAction()
        self.destroy()

    def onCloseBtnClick(self):
        self.__logCloseAction()
        self.destroy()

    def onRewardsBtnClick(self):
        rewards = []
        currentScreen = EpicBattleLogKeys.AFTER_BATTLE_VIEW.value
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.REWARDS.value, EpicBattleLogKeys.AFTER_BATTLE_VIEW.value)

        def _onAwardsClosed():
            self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, EpicBattleLogKeys.AWARDS_VIEW.value, currentScreen)

        def _onAwardsAnimationEnded():
            if self.__rewardsSelectionWindow:
                self.__rewardsSelectionWindow.destroy()

        def _logRewardSelectionClosed():
            self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, EpicBattleLogKeys.REWARDS_SELECTION_VIEW.value, currentScreen)

        def _onRewardReceived(rs):
            rewards.extend(rs)
            if rewards:
                _logRewardSelectionClosed()
                self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)
                showFrontlineAwards(rewards, _onAwardsClosed, _onAwardsAnimationEnded)

        self.__stopViewWatchedLog()
        self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)
        self.__rewardsSelectionWindow = showEpicRewardsSelectionWindow(onRewardsReceivedCallback=_onRewardReceived, onCloseCallback=_logRewardSelectionClosed, onLoadedCallback=self.destroy, isAutoDestroyWindowsOnReceivedRewards=False)

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
        self.__removeListeners()
        self.__stopViewWatchedLog()

    def _populate(self):
        super(EpicBattlesAfterBattleView, self)._populate()
        self.__addListeners()
        self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)
        levelUpInfo = self.__ctx['levelUpInfo']
        pMetaLevel, pFamePts = levelUpInfo.get('metaLevel', (None, None))
        prevPMetaLevel, prevPFamePts = levelUpInfo.get('prevMetaLevel', (None, None))
        boosterFLXP = levelUpInfo.get('boosterFlXP', 0)
        originalFlXP = levelUpInfo.get('originalFlXP', 0)
        maxMetaLevel = self.__epicController.getMaxPlayerLevel()
        famePtsToProgress = self.__epicController.getLevelProgress()
        season = self.__epicController.getCurrentSeason() or None
        cycleNumber = 0
        if season is not None:
            cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
        famePointsReceived = sum(famePtsToProgress[prevPMetaLevel:pMetaLevel]) + pFamePts - prevPFamePts
        achievedRank = max(levelUpInfo.get('playerRank', 0), 1)
        rankNameId = R.strings.epic_battle.rank.dyn('rank' + str(achievedRank))
        rankName = toUpper(backport.text(rankNameId())) if rankNameId.exists() else ''
        sourceBonuses = self.__getBonuses(prevPMetaLevel, pMetaLevel)
        tokenBonusesGroups = collections.defaultdict(list)
        otherBonuses = []
        for sourceBonus in sourceBonuses:
            if sourceBonus.getName() == EPIC_SELECT_BONUS_NAME:
                for key in sourceBonus.getValue():
                    splitKey = key.rsplit(':', 2)[0]
                    tokenBonusesGroups[splitKey].append(sourceBonus)

            otherBonuses.append(sourceBonus)

        tokenBonuses = []
        for tokenBonusesGroup in tokenBonusesGroups.values():
            tokenBonuses += mergeBonuses(tokenBonusesGroup)

        bonuses = sorted(mergeBonuses(otherBonuses) + tokenBonuses, key=lambda item: self._BONUS_ORDER_PRIORITY.get(item.getName(), self._MIDDLE_PRIORITY))
        tooltipToBonusNameMapping = {}
        awardsVO = self.__markAnimationBonuses(self._awardsFormatter.getFormattedBonuses(bonuses, size=AWARDS_SIZES.BIG))
        for idx, bonus in enumerate(bonuses):
            awardTooltip = awardsVO[idx].get('tooltip')
            if awardTooltip is not None:
                tooltipToBonusNameMapping[str(awardTooltip)] = bonus.getName()

        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.AFTER_BATTLE_VIEW.value, skipAdditionalInfoTooltips=(TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP,), overrideTooltipsId=tooltipToBonusNameMapping)
        fameBarVisible = True
        dailyQuestAvailable = False
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
         'maxLvlReached': self.__maxLvlReached,
         'questPanelVisible': dailyQuestAvailable,
         'isRewardsButtonShown': self.__epicController.hasAnyOfferGiftToken() and self.__hasSelectBonus(bonuses)}
        self.as_setDataS(data)
        return

    def __stopViewWatchedLog(self):
        if not self.__isViewWatchedLogStopped:
            self.__isViewWatchedLogStopped = True
            self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, EpicBattleLogKeys.AFTER_BATTLE_VIEW.value, EpicBattleLogKeys.HANGAR.value)
            self.__uiEpicBattleLogger.reset()

    def __logCloseAction(self):
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLOSE.value, EpicBattleLogKeys.AFTER_BATTLE_VIEW.value, parentScreen=EpicBattleLogKeys.HANGAR.value)

    def __getBonuses(self, prevLevel, level):
        awardsData = []
        allLevelData = self.__epicController.getAllLevelRewards()
        for questLvl, rewardData in allLevelData.iteritems():
            if prevLevel < questLvl <= level:
                rewards = rewardData.getBonuses()
                rewards.extend(self.__getAbilityPointsRewardBonus(questLvl))
                bonuses = self.__epicController.replaceOfferByReward(rewards)
                awardsData.extend(bonuses)

        return awardsData

    @staticmethod
    def __markAnimationBonuses(bonuses):
        for bonus in bonuses:
            if bonus['specialAlias'] == TOOLTIPS_CONSTANTS.EPIC_BATTLE_INSTRUCTION_TOOLTIP:
                bonus['hasAnimation'] = True

        return bonuses

    def __getAbilityPointsRewardBonus(self, level):
        abilityPts = self.__epicController.getAbilityPointsForLevel()
        return [EpicAbilityPtsBonus(name=EPIC_ABILITY_PTS_NAME, value=abilityPts[level - 1])] if abilityPts and abilityPts[level - 1] and level <= len(abilityPts) else []

    def __getProgress(self, curLevel, curFamePoints, prevLevel, prevFamePoints, maxLevel, boostedXP):
        getPointsProgressForLevel = self.__epicController.getPointsProgressForLevel
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

    @staticmethod
    def __hasSelectBonus(bonuses):
        return any((bonus.getName() == EPIC_SELECT_BONUS_NAME for bonus in bonuses))

    def __addListeners(self):
        self.__eventsCache.onSyncCompleted += self.__onServerSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def __removeListeners(self):
        self.__eventsCache.onSyncCompleted -= self.__onServerSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def __onServerSettingsChanged(self, *_):
        if not self.__epicController.isEnabled():
            self.destroy()
