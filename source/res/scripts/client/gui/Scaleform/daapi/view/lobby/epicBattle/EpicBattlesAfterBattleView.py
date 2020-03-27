# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/EpicBattlesAfterBattleView.py
import SoundGroups
from constants import EPIC_ABILITY_PTS_NAME
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_level_icon import getEpicMetaIconVODict
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import FRONTLINE_LEVEL_TOKEN_BASE, FRONTLINE_PROGRESSION_FINISH_TOKEN
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EpicCurtailingAwardsComposer
from gui.Scaleform.daapi.view.meta.EpicBattlesAfterBattleViewMeta import EpicBattlesAfterBattleViewMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.server_events.bonuses import CreditsBonus, CrystalBonus, ItemsBonus, GoodiesBonus, BasicPremiumDaysBonus, PlusPremiumDaysBonus, EpicAbilityPtsBonus
from gui.shared.formatters import text_styles
from gui.shared.utils import toUpper
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_LEVELUP_TOKEN_TEMPLATE = 'epicmetagame:levelup:%d'

def _AccumulateBonuses(bonuses):

    def __accumulateIntegralBonus(integralBonusType, bonuses):
        return integralBonusType(bonuses[0].getName(), sum([ b.getValue() for b in bonuses ]))

    def accumulateCredits(bonuses):
        return __accumulateIntegralBonus(CreditsBonus, bonuses)

    def accumulateCrystals(bonuses):
        return __accumulateIntegralBonus(CrystalBonus, bonuses)

    def accumulateBasicPremiumDays(bonuses):
        return __accumulateIntegralBonus(BasicPremiumDaysBonus, bonuses)

    def accumulatePlusPremiumDays(bonuses):
        return __accumulateIntegralBonus(PlusPremiumDaysBonus, bonuses)

    def accumulateEpicAbilityPtsBonus(bonuses):
        return __accumulateIntegralBonus(EpicAbilityPtsBonus, bonuses)

    def accumulateItems(bonuses):
        values = dict()
        for b in bonuses:
            for bid, cnt in b.getValue().iteritems():
                values[bid] = values.get(bid, 0) + cnt

        return ItemsBonus(bonuses[0].getName(), values)

    def accumulateGoodies(bonuses):
        values = dict()
        for b in bonuses:
            for bid, value in b.getValue().iteritems():
                if bid in values.iterkeys():
                    cnt = values.get(bid).get('count', 0)
                    values[bid]['count'] = cnt + value.get('count', 0)
                values[bid] = {'count': value.get('count', 0)}

        return GoodiesBonus(bonuses[0].getName(), values)

    typeToAccumulator = {CreditsBonus: accumulateCredits,
     CrystalBonus: accumulateCrystals,
     ItemsBonus: accumulateItems,
     GoodiesBonus: accumulateGoodies,
     BasicPremiumDaysBonus: accumulateBasicPremiumDays,
     PlusPremiumDaysBonus: accumulatePlusPremiumDays,
     EpicAbilityPtsBonus: accumulateEpicAbilityPtsBonus}
    accumulatedBonuses = []
    for bonusType in set((type(b) for b in bonuses)):
        bonusesOfType = [ b for b in bonuses if isinstance(b, bonusType) ]
        if bonusType not in typeToAccumulator.iterkeys():
            accumulatedBonuses.extend(bonusesOfType)
        accumulatedBonuses.append(typeToAccumulator.get(bonusType)(bonusesOfType))

    return accumulatedBonuses


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
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onWindowClose(self):
        self.__close()

    def onProgressBarStartAnim(self):
        if not self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_START)
            self.__isProgressBarAnimating = True

    def onProgressBarCompleteAnim(self):
        if self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_STOP)
            self.__isProgressBarAnimating = False

    def _populate(self):
        super(EpicBattlesAfterBattleView, self)._populate()
        extInfo = self.__ctx['reusableInfo'].personal.avatar.extensionInfo
        epicMetaGame = extInfo['epicMetaGame']
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
        achievedRank = max(extInfo['playerRank'].get('rank', 0), 1)
        rankNameId = R.strings.epic_battle.rank.dyn('rank' + str(achievedRank))
        rankName = toUpper(backport.text(rankNameId())) if rankNameId.exists() else ''
        awardsVO = self._awardsFormatter.getFormattedBonuses(self.__getBonuses(pMetaLevel), size=AWARDS_SIZES.BIG)
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
         'epicMetaLevelIconData': getEpicMetaIconVODict(cycleNumber, pMetaLevel),
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

    def __getBonuses(self, level):
        questsProgressData = self.__ctx['reusableInfo'].personal.getQuestsProgress()
        allQuests = self.__eventsCache.getAllQuests()
        currentLevelQuest = allQuests.get(_LEVELUP_TOKEN_TEMPLATE % level, None)
        if currentLevelQuest and questsProgressData:
            bonuses = sum([ allQuests.get(q).getBonuses() for q in questsProgressData if FRONTLINE_LEVEL_TOKEN_BASE in q or FRONTLINE_PROGRESSION_FINISH_TOKEN in q ], self.__getAbilityPointsRewardBonus(level))
            bonuses = _AccumulateBonuses(bonuses)
        else:
            bonuses = []
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

    def __close(self):
        self.onProgressBarCompleteAnim()
        self.destroy()
