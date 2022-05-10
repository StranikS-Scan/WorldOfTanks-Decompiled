# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/battle_level_panel.py
import BigWorld
import BattleReplay
from helpers import int2roman
import WWISE
from gui.Scaleform.daapi.view.meta.BattleLevelPanelMeta import BattleLevelPanelMeta
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener

class BattleLevelPanel(BattleLevelPanelMeta, IProgressionListener):
    __SOUND_XP_DIFF = 1
    __XP_UPDATE_TIME_DIFF = 1.0

    def __init__(self):
        super(BattleLevelPanel, self).__init__()
        self.__firstShow = True
        self.__maxLevelAchieved = False
        self.__isInitialized = False
        self.__lastXPUpdateTime = 0.0

    def updateData(self, arenaLevelData):
        animationState = arenaLevelData.xpIsChanged
        if arenaLevelData.observedVehicleIsChanged:
            animationState = False
            self.__maxLevelAchieved = False
            self.as_resetS()
        if self.__maxLevelAchieved:
            return
        if BattleReplay.g_replayCtrl.isPlaying:
            animationState = False
        self.__update(arenaLevelData, animationState)
        self.__firstShow = False

    def __update(self, arenaLevel, animationState):
        if BigWorld.time() - self.__lastXPUpdateTime < self.__XP_UPDATE_TIME_DIFF:
            animationState = False
        self.__lastXPUpdateTime = BigWorld.time()
        if not self.__isInitialized:
            self.as_setAnimationS(False)
            self.__isInitialized = True
        else:
            self.as_setAnimationS(animationState)
            if not animationState and not arenaLevel.isMaxLvlAchieved:
                expText = '{currentXP} / {targetXP}'.format(currentXP=arenaLevel.xp, targetXP=arenaLevel.targetXP)
                self.as_setLevelS(int2roman(arenaLevel.level), int2roman(arenaLevel.level + 1), expText)
        if arenaLevel.xp == 0 and arenaLevel.level == 1:
            expText = ' / {targetXP}'.format(targetXP=arenaLevel.targetXP)
            self.as_setLevelS(int2roman(arenaLevel.level), int2roman(arenaLevel.level + 1), expText)
            self.as_setExperienceS(0, expText, 0, 0, False)
            return
        if arenaLevel.levelIsChanged:
            expText = ' / {targetXP}'.format(targetXP=arenaLevel.baseXP)
            percent = IProgressionListener.MAX_PERCENT_AMOUNT
            xp = arenaLevel.baseXP
        else:
            expText = ' / {targetXP}'.format(targetXP=arenaLevel.targetXP)
            percent = arenaLevel.percent
            xp = arenaLevel.xp
        playSound = arenaLevel.diff >= self.__SOUND_XP_DIFF and not self.__firstShow
        self.as_setExperienceS(xp, expText, arenaLevel.diff, percent, playSound)
        if arenaLevel.isMaxLvlAchieved:
            self.as_setMaxLevelReachedS(int2roman(arenaLevel.level))
            self.__maxLevelAchieved = True
            return
        if arenaLevel.levelIsChanged or self.__firstShow:
            expText = '{baseXP} / {targetXP}'.format(baseXP=arenaLevel.baseXP, targetXP=arenaLevel.targetXP)
            self.as_setLevelS(int2roman(arenaLevel.level), int2roman(arenaLevel.level + 1), expText)
            expText = ' / {targetXP}'.format(targetXP=arenaLevel.targetXP)
            self.as_setExperienceS(arenaLevel.xp, expText, arenaLevel.diffAfterLevel, arenaLevel.percent, playSound)

    def onPlaySound(self, soundType):
        WWISE.WW_eventGlobal(soundType)
