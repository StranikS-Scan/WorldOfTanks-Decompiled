# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesSkillViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class EpicBattlesSkillViewMeta(WrapperViewMeta):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onBackBtnClick(self):
        self._printOverrideError('onBackBtnClick')

    def onSelectSkillBtnClick(self, skillID):
        self._printOverrideError('onSelectSkillBtnClick')

    def onSkillUpgrade(self, skillID):
        self._printOverrideError('onSkillUpgrade')

    def onSkillOverLevel(self, skillID, level):
        self._printOverrideError('onSkillOverLevel')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_updateDataS(self, data):
        return self.flashObject.as_updateData(data) if self._isDAAPIInited() else None

    def as_setSelectedSkillS(self, skillID):
        return self.flashObject.as_setSelectedSkill(skillID) if self._isDAAPIInited() else None

    def as_setSkillDataBlockS(self, data):
        return self.flashObject.as_setSkillDataBlock(data) if self._isDAAPIInited() else None
