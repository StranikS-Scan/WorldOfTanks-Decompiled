# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/battle_level_panel.py
from helpers import int2roman
import WWISE
from gui.Scaleform.daapi.view.meta.BattleLevelPanelMeta import BattleLevelPanelMeta
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleLevelPanel(BattleLevelPanelMeta, IProgressionListener):
    __SOUND_XP_DIFF = 200
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleLevelPanel, self).__init__()
        self.__totalXP = 0
        self.__xp = 0
        self.__xpPrev = 0
        self.__xpPercent = 0
        self.__level = 0
        self.__firstShow = True
        self.__isMaxLvl = False

    def _populate(self):
        super(BattleLevelPanel, self)._populate()
        self.__updateXP()

    def setCurrentXP(self, xp, xpPercent):
        if self.__isMaxLvl:
            return
        if xp != self.__xp:
            self.__xpPrev = self.__xp
            self.__xp = xp
        if self.__firstShow:
            self.__xpPrev = self.__xp
            self.__firstShow = False
        if self.__xp <= 0:
            self.__xpPrev = 0
        self.__xpPercent = xpPercent
        self.__updateXP()

    def setLevel(self, level, _, maxXP):
        self.__totalXP = maxXP
        self.__level = level
        self.__updateLevel()
        self.__updateXP()

    def onMaxLvlAchieved(self):
        self.__isMaxLvl = True
        self.as_setIsMaxLevelS(True)

    def onPlaySound(self, soundType):
        WWISE.WW_eventGlobal(soundType)

    def __updateLevel(self):
        experienceText = '{xp} / {xpTotal}'.format(xp=self.__xp, xpTotal=self.__totalXP)
        self.as_setLevelS(int2roman(self.__level), int2roman(self.__level + 1), experienceText)

    def __updateXP(self):
        if self.__xpPercent != IProgressionListener.MAX_PERCENT_AMOUNT:
            experienceText = ' / {xpTotal}'.format(xpTotal=self.__totalXP)
            expDiff = self.__xp - self.__xpPrev
            progressionCtrl = self.__sessionProvider.dynamic.progression
            playSound = expDiff >= self.__SOUND_XP_DIFF and self.__level < progressionCtrl.maxLevel
            if self.__xp >= self.__totalXP and self.__xp > 0:
                self.as_setExperienceS(self.__totalXP, experienceText, expDiff, IProgressionListener.MAX_PERCENT_AMOUNT, playSound)
            else:
                self.as_setExperienceS(self.__xp, experienceText, expDiff, self.__xpPercent, playSound)
