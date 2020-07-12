# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleLevelPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleLevelPanelMeta(BaseDAAPIComponent):

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setLevelS(self, currentLevel, nextLevel, experience):
        return self.flashObject.as_setLevel(currentLevel, nextLevel, experience) if self._isDAAPIInited() else None

    def as_setExperienceS(self, currentExperience, targetExperience, expDiff, percent, playSound):
        return self.flashObject.as_setExperience(currentExperience, targetExperience, expDiff, percent, playSound) if self._isDAAPIInited() else None

    def as_setMaxLevelReachedS(self, levelReached):
        return self.flashObject.as_setMaxLevelReached(levelReached) if self._isDAAPIInited() else None
