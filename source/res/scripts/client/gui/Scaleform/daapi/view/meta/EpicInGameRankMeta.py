# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicInGameRankMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicInGameRankMeta(BaseDAAPIComponent):

    def as_setRankTextsS(self, rankTexts):
        return self.flashObject.as_setRankTexts(rankTexts) if self._isDAAPIInited() else None

    def as_setRankExperienceLevelsS(self, levelCaps):
        return self.flashObject.as_setRankExperienceLevels(levelCaps) if self._isDAAPIInited() else None

    def as_initRankS(self, progress):
        return self.flashObject.as_initRank(progress) if self._isDAAPIInited() else None

    def as_updatePlayerExperienceS(self, progress):
        return self.flashObject.as_updatePlayerExperience(progress) if self._isDAAPIInited() else None
