# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTutorialMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleTutorialMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_populateProgressBarS(self, currentChapter, totalChapters):
        return self.flashObject.as_populateProgressBar(currentChapter, totalChapters) if self._isDAAPIInited() else None

    def as_setTrainingProgressBarS(self, mask):
        return self.flashObject.as_setTrainingProgressBar(mask) if self._isDAAPIInited() else None

    def as_setChapterProgressBarS(self, totalSteps, mask):
        return self.flashObject.as_setChapterProgressBar(totalSteps, mask) if self._isDAAPIInited() else None

    def as_showGreetingS(self, targetID, title, description):
        return self.flashObject.as_showGreeting(targetID, title, description) if self._isDAAPIInited() else None

    def as_setChapterInfoS(self, description):
        return self.flashObject.as_setChapterInfo(description) if self._isDAAPIInited() else None

    def as_showNextTaskS(self, taskID, text, prevDone):
        return self.flashObject.as_showNextTask(taskID, text, prevDone) if self._isDAAPIInited() else None

    def as_showHintS(self, hintID, text, imagePath, imageAltPath):
        return self.flashObject.as_showHint(hintID, text, imagePath, imageAltPath) if self._isDAAPIInited() else None

    def as_hideGreetingS(self, targetID):
        return self.flashObject.as_hideGreeting(targetID) if self._isDAAPIInited() else None
