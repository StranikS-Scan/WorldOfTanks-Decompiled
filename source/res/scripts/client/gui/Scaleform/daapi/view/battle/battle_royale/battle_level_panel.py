# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/battle_level_panel.py
from helpers import int2roman
import WWISE
from gui.Scaleform.daapi.view.meta.BattleLevelPanelMeta import BattleLevelPanelMeta
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleLevelPanel(BattleLevelPanelMeta, IProgressionListener):
    __SOUND_XP_DIFF = 1
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleLevelPanel, self).__init__()
        self.__targetXP = 0
        self.__baseXP = 0
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
        self.__xpPercent = xpPercent
        self.__updateXP()
        self.__firstShow = False

    def setLevel(self, level, minXP, maxXP):
        if self.__isMaxLvl:
            return
        self.__level = level
        self.__baseXP = minXP
        self.__targetXP = maxXP
        if self.__targetXP > self.__baseXP:
            self.__updateLevel()
            self.__updateXP()

    def onMaxLvlAchieved(self):
        if self.__isMaxLvl:
            return
        self.as_setMaxLevelReachedS(int2roman(self.__level))
        self.__isMaxLvl = True

    def onPlaySound(self, soundType):
        WWISE.WW_eventGlobal(soundType)

    def __updateLevel(self):
        experienceText = '{baseXP} / {targetXP}'.format(baseXP=self.__baseXP, targetXP=self.__targetXP)
        self.as_setLevelS(int2roman(self.__level), int2roman(self.__level + 1), experienceText)

    def __updateXP(self):
        if self.__xpPercent != IProgressionListener.MAX_PERCENT_AMOUNT:
            expDiff = self.__xp - max(self.__xpPrev, self.__baseXP)
            if expDiff <= 0:
                return
            experienceText = ' / {targetXP}'.format(targetXP=self.__targetXP)
            playSound = expDiff >= self.__SOUND_XP_DIFF and not self.__firstShow
            if self.__xp >= self.__targetXP > 0:
                self.as_setExperienceS(self.__targetXP, experienceText, expDiff, IProgressionListener.MAX_PERCENT_AMOUNT, playSound)
            else:
                self.as_setExperienceS(self.__xp, experienceText, expDiff, self.__xpPercent, playSound)
