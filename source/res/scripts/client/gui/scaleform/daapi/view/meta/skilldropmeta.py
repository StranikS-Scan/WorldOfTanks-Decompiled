# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SkillDropMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SkillDropMeta(AbstractWindowView):

    def calcDropSkillsParams(self, tmanCompDescr, xpReuseFraction):
        self._printOverrideError('calcDropSkillsParams')

    def dropSkills(self, dropSkillCostIdx):
        self._printOverrideError('dropSkills')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setGoldS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setGold(value)

    def as_setCreditsS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCredits(value)
