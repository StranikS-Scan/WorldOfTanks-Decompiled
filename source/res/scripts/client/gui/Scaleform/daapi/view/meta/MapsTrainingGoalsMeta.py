# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MapsTrainingGoalsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MapsTrainingGoalsMeta(BaseDAAPIComponent):

    def as_updateS(self, data):
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None

    def as_destroyGoalS(self, vehClass):
        return self.flashObject.as_destroyGoal(vehClass) if self._isDAAPIInited() else None

    def as_showHintS(self, hintType, description, time=None):
        return self.flashObject.as_showHint(hintType, description, time) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None

    def as_setVisibleS(self, isVisible):
        return self.flashObject.as_setVisible(isVisible) if self._isDAAPIInited() else None
