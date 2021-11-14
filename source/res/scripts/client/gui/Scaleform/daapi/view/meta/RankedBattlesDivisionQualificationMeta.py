# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesDivisionQualificationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RankedBattlesDivisionQualificationMeta(BaseDAAPIComponent):

    def as_setQualificationEfficiencyDataS(self, data):
        return self.flashObject.as_setQualificationEfficiencyData(data) if self._isDAAPIInited() else None

    def as_setQualificationStepsDataS(self, data):
        return self.flashObject.as_setQualificationStepsData(data) if self._isDAAPIInited() else None

    def as_setQualificationDataS(self, imageSrcSmall, imageSrcBig, isFirstEnter):
        return self.flashObject.as_setQualificationData(imageSrcSmall, imageSrcBig, isFirstEnter) if self._isDAAPIInited() else None

    def as_setQualificationProgressS(self, progressTextSmall, progressTextBig, isCompleted, descr):
        return self.flashObject.as_setQualificationProgress(progressTextSmall, progressTextBig, isCompleted, descr) if self._isDAAPIInited() else None
